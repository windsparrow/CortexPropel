#!/usr/bin/env python3
"""
CortexPropel 任务查询和状态更新功能使用示例

这个示例展示了如何使用 TaskQueryEngine 和 TaskStatusUpdater 类
来查询、过滤、排序和更新任务状态。
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.cortex_propel.models.task import Task, TaskStatus, TaskPriority
from src.cortex_propel.models.project import Project
from src.cortex_propel.storage.file_manager import FileManager
from src.cortex_propel.utils.task_management import TaskQueryEngine, TaskStatusUpdater


def create_sample_tasks():
    """创建示例任务"""
    # 创建文件管理器
    file_manager = FileManager()
    
    # 创建项目
    project = Project(
        id="sample_project",
        name="示例项目",
        description="用于演示任务查询和状态更新功能的示例项目"
    )
    file_manager.save_project(project)
    project_id = project.id
    
    # 创建示例任务
    tasks = [
        Task(
            id="task_1",
            title="设计系统架构",
            description="设计整个系统的架构和组件关系",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            due_date=(datetime.now() - timedelta(days=2)).date(),
            progress=100
        ),
        Task(
            id="task_2",
            title="实现核心功能",
            description="实现系统的核心功能模块",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=(datetime.now() + timedelta(days=3)).date(),
            progress=60
        ),
        Task(
            id="task_3",
            title="编写单元测试",
            description="为核心功能编写单元测试",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            due_date=(datetime.now() + timedelta(days=5)).date(),
            progress=0
        ),
        Task(
            id="task_4",
            title="优化性能",
            description="优化系统性能，减少响应时间",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW,
            due_date=(datetime.now() + timedelta(days=10)).date(),
            progress=0
        ),
        Task(
            id="task_5",
            title="编写文档",
            description="编写用户手册和API文档",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            due_date=(datetime.now() + timedelta(days=7)).date(),
            progress=0
        ),
        Task(
            id="task_6",
            title="部署系统",
            description="将系统部署到生产环境",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            due_date=(datetime.now() + timedelta(days=1)).date(),
            progress=0
        )
    ]
    
    # 保存任务
    for task in tasks:
        file_manager.save_task(task, project_id)
    
    return project_id


def demonstrate_task_querying(project_id):
    """演示任务查询功能"""
    print("\n=== 任务查询功能演示 ===")
    
    # 创建文件管理器和任务查询引擎
    file_manager = FileManager()
    query_engine = TaskQueryEngine(file_manager)
    
    # 获取所有任务
    all_tasks = query_engine.query_tasks(project_id)
    print(f"\n项目中共有 {len(all_tasks)} 个任务")
    
    # 按状态过滤
    pending_tasks = query_engine.query_tasks(project_id, status=TaskStatus.PENDING)
    print(f"\n待处理任务: {len(pending_tasks)} 个")
    for task in pending_tasks:
        print(f"  - {task.title} (优先级: {task.priority})")
    
    # 按优先级过滤
    high_priority_tasks = query_engine.query_tasks(project_id, priority=TaskPriority.HIGH)
    print(f"\n高优先级任务: {len(high_priority_tasks)} 个")
    for task in high_priority_tasks:
        print(f"  - {task.title} (状态: {task.status})")
    
    # 按截止日期过滤
    overdue_tasks = query_engine.query_tasks(project_id, due_before=datetime.now().date())
    print(f"\n过期任务: {len(overdue_tasks)} 个")
    for task in overdue_tasks:
        print(f"  - {task.title} (截止日期: {task.due_date})")
    
    # 排序
    print("\n按优先级排序的任务:")
    tasks_by_priority = query_engine.query_tasks(project_id, sort_by="priority", sort_order="desc")
    for i, task in enumerate(tasks_by_priority, 1):
        print(f"  {i}. {task.title} (优先级: {task.priority})")
    
    print("\n按截止日期排序的任务:")
    tasks_by_due_date = query_engine.query_tasks(project_id, sort_by="due_date", sort_order="asc")
    for i, task in enumerate(tasks_by_due_date, 1):
        due_date_str = task.due_date.strftime("%Y-%m-%d") if task.due_date else "无截止日期"
        print(f"  {i}. {task.title} (截止日期: {due_date_str})")
    
    # 搜索任务
    print("\n搜索包含'系统'的任务:")
    search_results = query_engine.query_tasks(project_id, query="系统")
    for task in search_results:
        print(f"  - {task.title}: {task.description}")
    
    # 获取任务统计
    print("\n任务统计:")
    stats = query_engine.get_task_statistics(project_id)
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  按状态: {stats['by_status']}")
    print(f"  按优先级: {stats['by_priority']}")
    print(f"  有截止日期的任务: {stats['with_due_date']}")
    print(f"  过期任务: {stats['overdue']}")
    print(f"  今天到期: {stats['due_today']}")
    print(f"  本周到期: {stats['due_this_week']}")
    print(f"  平均进度: {stats['average_progress']:.1f}%")


def demonstrate_task_status_updates(project_id):
    """演示任务状态更新功能"""
    print("\n=== 任务状态更新功能演示 ===")
    
    # 创建文件管理器和任务状态更新器
    file_manager = FileManager()
    status_updater = TaskStatusUpdater(file_manager)
    
    # 更新任务状态
    task_id = "task_3"  # 编写单元测试
    print(f"\n更新任务 '{task_id}' 的状态...")
    
    # 开始任务
    updated_task, additional_info = status_updater.update_task_status(
        project_id, task_id, status=TaskStatus.IN_PROGRESS, progress=30
    )
    print(f"  状态更新为: {updated_task.status}, 进度: {updated_task.progress}%")
    
    # 更新进度
    updated_task, additional_info = status_updater.update_task_progress(
        project_id, task_id, progress=70
    )
    print(f"  进度更新为: {updated_task.progress}%")
    
    # 完成任务
    updated_task, additional_info = status_updater.update_task_status(
        project_id, task_id, status=TaskStatus.COMPLETED
    )
    print(f"  状态更新为: {updated_task.status}, 进度: {updated_task.progress}%")
    
    # 批量更新任务优先级
    print("\n批量更新任务优先级...")
    task_ids = ["task_4", "task_5"]  # 优化性能、编写文档
    updated_tasks = status_updater.bulk_update_priority(
        project_id, task_ids, TaskPriority.HIGH
    )
    print(f"  更新了 {len(updated_tasks)} 个任务的优先级")
    for task in updated_tasks:
        print(f"    - {task.title}: 优先级 -> {task.priority}")
    
    # 获取建议的下一步行动
    print("\n建议的下一步行动:")
    next_actions = status_updater.get_suggested_next_actions(project_id)
    for action in next_actions:
        print(f"  - {action['action']}: {action['reason']}")


def main():
    """主函数"""
    print("CortexPropel 任务查询和状态更新功能使用示例")
    
    # 创建示例任务
    print("\n创建示例任务...")
    project_id = create_sample_tasks()
    print("示例任务创建完成!")
    
    # 演示任务查询功能
    demonstrate_task_querying(project_id)
    
    # 演示任务状态更新功能
    demonstrate_task_status_updates(project_id)
    
    print("\n示例演示完成!")


if __name__ == "__main__":
    main()