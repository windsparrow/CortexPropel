import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from datetime import datetime, timedelta
from src.models.task import Task, TaskStatus, TaskPriority
from src.services.task_service import TaskService
from src.agents.task_agent import TaskAgent


class TestTaskAgent(unittest.TestCase):
    """任务智能体单元测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        # 初始化任务服务和智能体
        self.task_service = TaskService(self.temp_file.name)
        self.task_agent = TaskAgent(self.task_service)
        
        # 创建测试任务
        self.task_id = "test-task-123"
        self.title = "测试任务"
        self.description = "这是一个测试任务"
        self.due_date = datetime.now() + timedelta(days=7)
        
        # 创建测试任务
        self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date,
            task_id=self.task_id
        )
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        os.unlink(self.temp_file.name)
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        self.assertIsNotNone(self.task_agent.task_service)
        self.assertIsNotNone(self.task_agent.llm)
        self.assertIsNotNone(self.task_agent.deepseek_client)
        self.assertIsNotNone(self.task_agent.graph)
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_create_task_intent(self, mock_understand_intent):
        """测试处理创建任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "create_task"
        
        # 模拟任务信息提取
        with patch.object(self.task_agent, '_extract_task_info') as mock_extract:
            mock_extract.return_value = {
                "title": "新任务",
                "description": "这是一个新任务",
                "priority": "high"
            }
            
            # 处理用户输入
            response = self.task_agent.process("创建一个高优先级的任务")
            
            # 验证响应
            self.assertIn("创建成功", response)
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_update_task_intent(self, mock_understand_intent):
        """测试处理更新任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "update_task"
        
        # 模拟任务信息提取
        with patch.object(self.task_agent, '_extract_task_info') as mock_extract:
            mock_extract.return_value = {
                "task_id": self.task_id,
                "status": "completed"
            }
            
            # 处理用户输入
            response = self.task_agent.process(f"将任务{self.task_id}标记为已完成")
            
            # 验证响应
            self.assertIn("更新成功", response)
            
            # 验证任务状态已更新
            task = self.task_service.get_task(self.task_id)
            self.assertTrue(task['success'])
            self.assertEqual(task['task']['status'], "completed")
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_list_tasks_intent(self, mock_understand_intent):
        """测试处理列出任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "list_tasks"
        
        # 处理用户输入
        response = self.task_agent.process("列出所有任务")
        
        # 验证响应
        self.assertIn("任务列表", response)
        self.assertIn(self.task_id, response)
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_show_task_intent(self, mock_understand_intent):
        """测试处理显示任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "show_task"
        
        # 模拟任务信息提取
        with patch.object(self.task_agent, '_extract_task_info') as mock_extract:
            mock_extract.return_value = {"task_id": self.task_id}
            
            # 处理用户输入
            response = self.task_agent.process(f"显示任务{self.task_id}的详情")
            
            # 验证响应
            self.assertIn("任务详情", response)
            self.assertIn(self.title, response)
            self.assertIn(self.description, response)
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_delete_task_intent(self, mock_understand_intent):
        """测试处理删除任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "delete_task"
        
        # 模拟任务信息提取
        with patch.object(self.task_agent, '_extract_task_info') as mock_extract:
            mock_extract.return_value = {"task_id": self.task_id}
            
            # 处理用户输入
            response = self.task_agent.process(f"删除任务{self.task_id}")
            
            # 验证响应
            self.assertIn("删除成功", response)
            
            # 验证任务已删除
            task = self.task_service.get_task(self.task_id)
            self.assertFalse(task['success'])
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_analyze_task_intent(self, mock_understand_intent):
        """测试处理分析任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "analyze_task"
        
        # 模拟任务信息提取
        with patch.object(self.task_agent, '_extract_task_info') as mock_extract:
            mock_extract.return_value = {"task_id": self.task_id}
            
            # 模拟DeepSeek API响应
            with patch.object(self.task_agent.deepseek_client, 'analyze_task') as mock_analyze:
                mock_analyze.return_value = {
                    "complexity": "medium",
                    "estimated_hours": 4,
                    "required_skills": ["Python", "数据分析"]
                }
                
                # 处理用户输入
                response = self.task_agent.process(f"分析任务{self.task_id}")
                
                # 验证响应
                self.assertIn("任务分析", response)
                self.assertIn("medium", response)
                self.assertIn("4", response)
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_suggest_tasks_intent(self, mock_understand_intent):
        """测试处理建议任务意图"""
        # 模拟意图识别结果
        mock_understand_intent.return_value = "suggest_tasks"
        
        # 模拟任务信息提取
        with patch.object(self.task_agent, '_extract_task_info') as mock_extract:
            mock_extract.return_value = {"project_description": "开发一个任务管理系统"}
            
            # 模拟DeepSeek API响应
            with patch.object(self.task_agent.deepseek_client, 'generate_task_suggestions') as mock_suggest:
                mock_suggest.return_value = [
                    {
                        "title": "需求分析",
                        "description": "分析项目需求",
                        "priority": "high",
                        "estimated_hours": 2
                    },
                    {
                        "title": "设计系统架构",
                        "description": "设计系统整体架构",
                        "priority": "high",
                        "estimated_hours": 4
                    }
                ]
                
                # 处理用户输入
                response = self.task_agent.process("为开发任务管理系统提供建议")
                
                # 验证响应
                self.assertIn("任务建议", response)
                self.assertIn("需求分析", response)
                self.assertIn("设计系统架构", response)
    
    @patch('src.agents.task_agent.TaskAgent._understand_intent')
    def test_process_optimize_tasks_intent(self, mock_understand_intent):
        """测试处理优化任务意图"""
        # 创建更多任务
        for i in range(3):
            self.task_service.create_task(
                title=f"任务{i}",
                description=f"这是任务{i}",
                priority=TaskPriority.MEDIUM,
                task_id=f"task-{i}"
            )
        
        # 模拟意图识别结果
        mock_understand_intent.return_value = "optimize_tasks"
        
        # 模拟DeepSeek API响应
        with patch.object(self.task_agent.deepseek_client, 'optimize_task_order') as mock_optimize:
            mock_optimize.return_value = [
                {"id": "task-0", "title": "任务0", "priority": "high"},
                {"id": "task-1", "title": "任务1", "priority": "medium"},
                {"id": "task-2", "title": "任务2", "priority": "low"}
            ]
            
            # 处理用户输入
            response = self.task_agent.process("优化任务顺序")
            
            # 验证响应
            self.assertIn("优化后的任务顺序", response)
            self.assertIn("任务0", response)
            self.assertIn("任务1", response)
            self.assertIn("任务2", response)
    
    def test_understand_intent(self):
        """测试意图识别"""
        # 测试创建任务意图
        intent = self.task_agent._understand_intent("创建一个新任务")
        self.assertEqual(intent, "create_task")
        
        # 测试更新任务意图
        intent = self.task_agent._understand_intent("更新任务状态")
        self.assertEqual(intent, "update_task")
        
        # 测试列出任务意图
        intent = self.task_agent._understand_intent("显示所有任务")
        self.assertEqual(intent, "list_tasks")
        
        # 测试显示任务意图
        intent = self.task_agent._understand_intent("查看任务详情")
        self.assertEqual(intent, "show_task")
        
        # 测试删除任务意图
        intent = self.task_agent._understand_intent("删除任务")
        self.assertEqual(intent, "delete_task")
        
        # 测试分析任务意图
        intent = self.task_agent._understand_intent("分析任务")
        self.assertEqual(intent, "analyze_task")
        
        # 测试建议任务意图
        intent = self.task_agent._understand_intent("提供任务建议")
        self.assertEqual(intent, "suggest_tasks")
        
        # 测试优化任务意图
        intent = self.task_agent._understand_intent("优化任务顺序")
        self.assertEqual(intent, "optimize_tasks")
    
    def test_extract_task_info(self):
        """测试任务信息提取"""
        # 测试创建任务信息提取
        info = self.task_agent._extract_task_info("创建一个高优先级的任务，标题是开发API，描述是实现用户认证API")
        self.assertEqual(info["title"], "开发API")
        self.assertEqual(info["description"], "实现用户认证API")
        self.assertEqual(info["priority"], "high")
        
        # 测试更新任务信息提取
        info = self.task_agent._extract_task_info(f"将任务{self.task_id}的状态更新为已完成")
        self.assertEqual(info["task_id"], self.task_id)
        self.assertEqual(info["status"], "completed")
        
        # 测试显示任务信息提取
        info = self.task_agent._extract_task_info(f"显示任务{self.task_id}的详情")
        self.assertEqual(info["task_id"], self.task_id)
        
        # 测试删除任务信息提取
        info = self.task_agent._extract_task_info(f"删除任务{self.task_id}")
        self.assertEqual(info["task_id"], self.task_id)
    
    def test_create_task_from_data(self):
        """测试从数据创建任务"""
        # 测试创建任务
        task_data = {
            "title": "测试任务",
            "description": "这是一个测试任务",
            "priority": "high",
            "estimated_hours": 3
        }
        
        task = self.task_agent._create_task_from_data(task_data)
        
        self.assertEqual(task.title, "测试任务")
        self.assertEqual(task.description, "这是一个测试任务")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.estimated_hours, 3)
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_format_task_details(self):
        """测试格式化任务详情"""
        # 获取任务
        task_result = self.task_service.get_task(self.task_id)
        task = task_result['task']
        
        # 格式化任务详情
        formatted = self.task_agent._format_task_details(task)
        
        self.assertIn("任务详情", formatted)
        self.assertIn(f"ID: {self.task_id}", formatted)
        self.assertIn(f"标题: {self.title}", formatted)
        self.assertIn(f"描述: {self.description}", formatted)
        self.assertIn("状态: pending", formatted)
        self.assertIn("优先级: medium", formatted)


if __name__ == "__main__":
    unittest.main()