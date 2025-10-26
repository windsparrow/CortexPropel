"""
LLM客户端模块
支持多种LLM提供商的配置和调用
"""

import os
import configparser
from typing import Optional, Dict, Any
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


def load_config(config_file: str = "config.ini") -> Dict[str, Any]:
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf-8')
    
    llm_config = dict(config['llm'])
    task_config = dict(config['task'])
    
    return {
        'llm': llm_config,
        'task': task_config
    }


def create_llm_client(config: Dict[str, Any]) -> BaseChatModel:
    """创建LLM客户端"""
    llm_config = config.get('llm', {})
    
    provider = llm_config.get('provider', 'deepseek')
    api_key = llm_config.get('api_key', os.getenv('LLM_API_KEY'))
    base_url = llm_config.get('base_url', 'https://api.deepseek.com/v1')
    model = llm_config.get('model', 'deepseek-chat')
    
    if not api_key or api_key == 'your_api_key_here':
        raise ValueError("请配置API密钥，可以在config.ini文件中设置或设置环境变量LLM_API_KEY")
    
    if provider in ['deepseek', 'openai', 'doubao']:
        return ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.1,
            max_tokens=2000
        )
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")


def get_llm_client(config_file: str = "config.ini") -> BaseChatModel:
    """获取LLM客户端实例"""
    config = load_config(config_file)
    return create_llm_client(config)