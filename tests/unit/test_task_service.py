import unittest
import json
import os
import tempfile
from datetime import datetime, timedelta
from src.models.task import Task, TaskStatus, TaskPriority
from src.services.task_service import TaskService


class TestTaskService(unittest.TestCase):
    """任务服务单元测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        # 初始化任务服务
        self.task_service = TaskService(self.temp_file.name)
        
        # 创建测试任务
        self.task_id = "test-task-123"
        self.title = "测试任务"
        self.description = "这是一个测试任务"
        self.due_date = datetime.now() + timedelta(days=7)
        
        self.task = Task(
            id=self.task_id,
            title=self.title,
            description=self.description,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date
        )
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        os.unlink(self.temp_file.name)
    
    def test_create_task(self):
        """测试创建任务"""
        result = self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['task_id'])
        self.assertEqual(result['message'], "任务创建成功")
        
        # 验证任务是否正确保存
        task = self.task_service.get_task(result['task_id'])
        self.assertTrue(task['success'])
        self.assertEqual(task['task']['title'], self.title)
        self.assertEqual(task['task']['description'], self.description)
        self.assertEqual(task['task']['priority'], "medium")
    
    def test_create_task_with_custom_id(self):
        """测试使用自定义ID创建任务"""
        result = self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date,
            task_id=self.task_id
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['task_id'], self.task_id)
        
        # 验证任务是否正确保存
        task = self.task_service.get_task(self.task_id)
        self.assertTrue(task['success'])
        self.assertEqual(task['task']['id'], self.task_id)
    
    def test_create_duplicate_task(self):
        """测试创建重复任务"""
        # 先创建一个任务
        self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date,
            task_id=self.task_id
        )
        
        # 尝试创建相同ID的任务
        result = self.task_service.create_task(
            title="另一个任务",
            description="这是另一个任务",
            priority=TaskPriority.HIGH,
            task_id=self.task_id
        )
        
        self.assertFalse(result['success'])
        self.assertIn("已存在", result['message'])
    
    def test_get_task(self):
        """测试获取任务"""
        # 创建任务
        self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date,
            task_id=self.task_id
        )
        
        # 获取任务
        result = self.task_service.get_task(self.task_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['task']['id'], self.task_id)
        self.assertEqual(result['task']['title'], self.title)
        self.assertEqual(result['task']['description'], self.description)
    
    def test_get_nonexistent_task(self):
        """测试获取不存在的任务"""
        result = self.task_service.get_task("nonexistent-task")
        
        self.assertFalse(result['success'])
        self.assertIn("不存在", result['message'])
    
    def test_update_task(self):
        """测试更新任务"""
        # 创建任务
        self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date,
            task_id=self.task_id
        )
        
        # 更新任务
        new_title = "更新后的任务"
        new_description = "更新后的描述"
        new_status = TaskStatus.IN_PROGRESS
        new_priority = TaskPriority.HIGH
        
        result = self.task_service.update_task(
            task_id=self.task_id,
            title=new_title,
            description=new_description,
            status=new_status,
            priority=new_priority
        )
        
        self.assertTrue(result['success'])
        
        # 验证更新结果
        task = self.task_service.get_task(self.task_id)
        self.assertTrue(task['success'])
        self.assertEqual(task['task']['title'], new_title)
        self.assertEqual(task['task']['description'], new_description)
        self.assertEqual(task['task']['status'], "in_progress")
        self.assertEqual(task['task']['priority'], "high")
    
    def test_update_nonexistent_task(self):
        """测试更新不存在的任务"""
        result = self.task_service.update_task(
            task_id="nonexistent-task",
            title="更新后的任务"
        )
        
        self.assertFalse(result['success'])
        self.assertIn("不存在", result['message'])
    
    def test_delete_task(self):
        """测试删除任务"""
        # 创建任务
        self.task_service.create_task(
            title=self.title,
            description=self.description,
            priority=TaskPriority.MEDIUM,
            due_date=self.due_date,
            task_id=self.task_id
        )
        
        # 删除任务
        result = self.task_service.delete_task(self.task_id)
        
        self.assertTrue(result['success'])
        
        # 验证任务已删除
        task = self.task_service.get_task(self.task_id)
        self.assertFalse(task['success'])
    
    def test_delete_nonexistent_task(self):
        """测试删除不存在的任务"""
        result = self.task_service.delete_task("nonexistent-task")
        
        self.assertFalse(result['success'])
        self.assertIn("不存在", result['message'])
    
    def test_list_tasks(self):
        """测试列出任务"""
        # 创建多个任务
        task_ids = []
        for i in range(5):
            task_id = f"task-{i}"
            task_ids.append(task_id)
            self.task_service.create_task(
                title=f"任务 {i}",
                description=f"这是任务 {i}",
                priority=TaskPriority.MEDIUM,
                task_id=task_id
            )
        
        # 列出所有任务
        result = self.task_service.list_tasks()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 5)
        self.assertEqual(len(result['tasks']), 5)
        
        # 验证任务ID
        returned_ids = [task['id'] for task in result['tasks']]
        for task_id in task_ids:
            self.assertIn(task_id, returned_ids)
    
    def test_list_tasks_with_filters(self):
        """测试使用过滤器列出任务"""
        # 创建不同状态和优先级的任务
        self.task_service.create_task(
            title="高优先级任务",
            description="高优先级",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            task_id="high-priority"
        )
        
        self.task_service.create_task(
            title="进行中任务",
            description="进行中",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.IN_PROGRESS,
            task_id="in-progress"
        )
        
        self.task_service.create_task(
            title="已完成任务",
            description="已完成",
            priority=TaskPriority.LOW,
            status=TaskStatus.COMPLETED,
            task_id="completed"
        )
        
        # 按状态过滤
        result = self.task_service.list_tasks(status=TaskStatus.PENDING)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['tasks'][0]['id'], "high-priority")
        
        # 按优先级过滤
        result = self.task_service.list_tasks(priority=TaskPriority.HIGH)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['tasks'][0]['id'], "high-priority")
        
        # 组合过滤
        result = self.task_service.list_tasks(
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 1)
        self.assertEqual(result['tasks'][0]['id'], "high-priority")
    
    def test_add_subtask(self):
        """测试添加子任务"""
        # 创建父任务
        self.task_service.create_task(
            title="父任务",
            description="这是一个父任务",
            task_id="parent-task"
        )
        
        # 创建子任务
        result = self.task_service.create_task(
            title="子任务",
            description="这是一个子任务",
            task_id="subtask"
        )
        
        # 添加子任务到父任务
        add_result = self.task_service.add_subtask("parent-task", result['task_id'])
        
        self.assertTrue(add_result['success'])
        
        # 验证子任务已添加
        parent_task = self.task_service.get_task("parent-task")
        self.assertTrue(parent_task['success'])
        self.assertIn(result['task_id'], parent_task['task']['subtasks'])
    
    def test_add_dependency(self):
        """测试添加依赖关系"""
        # 创建任务
        self.task_service.create_task(
            title="任务1",
            description="这是任务1",
            task_id="task-1"
        )
        
        result = self.task_service.create_task(
            title="任务2",
            description="这是任务2",
            task_id="task-2"
        )
        
        # 添加依赖关系
        add_result = self.task_service.add_dependency(result['task_id'], "task-1")
        
        self.assertTrue(add_result['success'])
        
        # 验证依赖关系已添加
        task2 = self.task_service.get_task(result['task_id'])
        self.assertTrue(task2['success'])
        self.assertIn("task-1", task2['task']['dependencies'])


if __name__ == "__main__":
    unittest.main()