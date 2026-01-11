import json
import logging
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# Handle imports for both package and standalone execution
try:
    from .config import config
except ImportError:
    # Standalone execution
    from config import config

# Configure logger
logger = logging.getLogger(__name__)


class LLMClient:
    """Client for processing tasks using LLM."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=config.MODEL_NAME,
            openai_api_key=config.MODEL_API_KEY,
            openai_api_base=config.MODEL_BASE_URL,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
        
        self.prompt = PromptTemplate(
            template=config.TASK_PROMPT_TEMPLATE,
            input_variables=["current_task_tree", "user_input"]
        )
        
        self.chain = self.prompt | self.llm
    
    def process_task_input(self, current_task_tree: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """
        Process user input and return operation instructions from LLM.
        
        Args:
            current_task_tree: The current task tree as a dictionary
            user_input: The user's task request
            
        Returns:
            Dictionary containing:
            - operations: List of operations (add/update/delete)
            - message: Description of what was done
        """
        task_tree_json = json.dumps(current_task_tree, ensure_ascii=False, indent=2)
        
        logger.info(f"[LLM请求] 用户输入: {user_input}")
        
        response = self.chain.invoke({
            "current_task_tree": task_tree_json,
            "user_input": user_input
        })
        
        # Extract JSON from response
        content = response.content
        logger.info(f"[LLM响应] {content}")
        
        try:
            json_start = content.index("{")
            json_end = content.rindex("}") + 1
            response_json = content[json_start:json_end]
            result = json.loads(response_json)
            
            # Validate response format
            if "operations" not in result:
                logger.warning("LLM response missing 'operations' field, wrapping as empty operations")
                result = {"operations": [], "message": result.get("message", "无法解析操作")}
            
            # Log operations summary
            ops = result.get("operations", [])
            logger.info(f"[操作摘要] 共 {len(ops)} 个操作: {[op.get('operation') for op in ops]}")
            
            return result
            
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"[解析失败] {e}")
            return {"operations": [], "message": f"解析LLM响应失败: {str(e)}"}
    
    def generate_analysis(self, tasks_data: list, query_request: str, query_type: str = "list") -> str:
        """
        Generate analysis report for queried tasks.
        
        Args:
            tasks_data: List of task dictionaries to analyze
            query_request: What the user wants to know
            query_type: Type of analysis (list/analyze/summary)
            
        Returns:
            Markdown formatted analysis report
        """
        tasks_json = json.dumps(tasks_data, ensure_ascii=False, indent=2)
        
        analysis_prompt = f"""
        你是一个数据分析助手。请根据以下任务/记录数据，生成分析报告。
        
        数据:
        {tasks_json}
        
        用户请求: {query_request}
        分析类型: {query_type}
        
        要求:
        1. 使用中文回复
        2. 输出格式为 Markdown
        3. 根据分析类型生成相应内容:
           - list: 生成清晰的列表，按时间排序
           - analyze: 分析数据趋势、变化规律
           - summary: 生成汇总报告，包括统计信息
        4. 如果数据包含数值（如体重、金额），尝试分析变化趋势
        5. 如果有时间信息，按时间顺序整理
        6. 保持简洁，重点突出
        
        直接输出 Markdown 内容，不要包含额外说明。
        """
        
        logger.info(f"[分析请求] 类型: {query_type}, 数据条数: {len(tasks_data)}")
        
        try:
            response = self.llm.invoke(analysis_prompt)
            report = response.content.strip()
            logger.info(f"[分析完成] 报告长度: {len(report)} 字符")
            return report
        except Exception as e:
            logger.error(f"[分析失败] {e}")
            return f"## 分析失败\n\n生成报告时出错: {str(e)}"