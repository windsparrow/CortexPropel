import unittest
from datetime import datetime, timedelta
from src.models.task import Task, TaskStatus, TaskPriority


class TestTaskModel(unittest.TestCase):
    """任务模型单元测试"""
    
    def setUp(self):
        """测试前准备"""
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
    
    def test_task_creation(self):
        """测试任务创建"""
        self.assertEqual(self.task.id, self.task_id)
        self.assertEqual(self.task.title, self.title)
        self.assertEqual(self.task.description, self.description)
        self.assertEqual(self.task.status, TaskStatus.PENDING)
        self.assertEqual(self.task.priority, TaskPriority.MEDIUM)
        self.assertEqual(self.task.due_date, self.due_date)
        self.assertIsNone(self.task.parent_task_id)
        self.assertEqual(self.task.subtasks, [])
        self.assertEqual(self.task.dependencies, [])
        self.assertIsNone(self.task.estimated_hours)
        self.assertIsNone(self.task.actual_hours)
        self.assertIsNone(self.task.created_at)
        self.assertIsNone(self.task.updated_at)
    
    def test_task_to_dict(self):
        """测试任务转换为字典"""
        task_dict = self.task.to_dict()
        
        self.assertEqual(task_dict["id"], self.task_id)
        self.assertEqual(task_dict["title"], self.title)
        self.assertEqual(task_dict["description"], self.description)
        self.assertEqual(task_dict["status"], "pending")
        self.assertEqual(task_dict["priority"], "medium")
        self.assertEqual(task_dict["due_date"], self.due_date.isoformat())
        self.assertIsNone(task_dict["parent_task_id"])
        self.assertEqual(task_dict["subtasks"], [])
        self.assertEqual(task_dict["dependencies"], [])
        self.assertIsNone(task_dict["estimated_hours"])
        self.assertIsNone(task_dict["actual_hours"])
    
    def test_task_from_dict(self):
        """测试从字典创建任务"""
        task_dict = {
            "id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": "pending",
            "priority": "medium",
            "due_date": self.due_date.isoformat(),
            "parent_task_id": None,
            "subtasks": [],
            "dependencies": [],
            "estimated_hours": 2.5,
            "actual_hours": None
        }
        
        task = Task.from_dict(task_dict)
        
        self.assertEqual(task.id, self.task_id)
        self.assertEqual(task.title, self.title)
        self.assertEqual(task.description, self.description)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.priority, TaskPriority.MEDIUM)
        self.assertEqual(task.due_date, self.due_date)
        self.assertIsNone(task.parent_task_id)
        self.assertEqual(task.subtasks, [])
        self.assertEqual(task.dependencies, [])
        self.assertEqual(task.estimated_hours, 2.5)
        self.assertIsNone(task.actual_hours)
    
    def test_task_with_subtasks(self):
        """测试带子任务的任务"""
        subtask1 = Task(
            id="subtask-1",
            title="子任务1",
            description="第一个子任务",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        
        subtask2 = Task(
            id="subtask-2",
            title="子任务2",
            description="第二个子任务",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.LOW
        )
        
        self.task.subtasks = [subtask1, subtask2]
        
        self.assertEqual(len(self.task.subtasks), 2)
        self.assertEqual(self.task.subtasks[0].title, "子任务1")
        self.assertEqual(self.task.subtasks[1].title, "子任务2")
    
    def test_task_with_dependencies(self):
        """测试带依赖关系的任务"""
        self.task.dependencies = ["task-1", "task-2"]
        
        self.assertEqual(len(self.task.dependencies), 2)
        self.assertIn("task-1", self.task.dependencies)
        self.assertIn("task-2", self.task.dependencies)
    
    def test_task_status_enum(self):
        """测试任务状态枚举"""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.CANCELLED.value, "cancelled")
    
    def test_task_priority_enum(self):
        """测试任务优先级枚举"""
        self.assertEqual(TaskPriority.LOW.value, "low")
        self.assertEqual(TaskPriority.MEDIUM.value, "medium")
        self.assertEqual(TaskPriority.HIGH.value, "high")


if __name__ == "__main__":
    unittest.main()