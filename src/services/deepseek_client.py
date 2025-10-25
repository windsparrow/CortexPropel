"""
DeepSeek API客户端模块
提供与DeepSeek API的交互功能
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from src.utils.config import config

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """聊天消息数据类"""
    role: str  # system, user, assistant
    content: str


@dataclass
class ChatCompletionResponse:
    """聊天完成响应数据类"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: API密钥，如果为None则从配置中获取
            base_url: API基础URL，如果为None则从配置中获取
        """
        self.api_key = api_key or config.deepseek_api_key
        self.base_url = base_url or config.deepseek_base_url
        
        if not self.api_key:
            logger.warning("DeepSeek API密钥未配置，某些功能可能无法使用")
        
        # 默认模型参数
        self.default_model = config.llm_model
        self.default_temperature = config.llm_temperature
        self.default_max_tokens = config.llm_max_tokens
        
        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def chat_completion(
        self,
        messages: List[Union[ChatMessage, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletionResponse, Any]:
        """
        聊天完成接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            stream: 是否流式返回
            **kwargs: 其他参数
            
        Returns:
            聊天完成响应
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未配置")
        
        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                formatted_messages.append(msg)
        
        # 构建请求数据
        data = {
            "model": model or self.default_model,
            "messages": formatted_messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.default_max_tokens,
            "stream": stream,
            **kwargs
        }
        
        # 发送请求
        url = f"{self.base_url}/chat/completions"
        
        try:
            if stream:
                return self._stream_request(url, data)
            else:
                response = self.session.post(url, json=data)
                response.raise_for_status()
                response_data = response.json()
                
                return ChatCompletionResponse(
                    id=response_data.get("id", ""),
                    object=response_data.get("object", ""),
                    created=response_data.get("created", 0),
                    model=response_data.get("model", ""),
                    choices=response_data.get("choices", []),
                    usage=response_data.get("usage", {})
                )
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek API请求失败: {e}")
            raise
    
    def _stream_request(self, url: str, data: Dict[str, Any]):
        """处理流式请求"""
        response = self.session.post(url, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        yield data
                    except json.JSONDecodeError:
                        continue
    
    def simple_chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简单聊天接口
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            **kwargs: 其他参数
            
        Returns:
            模型回复文本
        """
        messages = []
        
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        
        messages.append(ChatMessage(role="user", content=prompt))
        
        response = self.chat_completion(messages, **kwargs)
        
        if response.choices and len(response.choices) > 0:
            return response.choices[0]["message"]["content"]
        
        return ""
    
    def analyze_task(self, task_description: str) -> Dict[str, Any]:
        """
        分析任务描述
        
        Args:
            task_description: 任务描述
            
        Returns:
            分析结果
        """
        system_prompt = """
        你是一个任务分析助手。请分析用户提供的任务描述，提取以下信息：
        1. 任务标题（简洁概括）
        2. 任务类型（如：开发、设计、学习、研究等）
        3. 任务优先级（高、中、低）
        4. 预估工作量（小时）
        5. 截止日期（如果有）
        6. 任务标签（关键词）
        7. 任务依赖（如果有）
        8. 任务分解（子任务列表）
        
        请以JSON格式返回分析结果。
        """
        
        try:
            response = self.simple_chat(task_description, system_prompt=system_prompt)
            # 尝试解析JSON
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"任务分析失败: {e}")
            return {
                "title": task_description[:50] + "..." if len(task_description) > 50 else task_description,
                "type": "其他",
                "priority": "中",
                "estimated_hours": 1,
                "due_date": None,
                "tags": [],
                "dependencies": [],
                "subtasks": []
            }
    
    def generate_task_suggestions(self, project_description: str) -> List[Dict[str, Any]]:
        """
        基于项目描述生成任务建议
        
        Args:
            project_description: 项目描述
            
        Returns:
            任务建议列表
        """
        system_prompt = """
        你是一个项目管理助手。请基于用户提供的项目描述，生成5-10个相关任务建议。
        每个任务应包含：
        1. 任务标题
        2. 任务描述
        3. 任务类型
        4. 优先级
        5. 预估工作量（小时）
        
        请以JSON数组格式返回任务建议。
        """
        
        try:
            response = self.simple_chat(project_description, system_prompt=system_prompt)
            # 尝试解析JSON
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"任务建议生成失败: {e}")
            return []
    
    def optimize_task_order(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        优化任务执行顺序
        
        Args:
            tasks: 任务列表
            
        Returns:
            优化后的任务列表
        """
        system_prompt = """
        你是一个任务优化助手。请基于提供的任务列表，优化任务执行顺序。
        考虑因素：
        1. 任务依赖关系
        2. 优先级
        3. 工作量
        4. 截止日期
        
        请以JSON数组格式返回优化后的任务顺序，保持原有任务结构，但调整顺序。
        """
        
        try:
            response = self.simple_chat(json.dumps(tasks), system_prompt=system_prompt)
            # 尝试解析JSON
            return json.loads(response)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"任务顺序优化失败: {e}")
            return tasks
    
    def is_available(self) -> bool:
        """检查API是否可用"""
        if not self.api_key:
            return False
        
        try:
            # 发送一个简单的请求测试API是否可用
            response = self.simple_chat("Hello", max_tokens=5)
            return True
        except Exception:
            return False


# 全局DeepSeek客户端实例
deepseek_client = DeepSeekClient()