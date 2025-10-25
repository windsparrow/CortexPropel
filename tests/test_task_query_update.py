#!/usr/bin/env python3
"""
测试任务查询和状态更新功能
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cortex_propel.models.task import Task, TaskStatus, TaskPriority
from cortex_propel.storage.file_manager import FileManager
from cortex_propel.utils.task_management import TaskQueryEngine, TaskStatusUpdater


def test_task_query_engine():
    """测试任务查询引擎"""
    print("测试任务查询引擎...")
    
    # 初始化文件管理器
    file_manager = FileManager()
    
    # 创建测试项目
    project_id = "test_query_project"
    project = file_manager.create_project(project_id, "测试查询项目", "用于测试查询功能的项目")
    
    # 创建测试任务
    tasks = []
    
    # 任务1: 高优先级，今天到期
    task1 = Task(
        id="task1",
        title="高优先级任务",
        description="这是一个高优先级任务，今天到期",
        priority=TaskPriority.HIGH,
        due_date=datetime.now(),
        status=TaskStatus.PENDING,
        tags=["urgent", "today"]
    )
    file_manager.save_task(task1, project_id)
    tasks.append(task1)
    
    # 任务2: 中优先级，明天到期
    task2 = Task(
        id="task2",
        title="中优先级任务",
        description="这是一个中优先级任务，明天到期",
        priority=TaskPriority.MEDIUM,
        due_date=datetime.now() + timedelta(days=1),
        status=TaskStatus.IN_PROGRESS,
        progress=30,
        tags=["normal", "tomorrow"]
    )
    file_manager.save_task(task2, project_id)
    tasks.append(task2)
    
    # 任务3: 低优先级，下周到期
    task3 = Task(
        id="task3",
        title="低优先级任务",
        description="这是一个低优先级任务，下周到期",
        priority=TaskPriority.LOW,
        due_date=datetime.now() + timedelta(days=7),
        status=TaskStatus.PENDING,
        tags=["low", "next-week"]
    )
    file_manager.save_task(task3, project_id)
    tasks.append(task3)
    
    # 任务4: 已完成任务
    task4 = Task(
        id="task4",
        title="已完成任务",
        description="这是一个已完成的任务",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.COMPLETED,
        progress=100,
        tags=["done"]
    )
    file_manager.save_task(task4, project_id)
    tasks.append(task4)
    
    # 创建任务5: 无截止日期的任务
    task5 = Task(
        id="task5",
        title="无截止日期任务",
        description="这是一个没有截止日期的任务",
        priority=TaskPriority.LOW,
        status=TaskStatus.PENDING,
        tags=["no-deadline"]
    )
    file_manager.save_task(task5, project_id)
    tasks.append(task5)
    
    # 创建任务6: 过期任务
    task6 = Task(
        id="task6",
        title="过期任务",
        description="这是一个已过期的任务",
        priority=TaskPriority.HIGH,
        due_date=datetime.now() - timedelta(days=2),
        status=TaskStatus.PENDING,
        tags=["overdue"]
    )
    file_manager.save_task(task6, project_id)
    tasks.append(task6)
    
    # 初始化查询引擎
    query_engine = TaskQueryEngine(file_manager)
    
    # 测试基本查询
    all_tasks = query_engine.query_tasks(project_id)
    print(f"总任务数: {len(all_tasks)}")
    
    # 测试状态过滤
    pending_tasks = query_engine.query_tasks(project_id, status=TaskStatus.PENDING)
    print(f"待处理任务数: {len(pending_tasks)}")
    
    # 测试优先级过滤
    high_priority_tasks = query_engine.query_tasks(project_id, priority=TaskPriority.HIGH)
    print(f"高优先级任务数: {len(high_priority_tasks)}")
    
    # 测试标签过滤
    urgent_tasks = query_engine.query_tasks(project_id, tags=["urgent"])
    print(f"紧急任务数: {len(urgent_tasks)}")
    
    # 测试自然语言查询
    today_tasks = query_engine.query_tasks(project_id, query="due today")
    print(f"今天到期的任务数: {len(today_tasks)}")
    
    overdue_tasks = query_engine.query_tasks(project_id, query="overdue")
    print(f"过期任务数: {len(overdue_tasks)}")
    
    # 测试排序
    tasks_by_priority = query_engine.query_tasks(project_id, sort_by="priority", sort_order="desc")
    print(f"按优先级降序排列的前3个任务:")
    for i, task in enumerate(tasks_by_priority[:3]):
        print(f"  {i+1}. {task.title} (优先级: {task.priority})")
    
    # 测试任务统计
    stats = query_engine.get_task_statistics(project_id)
    print("\n任务统计:")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  按状态: {stats['by_status']}")
    print(f"  按优先级: {stats['by_priority']}")
    print(f"  有截止日期的任务: {stats['with_due_date']}")
    print(f"  过期任务: {stats['overdue']}")
    print(f"  今天到期: {stats['due_today']}")
    print(f"  本周到期: {stats['due_this_week']}")
    print(f"  平均进度: {stats['average_progress']:.1f}%")
    
    # 测试任务层次结构
    # 创建一个父任务和子任务
    parent_task = Task(
        id="parent_task",
        title="父任务",
        description="这是一个父任务",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING
    )
    file_manager.save_task(parent_task, project_id)
    
    child_task1 = Task(
        id="child_task1",
        title="子任务1",
        description="这是父任务的第一个子任务",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        parent_id=parent_task.id
    )
    file_manager.save_task(child_task1, project_id)
    
    child_task2 = Task(
        id="child_task2",
        title="子任务2",
        description="这是父任务的第二个子任务",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        parent_id=parent_task.id
    )
    file_manager.save_task(child_task2, project_id)
    
    # 更新父任务的子任务列表
    parent_task.subtasks = [child_task1.id, child_task2.id]
    file_manager.save_task(parent_task, project_id)
    
    # 获取任务层次结构
    hierarchy = query_engine.get_task_hierarchy(project_id)
    print("\n任务层次结构:")
    for task_dict in hierarchy:
        task = task_dict["task"]
        subtasks = task_dict["subtasks"]
        print(f"  {task.title}")
        for subtask_dict in subtasks:
            subtask = subtask_dict["task"]
            print(f"    - {subtask.title}")
    
    print("任务查询引擎测试完成!\n")


def test_task_status_updater():
    """测试任务状态更新器"""
    print("测试任务状态更新器...")
    
    # 初始化文件管理器
    file_manager = FileManager()
    
    # 创建测试项目
    project_id = "test_update_project"
    project = file_manager.create_project(project_id, "测试更新项目", "用于测试更新功能的项目")
    
    # 创建测试任务
    task = Task(
        id="update_test_task",
        title="测试任务",
        description="这是一个用于测试状态更新的任务",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        progress=0
    )
    file_manager.save_task(task, project_id)
    
    # 初始化状态更新器
    status_updater = TaskStatusUpdater(file_manager)
    
    # 测试更新状态为进行中
    updated_task, additional_tasks = status_updater.update_task_status(
        project_id, task.id, status=TaskStatus.IN_PROGRESS
    )
    print(f"任务状态更新为: {updated_task.status.value}, 进度: {updated_task.progress}%")
    
    # 测试更新进度
    updated_task, additional_tasks = status_updater.update_task_status(
        project_id, task.id, progress=50
    )
    print(f"任务进度更新为: {updated_task.progress}%")
    
    # 测试更新状态为已完成
    updated_task, additional_tasks = status_updater.update_task_status(
        project_id, task.id, status=TaskStatus.COMPLETED
    )
    print(f"任务状态更新为: {updated_task.status.value}, 进度: {updated_task.progress}%")
    
    # 测试父子任务状态更新
    # 创建父任务
    parent_task = Task(
        id="parent_task_update",
        title="父任务",
        description="这是一个父任务",
        priority=TaskPriority.HIGH,
        status=TaskStatus.PENDING,
        progress=0
    )
    file_manager.save_task(parent_task, project_id)
    
    # 创建子任务
    child_task1 = Task(
        id="child_task1_update",
        title="子任务1",
        description="这是父任务的第一个子任务",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        progress=0,
        parent_id=parent_task.id
    )
    file_manager.save_task(child_task1, project_id)
    
    child_task2 = Task(
        id="child_task2_update",
        title="子任务2",
        description="这是父任务的第二个子任务",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.PENDING,
        progress=0,
        parent_id=parent_task.id
    )
    file_manager.save_task(child_task2, project_id)
    
    # 更新父任务的子任务列表
    parent_task.subtasks = [child_task1.id, child_task2.id]
    file_manager.save_task(parent_task, project_id)
    
    # 完成第一个子任务
    updated_child1, additional = status_updater.update_task_status(
        project_id, child_task1.id, status=TaskStatus.COMPLETED
    )
    print(f"子任务1状态更新为: {updated_child1.status.value}")
    
    # 检查父任务是否自动更新
    updated_parent = file_manager.load_task(parent_task.id, project_id)
    print(f"父任务状态: {updated_parent.status}, 进度: {updated_parent.progress}%")
    
    # 完成第二个子任务
    updated_child2, additional = status_updater.update_task_status(
        project_id, child_task2.id, status=TaskStatus.COMPLETED
    )
    print(f"子任务2状态更新为: {updated_child2.status}")
    
    # 检查父任务是否自动更新为已完成
    updated_parent = file_manager.load_task(parent_task.id, project_id)
    print(f"父任务状态: {updated_parent.status}, 进度: {updated_parent.progress}%")
    
    # 测试获取建议的下一步行动
    suggestions = status_updater.get_suggested_next_actions(project_id)
    print("\n建议的下一步行动:")
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"  {i+1}. {suggestion['action']}")
        print(f"     原因: {suggestion['reason']}")
    
    print("任务状态更新器测试完成!\n")


if __name__ == "__main__":
    test_task_query_engine()
    test_task_status_updater()
    print("所有测试完成!")