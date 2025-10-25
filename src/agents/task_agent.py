"""
智能体核心逻辑模块
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import re
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain.memory import ConversationBufferMemory

from ..models import Task, TaskManager, TaskStatus, TaskPriority
from ..utils.config import config
from ..services import DeepSeekClient
from .llm_interface import get_langchain_llm


class TaskAgentState:
    """任务智能体状态"""
    
    def __init__(self):
        self.user_input: str = ""
        self.intent: str = ""
        self.task_data: Dict[str, Any] = {}
        self.task_id: Optional[str] = None
        self.response: str = ""
        self.conversation_history: List[Dict[str, str]] = []
        self.task_manager: TaskManager = TaskManager(config.tasks_file)
        self.memory = ConversationBufferMemory()


class TaskAgent:
    """任务智能体"""
    
    def __init__(self):
        self.llm = get_langchain_llm()
        self.deepseek_client = DeepSeekClient()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建智能体工作流图"""
        workflow = StateGraph(TaskAgentState)
        
        # 添加节点
        workflow.add_node("understand_intent", self._understand_intent)
        workflow.add_node("extract_task_info", self._extract_task_info)
        workflow.add_node("execute_task_operation", self._execute_task_operation)
        workflow.add_node("generate_response", self._generate_response)
        
        # 设置入口点
        workflow.set_entry_point("understand_intent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "understand_intent",
            self._route_after_intent,
            {
                "create_task": "extract_task_info",
                "update_task": "extract_task_info",
                "list_tasks": "execute_task_operation",
                "show_task": "execute_task_operation",
                "delete_task": "execute_task_operation",
                "analyze_task": "execute_task_operation",
                "suggest_tasks": "execute_task_operation",
                "optimize_tasks": "execute_task_operation",
                "unknown": "generate_response"
            }
        )
        
        # 添加普通边
        workflow.add_edge("extract_task_info", "execute_task_operation")
        workflow.add_edge("execute_task_operation", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def _understand_intent(self, state: TaskAgentState) -> TaskAgentState:
        """理解用户意图"""
        prompt = f"""
        你是一个任务管理智能助手，负责理解用户的意图并分类。
        
        用户的输入是: "{state.user_input}"
        
        请判断用户的意图，并返回以下分类之一:
        - create_task: 创建新任务
        - update_task: 更新已有任务
        - list_tasks: 列出任务
        - show_task: 显示任务详情
        - delete_task: 删除任务
        - analyze_task: 分析任务
        - suggest_tasks: 生成任务建议
        - optimize_tasks: 优化任务顺序
        - unknown: 无法识别的意图
        
        只返回分类名称，不要添加其他内容。
        """
        
        # 优先使用DeepSeek API
        try:
            if self.deepseek_client.is_available():
                response = self.deepseek_client.simple_chat(prompt, max_tokens=50)
                state.intent = response.strip().lower()
            else:
                response = self.llm.invoke(prompt)
                state.intent = response.strip().lower()
        except Exception:
            # 如果DeepSeek API失败，回退到原始LLM
            response = self.llm.invoke(prompt)
            state.intent = response.strip().lower()
        
        # 添加到对话历史
        state.conversation_history.append({"role": "user", "content": state.user_input})
        state.conversation_history.append({"role": "assistant", "content": f"意图识别: {state.intent}"})
        
        return state
    
    def _extract_task_info(self, state: TaskAgentState) -> TaskAgentState:
        """提取任务信息"""
        if state.intent == "create_task":
            prompt = f"""
            你是一个任务管理助手，负责从用户输入中提取任务信息。
            
            用户的输入是: "{state.user_input}"
            
            请提取以下信息，并以JSON格式返回:
            - title: 任务标题
            - description: 任务描述
            - priority: 任务优先级 (low/medium/high)
            - due_date: 截止日期 (YYYY-MM-DD格式，如果有的话)
            - tags: 标签列表
            
            如果某个信息无法从输入中提取，请使用null或空列表。
            只返回JSON，不要添加其他内容。
            """
        elif state.intent == "update_task":
            prompt = f"""
            你是一个任务管理助手，负责从用户输入中提取任务更新信息。
            
            用户的输入是: "{state.user_input}"
            
            请提取以下信息，并以JSON格式返回:
            - task_id: 要更新的任务ID (如果提到了的话)
            - title: 新的任务标题 (如果要更新的话)
            - description: 新的任务描述 (如果要更新的话)
            - status: 新的任务状态 (pending/in_progress/completed/cancelled)
            - priority: 新的任务优先级 (low/medium/high)
            - due_date: 新的截止日期 (YYYY-MM-DD格式)
            
            如果某个信息无法从输入中提取，请使用null。
            只返回JSON，不要添加其他内容。
            """
        else:
            return state
        
        # 优先使用DeepSeek API
        try:
            if self.deepseek_client.is_available():
                response = self.deepseek_client.simple_chat(prompt, max_tokens=500)
            else:
                response = self.llm.invoke(prompt)
        except Exception:
            # 如果DeepSeek API失败，回退到原始LLM
            response = self.llm.invoke(prompt)
        
        try:
            state.task_data = json.loads(response.strip())
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试提取JSON部分
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                state.task_data = json.loads(json_match.group(1))
            else:
                state.task_data = {}
        
        return state
    
    def _execute_task_operation(self, state: TaskAgentState) -> TaskAgentState:
        """执行任务操作"""
        task_manager = state.task_manager
        
        if state.intent == "create_task":
            task = self._create_task_from_data(state.task_data)
            state.task_id = task_manager.add_task(task)
            state.response = f"已创建任务: {task.title} (ID: {task.id})"
            
        elif state.intent == "update_task":
            task_id = state.task_data.get("task_id")
            if not task_id:
                # 尝试从用户输入中提取任务ID
                task_id_match = re.search(r'task-(\w+)', state.user_input)
                if task_id_match:
                    task_id = f"task-{task_id_match.group(1)}"
            
            if task_id:
                task = task_manager.get_task(task_id)
                if task:
                    # 更新任务
                    update_data = {k: v for k, v in state.task_data.items() 
                                 if k != "task_id" and v is not None}
                    
                    # 处理状态和优先级的枚举值
                    if "status" in update_data:
                        try:
                            update_data["status"] = TaskStatus(update_data["status"])
                        except ValueError:
                            pass
                    
                    if "priority" in update_data:
                        try:
                            update_data["priority"] = TaskPriority(update_data["priority"])
                        except ValueError:
                            pass
                    
                    # 处理日期
                    if "due_date" in update_data and update_data["due_date"]:
                        try:
                            update_data["due_date"] = datetime.strptime(update_data["due_date"], "%Y-%m-%d")
                        except ValueError:
                            pass
                    
                    for key, value in update_data.items():
                        setattr(task, key, value)
                    
                    task.updated_at = datetime.now()
                    task_manager.save_tasks()
                    state.response = f"已更新任务: {task.title} (ID: {task.id})"
                else:
                    state.response = f"未找到ID为 {task_id} 的任务"
            else:
                state.response = "无法确定要更新的任务ID"
                
        elif state.intent == "list_tasks":
            tasks = task_manager.get_all_tasks()
            if tasks:
                task_list = "\n".join([f"- {task.title} (ID: {task.id}, 状态: {task.status.value})" 
                                     for task in tasks])
                state.response = f"任务列表:\n{task_list}"
            else:
                state.response = "当前没有任务"
                
        elif state.intent == "show_task":
            task_id = state.task_data.get("task_id")
            if not task_id:
                # 尝试从用户输入中提取任务ID
                task_id_match = re.search(r'task-(\w+)', state.user_input)
                if task_id_match:
                    task_id = f"task-{task_id_match.group(1)}"
            
            if task_id:
                task = task_manager.get_task(task_id)
                if task:
                    state.response = self._format_task_details(task)
                else:
                    state.response = f"未找到ID为 {task_id} 的任务"
            else:
                state.response = "无法确定要查看的任务ID"
                
        elif state.intent == "delete_task":
            task_id = state.task_data.get("task_id")
            if not task_id:
                # 尝试从用户输入中提取任务ID
                task_id_match = re.search(r'task-(\w+)', state.user_input)
                if task_id_match:
                    task_id = f"task-{task_id_match.group(1)}"
            
            if task_id:
                if task_manager.delete_task(task_id):
                    state.response = f"已删除任务 (ID: {task_id})"
                else:
                    state.response = f"未找到ID为 {task_id} 的任务"
            else:
                state.response = "无法确定要删除的任务ID"
        
        elif state.intent == "analyze_task":
            # 分析任务
            task_id = state.task_data.get("task_id")
            if not task_id:
                # 尝试从用户输入中提取任务ID
                task_id_match = re.search(r'task-(\w+)', state.user_input)
                if task_id_match:
                    task_id = f"task-{task_id_match.group(1)}"
            
            if task_id:
                task = task_manager.get_task(task_id)
                if task:
                    # 使用DeepSeek API分析任务
                    try:
                        if self.deepseek_client.is_available():
                            analysis = self.deepseek_client.analyze_task(task.description)
                            analysis_text = "\n".join([f"- {k}: {v}" for k, v in analysis.items()])
                            state.response = f"任务分析结果:\n{analysis_text}"
                        else:
                            state.response = f"任务详情:\n{self._format_task_details(task)}"
                    except Exception:
                        state.response = f"任务详情:\n{self._format_task_details(task)}"
                else:
                    state.response = f"未找到ID为 {task_id} 的任务"
            else:
                # 如果没有指定任务ID，分析用户输入的任务描述
                try:
                    if self.deepseek_client.is_available():
                        analysis = self.deepseek_client.analyze_task(state.user_input)
                        analysis_text = "\n".join([f"- {k}: {v}" for k, v in analysis.items()])
                        state.response = f"任务分析结果:\n{analysis_text}"
                    else:
                        state.response = "无法分析任务，请提供任务ID或更详细的任务描述"
                except Exception:
                    state.response = "无法分析任务，请提供任务ID或更详细的任务描述"
        
        elif state.intent == "suggest_tasks":
            # 生成任务建议
            try:
                if self.deepseek_client.is_available():
                    suggestions = self.deepseek_client.generate_task_suggestions(state.user_input)
                    if suggestions:
                        suggestion_text = "\n".join([
                            f"{i+1}. {s.get('title', '')} - {s.get('description', '')} (优先级: {s.get('priority', '中')}, 预估工时: {s.get('estimated_hours', 1)}小时)"
                            for i, s in enumerate(suggestions)
                        ])
                        state.response = f"任务建议:\n{suggestion_text}"
                    else:
                        state.response = "无法生成任务建议，请提供更详细的项目描述"
                else:
                    state.response = "任务建议功能当前不可用"
            except Exception:
                state.response = "生成任务建议时出错"
        
        elif state.intent == "optimize_tasks":
            # 优化任务顺序
            tasks = task_manager.get_all_tasks()
            if tasks:
                # 转换为字典格式
                task_dicts = [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "priority": task.priority.value,
                        "status": task.status.value,
                        "due_date": task.due_date.isoformat() if task.due_date else None
                    }
                    for task in tasks
                ]
                
                try:
                    if self.deepseek_client.is_available():
                        optimized_tasks = self.deepseek_client.optimize_task_order(task_dicts)
                        optimized_text = "\n".join([
                            f"{i+1}. {task.get('title', '')} (ID: {task.get('id', '')}, 优先级: {task.get('priority', '中')})"
                            for i, task in enumerate(optimized_tasks)
                        ])
                        state.response = f"优化后的任务顺序:\n{optimized_text}"
                    else:
                        # 按优先级排序
                        sorted_tasks = sorted(tasks, key=lambda t: (
                            t.priority.value, 
                            t.due_date.isoformat() if t.due_date else "9999-12-31"
                        ))
                        sorted_text = "\n".join([
                            f"{i+1}. {task.title} (ID: {task.id}, 优先级: {task.priority.value})"
                            for i, task in enumerate(sorted_tasks)
                        ])
                        state.response = f"按优先级排序的任务列表:\n{sorted_text}"
                except Exception:
                    # 按优先级排序
                    sorted_tasks = sorted(tasks, key=lambda t: (
                        t.priority.value, 
                        t.due_date.isoformat() if t.due_date else "9999-12-31"
                    ))
                    sorted_text = "\n".join([
                        f"{i+1}. {task.title} (ID: {task.id}, 优先级: {task.priority.value})"
                        for i, task in enumerate(sorted_tasks)
                    ])
                    state.response = f"按优先级排序的任务列表:\n{sorted_text}"
            else:
                state.response = "当前没有任务可以优化"
        
        return state
    
    def _generate_response(self, state: TaskAgentState) -> TaskAgentState:
        """生成响应"""
        if not state.response:
            state.response = "抱歉，我无法理解您的请求。请尝试重新表述。"
        
        # 添加到对话历史
        state.conversation_history.append({"role": "assistant", "content": state.response})
        
        return state
    
    def _route_after_intent(self, state: TaskAgentState) -> str:
        """根据意图决定下一步"""
        return state.intent
    
    def _create_task_from_data(self, data: Dict[str, Any]) -> Task:
        """从数据创建任务"""
        title = data.get("title", "新任务")
        description = data.get("description", "")
        
        # 处理优先级
        priority_str = data.get("priority", "medium")
        try:
            priority = TaskPriority(priority_str)
        except ValueError:
            priority = TaskPriority.MEDIUM
        
        # 处理截止日期
        due_date = None
        if data.get("due_date"):
            try:
                due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")
            except ValueError:
                pass
        
        # 处理标签
        tags = data.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        
        return Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags
        )
    
    def _format_task_details(self, task: Task) -> str:
        """格式化任务详情"""
        details = [
            f"任务ID: {task.id}",
            f"标题: {task.title}",
            f"描述: {task.description}",
            f"状态: {task.status.value}",
            f"优先级: {task.priority.value}",
            f"创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"更新时间: {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if task.due_date:
            details.append(f"截止日期: {task.due_date.strftime('%Y-%m-%d')}")
        
        if task.completed_at:
            details.append(f"完成时间: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if task.tags:
            details.append(f"标签: {', '.join(task.tags)}")
        
        if task.estimated_hours:
            details.append(f"预估工时: {task.estimated_hours}小时")
        
        if task.actual_hours:
            details.append(f"实际工时: {task.actual_hours}小时")
        
        if task.subtasks:
            details.append(f"子任务: {', '.join(task.subtasks)}")
        
        return "\n".join(details)
    
    def process(self, user_input: str) -> str:
        """处理用户输入"""
        state = TaskAgentState()
        state.user_input = user_input
        
        # 执行工作流
        result = self.graph.invoke(state)
        
        return result.response