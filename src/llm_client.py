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