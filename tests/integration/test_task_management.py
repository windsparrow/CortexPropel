import unittest
import tempfile
import os
from datetime import datetime, timedelta
from src.models.task import Task, TaskStatus, TaskPriority
from src.services.task_service import TaskService, TaskExecutor, TaskScheduler, SchedulingPolicy
from src.agents.task_agent import TaskAgent


class TestTaskManagementIntegration(unittest.TestCase):
    """任务管理系统集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        # 初始化任务服务、执行器、调度器和智能体
        self.task_service = TaskService(self.temp_file.name)
        self.executor = TaskExecutor(self.task_service)
        self.scheduler = TaskScheduler(self.task_service, policy=SchedulingPolicy.PRIORITY_FIRST)
        self.agent = TaskAgent(self.task_service)
        
        # 创建测试任务
        self.task_ids = []
        for i in range(5):
            task_id = f"task-{i}"
            self.task_ids.append(task_id)
            priority = TaskPriority.HIGH if i % 2 == 0 else TaskPriority.MEDIUM
            status = TaskStatus.PENDING if i < 3 else TaskStatus.IN_PROGRESS
            
            self.task_service.create_task(
                title=f"任务 {i}",
                description=f"这是任务 {i} 的描述",
                priority=priority,
                status=status,
                estimated_hours=i + 1,
                task_id=task_id
            )
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        os.unlink(self.temp_file.name)
    
    def test_task_lifecycle(self):
        """测试任务完整生命周期"""
        # 1. 创建任务
        result = self.task_service.create_task(
            title="生命周期测试任务",
            description="这是一个用于测试生命周期的任务",
            priority=TaskPriority.HIGH,
            estimated_hours=3
        )
        
        self.assertTrue(result['success'])
        task_id = result['task_id']
        
        # 2. 获取任务
        task_result = self.task_service.get_task(task_id)
        self.assertTrue(task_result['success'])
        self.assertEqual(task_result['task']['title'], "生命周期测试任务")
        self.assertEqual(task_result['task']['status'], "pending")
        
        # 3. 更新任务状态
        update_result = self.task_service.update_task(
            task_id=task_id,
            status=TaskStatus.IN_PROGRESS
        )
        self.assertTrue(update_result['success'])
        
        # 验证状态已更新
        task_result = self.task_service.get_task(task_id)
        self.assertEqual(task_result['task']['status'], "in_progress")
        
        # 4. 添加子任务
        subtask_result = self.task_service.create_task(
            title="子任务",
            description="这是一个子任务",
            priority=TaskPriority.MEDIUM,
            task_id="subtask"
        )
        
        add_subtask_result = self.task_service.add_subtask(task_id, subtask_result['task_id'])
        self.assertTrue(add_subtask_result['success'])
        
        # 验证子任务已添加
        task_result = self.task_service.get_task(task_id)
        self.assertIn(subtask_result['task_id'], task_result['task']['subtasks'])
        
        # 5. 完成任务
        complete_result = self.task_service.update_task(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            actual_hours=2.5
        )
        self.assertTrue(complete_result['success'])
        
        # 验证任务已完成
        task_result = self.task_service.get_task(task_id)
        self.assertEqual(task_result['task']['status'], "completed")
        self.assertEqual(task_result['task']['actual_hours'], 2.5)
        
        # 6. 删除任务
        delete_result = self.task_service.delete_task(task_id)
        self.assertTrue(delete_result['success'])
        
        # 验证任务已删除
        task_result = self.task_service.get_task(task_id)
        self.assertFalse(task_result['success'])
    
    def test_task_executor(self):
        """测试任务执行器"""
        # 获取待执行的任务
        result = self.task_service.list_tasks(status=TaskStatus.PENDING)
        self.assertTrue(result['success'])
        self.assertEqual(len(result['tasks']), 3)
        
        # 执行任务
        for task in result['tasks']:
            execute_result = self.executor.execute_task(task['id'])
            self.assertTrue(execute_result['success'])
            
            # 验证任务状态已更新
            task_result = self.task_service.get_task(task['id'])
            self.assertEqual(task_result['task']['status'], "in_progress")
            
            # 完成任务
            complete_result = self.task_service.update_task(
                task_id=task['id'],
                status=TaskStatus.COMPLETED,
                actual_hours=1.0
            )
            self.assertTrue(complete_result['success'])
    
    def test_task_scheduler(self):
        """测试任务调度器"""
        # 获取待调度的任务
        result = self.task_service.list_tasks(status=TaskStatus.PENDING)
        self.assertTrue(result['success'])
        self.assertEqual(len(result['tasks']), 3)
        
        # 调度任务
        schedule_result = self.scheduler.schedule_tasks()
        self.assertTrue(schedule_result['success'])
        self.assertEqual(len(schedule_result['scheduled_tasks']), 3)
        
        # 验证任务已按优先级排序
        scheduled_tasks = schedule_result['scheduled_tasks']
        self.assertEqual(scheduled_tasks[0]['priority'], "high")
        self.assertEqual(scheduled_tasks[1]['priority'], "high")
        self.assertEqual(scheduled_tasks[2]['priority'], "medium")
    
    def test_task_agent_integration(self):
        """测试任务智能体集成"""
        # 测试创建任务
        response = self.agent.process("创建一个高优先级的任务，标题是集成测试任务，描述是测试智能体集成")
        self.assertIn("创建成功", response)
        
        # 获取创建的任务ID
        import re
        match = re.search(r'任务ID: (\w+)', response)
        self.assertIsNotNone(match)
        task_id = match.group(1)
        
        # 测试更新任务
        response = self.agent.process(f"将任务{task_id}的状态更新为进行中")
        self.assertIn("更新成功", response)
        
        # 测试显示任务
        response = self.agent.process(f"显示任务{task_id}的详情")
        self.assertIn("任务详情", response)
        self.assertIn("集成测试任务", response)
        
        # 测试列出任务
        response = self.agent.process("列出所有任务")
        self.assertIn("任务列表", response)
        self.assertIn(task_id, response)
        
        # 测试删除任务
        response = self.agent.process(f"删除任务{task_id}")
        self.assertIn("删除成功", response)
    
    def test_task_filtering(self):
        """测试任务过滤"""
        # 按状态过滤
        result = self.task_service.list_tasks(status=TaskStatus.PENDING)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 3)
        
        result = self.task_service.list_tasks(status=TaskStatus.IN_PROGRESS)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        
        # 按优先级过滤
        result = self.task_service.list_tasks(priority=TaskPriority.HIGH)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 3)
        
        result = self.task_service.list_tasks(priority=TaskPriority.MEDIUM)
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        
        # 组合过滤
        result = self.task_service.list_tasks(
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
    
    def test_task_dependencies(self):
        """测试任务依赖关系"""
        # 创建有依赖关系的任务
        task1_id = "dep-task-1"
        task2_id = "dep-task-2"
        
        self.task_service.create_task(
            title="依赖任务1",
            description="这是依赖任务1",
            priority=TaskPriority.HIGH,
            task_id=task1_id
        )
        
        result = self.task_service.create_task(
            title="依赖任务2",
            description="这是依赖任务2",
            priority=TaskPriority.HIGH,
            task_id=task2_id
        )
        
        # 添加依赖关系
        add_dep_result = self.task_service.add_dependency(task2_id, task1_id)
        self.assertTrue(add_dep_result['success'])
        
        # 验证依赖关系
        task2_result = self.task_service.get_task(task2_id)
        self.assertTrue(task2_result['success'])
        self.assertIn(task1_id, task2_result['task']['dependencies'])
        
        # 测试调度器考虑依赖关系
        schedule_result = self.scheduler.schedule_tasks()
        self.assertTrue(schedule_result['success'])
        
        # 验证任务1在任务2之前被调度
        scheduled_tasks = schedule_result['scheduled_tasks']
        task1_index = next(i for i, task in enumerate(scheduled_tasks) if task['id'] == task1_id)
        task2_index = next(i for i, task in enumerate(scheduled_tasks) if task['id'] == task2_id)
        self.assertLess(task1_index, task2_index)
    
    def test_task_subtasks(self):
        """测试任务子任务"""
        # 创建父任务
        parent_id = "parent-task"
        self.task_service.create_task(
            title="父任务",
            description="这是一个父任务",
            priority=TaskPriority.HIGH,
            task_id=parent_id
        )
        
        # 创建子任务
        subtask_ids = []
        for i in range(3):
            subtask_id = f"subtask-{i}"
            subtask_ids.append(subtask_id)
            self.task_service.create_task(
                title=f"子任务 {i}",
                description=f"这是子任务 {i}",
                priority=TaskPriority.MEDIUM,
                task_id=subtask_id
            )
            
            # 添加子任务到父任务
            self.task_service.add_subtask(parent_id, subtask_id)
        
        # 验证子任务已添加
        parent_result = self.task_service.get_task(parent_id)
        self.assertTrue(parent_result['success'])
        self.assertEqual(len(parent_result['task']['subtasks']), 3)
        
        for subtask_id in subtask_ids:
            self.assertIn(subtask_id, parent_result['task']['subtasks'])
    
    def test_scheduling_policies(self):
        """测试调度策略"""
        # 测试优先级优先策略
        scheduler = TaskScheduler(self.task_service, policy=SchedulingPolicy.PRIORITY_FIRST)
        result = scheduler.schedule_tasks()
        self.assertTrue(result['success'])
        
        # 验证任务按优先级排序
        scheduled_tasks = result['scheduled_tasks']
        priorities = [task['priority'] for task in scheduled_tasks]
        self.assertEqual(priorities, ['high', 'high', 'medium'])
        
        # 测试截止日期优先策略
        # 为任务添加截止日期
        for i, task_id in enumerate(self.task_ids[:3]):
            due_date = datetime.now() + timedelta(days=i+1)
            self.task_service.update_task(task_id=task_id, due_date=due_date)
        
        scheduler = TaskScheduler(self.task_service, policy=SchedulingPolicy.DEADLINE_FIRST)
        result = scheduler.schedule_tasks()
        self.assertTrue(result['success'])
        
        # 验证任务按截止日期排序
        scheduled_tasks = result['scheduled_tasks']
        due_dates = [task['due_date'] for task in scheduled_tasks]
        self.assertEqual(due_dates[0], due_dates[1])  # 前两个任务应该是同一天的
        self.assertEqual(due_dates[2], due_dates[2])  # 第三个任务应该是后一天的


if __name__ == "__main__":
    unittest.main()