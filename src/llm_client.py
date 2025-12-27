import json
from typing import Dict, Any

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from .config import config


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
        Process user input and update the task tree using the LLM.
        
        Args:
            current_task_tree: The current task tree as a dictionary
            user_input: The user's new task request
            
        Returns:
            The updated task tree as a dictionary
        """
        task_tree_json = json.dumps(current_task_tree, ensure_ascii=False, indent=2)
        
        response = self.chain.invoke({
            "current_task_tree": task_tree_json,
            "user_input": user_input
        })
        
        # Extract JSON from response
        content = response.content
        json_start = content.index("{")
        json_end = content.rindex("}") + 1
        response_json = content[json_start:json_end]
        
        return json.loads(response_json)