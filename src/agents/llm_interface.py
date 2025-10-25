"""
LLM接口模块
提供与不同LLM提供商的统一接口
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import json
import requests
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field

from ..utils.config import config


class BaseLLM(ABC):
    """LLM基类"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        pass


class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM实现"""
    
    def __init__(self):
        self.api_key = config.deepseek_api_key
        self.base_url = config.deepseek_base_url
        self.model = config.deepseek_model
        
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话生成"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000)
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]


class LangChainDeepSeekLLM(LLM):
    """LangChain兼容的DeepSeek LLM实现"""
    
    api_key: str = Field(...)
    base_url: str = Field(default="https://api.deepseek.com/v1")
    model: str = Field(default="deepseek-chat")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.api_key:
            self.api_key = config.deepseek_api_key
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """调用LLM生成文本"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens)
        }
        
        if stop:
            data["stop"] = stop
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API错误: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        return "deepseek"


def get_llm() -> BaseLLM:
    """获取LLM实例"""
    if config.llm_provider == "deepseek":
        return DeepSeekLLM()
    else:
        raise ValueError(f"不支持的LLM提供商: {config.llm_provider}")


def get_langchain_llm() -> LLM:
    """获取LangChain兼容的LLM实例"""
    if config.llm_provider == "deepseek":
        return LangChainDeepSeekLLM()
    else:
        raise ValueError(f"不支持的LLM提供商: {config.llm_provider}")