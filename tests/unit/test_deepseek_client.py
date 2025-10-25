import unittest
from unittest.mock import patch, MagicMock
import os
from src.services.deepseek_client import DeepSeekClient, ChatMessage, ChatCompletionResponse


class TestDeepSeekClient(unittest.TestCase):
    """DeepSeek客户端单元测试"""
    
    def setUp(self):
        """测试前准备"""
        # 设置测试环境变量
        os.environ['DEEPSEEK_API_KEY'] = 'test-api-key'
        os.environ['DEEPSEEK_BASE_URL'] = 'https://api.test.deepseek.com'
        
        # 创建DeepSeek客户端实例
        self.client = DeepSeekClient()
    
    def test_client_initialization(self):
        """测试客户端初始化"""
        self.assertEqual(self.client.api_key, 'test-api-key')
        self.assertEqual(self.client.base_url, 'https://api.test.deepseek.com')
        self.assertEqual(self.client.model, 'deepseek-chat')
    
    def test_client_initialization_with_default_url(self):
        """测试使用默认URL初始化客户端"""
        # 移除自定义URL环境变量
        if 'DEEPSEEK_BASE_URL' in os.environ:
            del os.environ['DEEPSEEK_BASE_URL']
        
        client = DeepSeekClient()
        self.assertEqual(client.base_url, 'https://api.deepseek.com')
        
        # 恢复环境变量
        os.environ['DEEPSEEK_BASE_URL'] = 'https://api.test.deepseek.com'
    
    def test_chat_message_creation(self):
        """测试聊天消息创建"""
        message = ChatMessage(role="user", content="Hello, world!")
        
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello, world!")
    
    def test_chat_completion_response_creation(self):
        """测试聊天完成响应创建"""
        response = ChatCompletionResponse(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="deepseek-chat",
            choices=[{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop"
            }],
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        )
        
        self.assertEqual(response.id, "test-id")
        self.assertEqual(response.object, "chat.completion")
        self.assertEqual(response.created, 1234567890)
        self.assertEqual(response.model, "deepseek-chat")
        self.assertEqual(len(response.choices), 1)
        self.assertEqual(response.choices[0]["message"]["content"], "Hello!")
        self.assertEqual(response.usage["total_tokens"], 15)
    
    @patch('requests.post')
    def test_chat_completion_success(self, mock_post):
        """测试聊天完成成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_post.return_value = mock_response
        
        # 调用聊天完成方法
        messages = [ChatMessage(role="user", content="Hello")]
        response = self.client.chat_completion(messages)
        
        # 验证结果
        self.assertIsNotNone(response)
        self.assertEqual(response.id, "test-id")
        self.assertEqual(response.choices[0]["message"]["content"], "Hello!")
        
        # 验证API调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], 'https://api.test.deepseek.com/v1/chat/completions')
        self.assertEqual(call_args[1]['headers']['Authorization'], 'Bearer test-api-key')
        self.assertEqual(call_args[1]['json']['model'], 'deepseek-chat')
        self.assertEqual(len(call_args[1]['json']['messages']), 1)
        self.assertEqual(call_args[1]['json']['messages'][0]['role'], 'user')
        self.assertEqual(call_args[1]['json']['messages'][0]['content'], 'Hello')
    
    @patch('requests.post')
    def test_chat_completion_api_error(self, mock_post):
        """测试聊天完成API错误"""
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        mock_post.return_value = mock_response
        
        # 调用聊天完成方法
        messages = [ChatMessage(role="user", content="Hello")]
        response = self.client.chat_completion(messages)
        
        # 验证结果
        self.assertIsNone(response)
    
    @patch('requests.post')
    def test_simple_chat_success(self, mock_post):
        """测试简单聊天成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello! How can I help you?"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
        }
        mock_post.return_value = mock_response
        
        # 调用简单聊天方法
        response = self.client.simple_chat("Hello, how are you?")
        
        # 验证结果
        self.assertEqual(response, "Hello! How can I help you?")
        
        # 验证API调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(len(call_args[1]['json']['messages']), 2)  # 系统消息 + 用户消息
        self.assertEqual(call_args[1]['json']['messages'][1]['content'], "Hello, how are you?")
    
    @patch('requests.post')
    def test_analyze_task_success(self, mock_post):
        """测试任务分析成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": '{"complexity": "medium", "estimated_hours": 4, "required_skills": ["Python", "数据分析"]}'},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35}
        }
        mock_post.return_value = mock_response
        
        # 调用任务分析方法
        response = self.client.analyze_task("开发一个数据分析工具")
        
        # 验证结果
        self.assertIsInstance(response, dict)
        self.assertEqual(response['complexity'], 'medium')
        self.assertEqual(response['estimated_hours'], 4)
        self.assertEqual(response['required_skills'], ["Python", "数据分析"])
    
    @patch('requests.post')
    def test_analyze_task_invalid_json(self, mock_post):
        """测试任务分析返回无效JSON"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "这不是有效的JSON"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
        }
        mock_post.return_value = mock_response
        
        # 调用任务分析方法
        response = self.client.analyze_task("开发一个数据分析工具")
        
        # 验证结果
        self.assertIsInstance(response, dict)
        self.assertIn('error', response)
    
    @patch('requests.post')
    def test_generate_task_suggestions_success(self, mock_post):
        """测试生成任务建议成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": '[{"title": "需求分析", "description": "分析项目需求", "priority": "high", "estimated_hours": 2}, {"title": "设计系统架构", "description": "设计系统整体架构", "priority": "high", "estimated_hours": 4}]'},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 30, "completion_tokens": 50, "total_tokens": 80}
        }
        mock_post.return_value = mock_response
        
        # 调用生成任务建议方法
        response = self.client.generate_task_suggestions("开发一个任务管理系统")
        
        # 验证结果
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 2)
        self.assertEqual(response[0]['title'], '需求分析')
        self.assertEqual(response[0]['priority'], 'high')
        self.assertEqual(response[0]['estimated_hours'], 2)
        self.assertEqual(response[1]['title'], '设计系统架构')
        self.assertEqual(response[1]['priority'], 'high')
        self.assertEqual(response[1]['estimated_hours'], 4)
    
    @patch('requests.post')
    def test_optimize_task_order_success(self, mock_post):
        """测试优化任务顺序成功"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": '[{"id": "task-2", "title": "任务2", "priority": "high"}, {"id": "task-1", "title": "任务1", "priority": "medium"}, {"id": "task-3", "title": "任务3", "priority": "low"}]'},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 40, "completion_tokens": 60, "total_tokens": 100}
        }
        mock_post.return_value = mock_response
        
        # 准备测试任务
        tasks = [
            {"id": "task-1", "title": "任务1", "priority": "medium", "description": "中等优先级任务"},
            {"id": "task-2", "title": "任务2", "priority": "high", "description": "高优先级任务"},
            {"id": "task-3", "title": "任务3", "priority": "low", "description": "低优先级任务"}
        ]
        
        # 调用优化任务顺序方法
        response = self.client.optimize_task_order(tasks)
        
        # 验证结果
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 3)
        self.assertEqual(response[0]['id'], 'task-2')  # 高优先级任务排在第一位
        self.assertEqual(response[1]['id'], 'task-1')
        self.assertEqual(response[2]['id'], 'task-3')
    
    @patch('requests.post')
    def test_is_available_true(self, mock_post):
        """测试API可用性检查 - 可用"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        mock_post.return_value = mock_response
        
        # 调用API可用性检查方法
        response = self.client.is_available()
        
        # 验证结果
        self.assertTrue(response)
    
    @patch('requests.post')
    def test_is_available_false(self, mock_post):
        """测试API可用性检查 - 不可用"""
        # 模拟API错误
        mock_post.side_effect = Exception("Connection error")
        
        # 调用API可用性检查方法
        response = self.client.is_available()
        
        # 验证结果
        self.assertFalse(response)


if __name__ == "__main__":
    unittest.main()