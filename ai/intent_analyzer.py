"""
LLM意图理解模块
使用LangGraph构建智能体来理解用户的自然语言意图
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import TaskStatus, TaskPriority, TaskManager


class UserIntent(str, Enum):
    """用户意图枚举"""
    CREATE_TASK = "create_task"      # 创建任务
    UPDATE_TASK = "update_task"      # 更新任务
    LIST_TASKS = "list_tasks"        # 列出任务
    SEARCH_TASKS = "search_tasks"    # 搜索任务
    UNKNOWN = "unknown"              # 未知意图


class IntentAnalysis(BaseModel):
    """意图分析结果"""
    intent: UserIntent = Field(description="用户意图")
    confidence: float = Field(description="置信度")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="提取的参数")
    explanation: str = Field(description="意图解释")


class TaskIntentExtractor:
    """任务意图提取器"""
    
    def __init__(self, llm):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=IntentAnalysis)
        
        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个智能任务管理助手，能够准确理解用户的自然语言意图。
            
            请分析用户的输入，识别以下意图类型：
            - create_task: 创建新任务（如"我要完成..."、"计划做..."、"需要建立..."）
            - update_task: 更新任务状态（如"我已经完成了..."、"正在做..."、"暂停..."）
            - list_tasks: 列出任务（如"显示所有任务"、"查看任务列表"、"有什么任务"）
            - search_tasks: 搜索任务（如"查找关于...的任务"、"搜索..."）
            
            对于create_task意图，提取：
            - title: 任务标题
            - description: 任务描述
            - priority: 优先级（高/中/低/紧急）
            - due_date: 截止日期（如果有）
            
            对于update_task意图，提取：
            - task_reference: 任务相关的关键词
            - new_status: 新状态（pending/in_progress/completed/cancelled/blocked）
            - progress_description: 进展描述
            
            对于list_tasks意图，提取：
            - filter_status: 状态过滤（可选）
            - filter_priority: 优先级过滤（可选）
            
            对于search_tasks意图，提取：
            - keyword: 搜索关键词
            
            请以JSON格式返回分析结果，确保包含以下字段：
            intent: 识别的意图类型
            confidence: 置信度（0.0-1.0）
            parameters: 提取的参数对象
            explanation: 对识别意图的简要解释"""),
            ("human", "用户输入: {user_input}")
        ])
        
        # 创建处理链
        self.chain = (
            self.prompt 
            | self.llm 
            | self.parser
        )
    
    def analyze_intent(self, user_input: str) -> IntentAnalysis:
        """分析用户意图"""
        try:
            result = self.chain.invoke({"user_input": user_input})
            return IntentAnalysis(**result)
        except Exception as e:
            # 如果解析失败，返回未知意图
            return IntentAnalysis(
                intent=UserIntent.UNKNOWN,
                confidence=0.0,
                parameters={},
                explanation=f"意图分析失败: {str(e)}"
            )


class TaskAgent:
    """任务管理智能体"""
    
    def __init__(self, task_manager: TaskManager, llm):
        self.task_manager = task_manager
        self.intent_extractor = TaskIntentExtractor(llm)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建LangGraph图"""
        
        # 定义状态
        class AgentState(BaseModel):
            user_input: str = ""
            intent_analysis: Optional[IntentAnalysis] = None
            result: Optional[Dict[str, Any]] = None
            error: Optional[str] = None
        
        # 定义节点函数
        def analyze_intent(state: AgentState) -> AgentState:
            """分析用户意图"""
            try:
                intent_analysis = self.intent_extractor.analyze_intent(state.user_input)
                return AgentState(
                    user_input=state.user_input,
                    intent_analysis=intent_analysis,
                    result=state.result,
                    error=state.error
                )
            except Exception as e:
                return AgentState(
                    user_input=state.user_input,
                    intent_analysis=state.intent_analysis,
                    result=state.result,
                    error=str(e)
                )
        
        def execute_action(state: AgentState) -> AgentState:
            """执行相应动作"""
            if not state.intent_analysis:
                return AgentState(
                    user_input=state.user_input,
                    intent_analysis=state.intent_analysis,
                    result={"error": "没有意图分析结果"},
                    error=state.error
                )
            
            try:
                intent = state.intent_analysis.intent
                params = state.intent_analysis.parameters
                
                if intent == UserIntent.CREATE_TASK:
                    result = self._handle_create_task(params)
                elif intent == UserIntent.UPDATE_TASK:
                    result = self._handle_update_task(params)
                elif intent == UserIntent.LIST_TASKS:
                    result = self._handle_list_tasks(params)
                elif intent == UserIntent.SEARCH_TASKS:
                    result = self._handle_search_tasks(params)
                else:
                    result = {"error": "无法识别的意图", "suggestion": "请尝试说得更具体一些"}
                
                return AgentState(
                    user_input=state.user_input,
                    intent_analysis=state.intent_analysis,
                    result=result,
                    error=state.error
                )
            except Exception as e:
                return AgentState(
                    user_input=state.user_input,
                    intent_analysis=state.intent_analysis,
                    result=state.result,
                    error=str(e)
                )
        
        # 构建图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("analyze_intent", analyze_intent)
        workflow.add_node("execute_action", execute_action)
        
        # 添加边
        workflow.add_edge("analyze_intent", "execute_action")
        workflow.add_edge("execute_action", END)
        
        # 设置入口点
        workflow.set_entry_point("analyze_intent")
        
        return workflow.compile()
    
    def _handle_create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理创建任务"""
        title = params.get("title", "未命名任务")
        description = params.get("description", "")
        
        # 解析优先级
        priority_map = {
            "高": TaskPriority.HIGH,
            "中": TaskPriority.MEDIUM,
            "低": TaskPriority.LOW,
            "紧急": TaskPriority.URGENT
        }
        priority = priority_map.get(params.get("priority", "中"), TaskPriority.MEDIUM)
        
        # 解析截止日期
        due_date = None
        if "due_date" in params:
            try:
                due_date = datetime.fromisoformat(params["due_date"])
            except:
                pass
        
        task = self.task_manager.create_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        
        return {
            "action": "create_task",
            "task": task.model_dump(mode='json'),
            "message": f"成功创建任务: {task.title}"
        }
    
    def _handle_update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理更新任务"""
        task_reference = params.get("task_reference", "")
        new_status_str = params.get("new_status", "")
        progress_description = params.get("progress_description", "")
        
        # 搜索相关任务
        candidate_tasks = self.task_manager.search_tasks(task_reference)
        
        if not candidate_tasks:
            return {
                "action": "update_task",
                "error": f"未找到与'{task_reference}'相关的任务",
                "suggestion": "请提供更具体的任务描述"
            }
        
        # 如果有多个候选任务，选择最相关的一个
        target_task = candidate_tasks[0]
        
        # 状态映射
        status_map = {
            "pending": TaskStatus.PENDING,
            "in_progress": TaskStatus.IN_PROGRESS,
            "completed": TaskStatus.COMPLETED,
            "cancelled": TaskStatus.CANCELLED,
            "blocked": TaskStatus.BLOCKED
        }
        
        updates = {}
        if new_status_str in status_map:
            updates["status"] = status_map[new_status_str]
        
        if progress_description:
            updates["description"] = f"{target_task.description}\n\n进展: {progress_description}"
        
        updated_task = self.task_manager.update_task(target_task.id, **updates)
        
        if updated_task:
            return {
                "action": "update_task",
                "task": updated_task.model_dump(mode='json'),
                "message": f"成功更新任务: {updated_task.title}"
            }
        else:
            return {
                "action": "update_task",
                "error": "任务更新失败"
            }
    
    def _handle_list_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理列出任务"""
        filter_status = params.get("filter_status")
        filter_priority = params.get("filter_priority")
        
        if filter_status:
            status_map = {
                "pending": TaskStatus.PENDING,
                "in_progress": TaskStatus.IN_PROGRESS,
                "completed": TaskStatus.COMPLETED,
                "cancelled": TaskStatus.CANCELLED,
                "blocked": TaskStatus.BLOCKED
            }
            if filter_status in status_map:
                tasks = self.task_manager.get_tasks_by_status(status_map[filter_status])
            else:
                tasks = self.task_manager.get_all_tasks()
        else:
            tasks = self.task_manager.get_all_tasks()
        
        return {
            "action": "list_tasks",
            "tasks": [task.model_dump(mode='json') for task in tasks],
            "count": len(tasks),
            "message": f"共找到 {len(tasks)} 个任务"
        }
    
    def _handle_search_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理搜索任务"""
        keyword = params.get("keyword", "")
        
        if not keyword:
            return {
                "action": "search_tasks",
                "error": "未提供搜索关键词"
            }
        
        tasks = self.task_manager.search_tasks(keyword)
        
        return {
            "action": "search_tasks",
            "tasks": [task.model_dump(mode='json') for task in tasks],
            "count": len(tasks),
            "keyword": keyword,
            "message": f"搜索'{keyword}'找到 {len(tasks)} 个任务"
        }
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """处理用户输入"""
        try:
            # 直接调用图处理
            initial_state = {
                "user_input": user_input,
                "intent_analysis": None,
                "result": None,
                "error": None
            }
            
            result = self.graph.invoke(initial_state)
            
            if result.get("error"):
                return {
                    "error": result["error"],
                    "suggestion": "请尝试重新表述您的问题"
                }
            
            return result.get("result", {})
            
        except Exception as e:
            return {
                "error": f"处理失败: {str(e)}",
                "suggestion": "请检查输入并重试"
            }