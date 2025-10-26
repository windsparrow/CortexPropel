"""
示例和测试数据生成器
用于演示和测试CortexPropel功能
"""

import json
from datetime import datetime, timedelta
from models.task import TaskManager, TaskStatus, TaskPriority


def create_sample_tasks():
    """创建示例任务数据"""
    task_manager = TaskManager("sample_tasks.json")
    
    # 创建一些示例任务
    tasks_data = [
        {
            "title": "完成项目需求分析",
            "description": "分析用户需求，编写需求文档，确定功能范围",
            "priority": TaskPriority.HIGH,
            "due_date": datetime.now() + timedelta(days=3)
        },
        {
            "title": "设计数据库架构",
            "description": "设计系统数据库表结构，确定数据关系",
            "priority": TaskPriority.MEDIUM,
            "due_date": datetime.now() + timedelta(days=7)
        },
        {
            "title": "实现用户认证模块",
            "description": "开发用户注册、登录、权限管理功能",
            "priority": TaskPriority.HIGH,
            "due_date": datetime.now() + timedelta(days=10)
        },
        {
            "title": "编写单元测试",
            "description": "为核心功能编写单元测试用例",
            "priority": TaskPriority.MEDIUM,
            "due_date": datetime.now() + timedelta(days=14)
        },
        {
            "title": "部署测试环境",
            "description": "配置测试服务器，部署应用程序",
            "priority": TaskPriority.LOW,
            "due_date": datetime.now() + timedelta(days=5)
        },
        {
            "title": "编写API文档",
            "description": "为所有API接口编写详细文档",
            "priority": TaskPriority.MEDIUM,
            "due_date": datetime.now() + timedelta(days=12)
        }
    ]
    
    # 创建任务
    created_tasks = []
    for task_data in tasks_data:
        task = task_manager.create_task(
            title=task_data["title"],
            description=task_data["description"],
            priority=task_data["priority"],
            due_date=task_data["due_date"]
        )
        created_tasks.append(task)
    
    # 设置一些任务为不同状态
    # 完成第一个任务
    created_tasks[0].update_status(TaskStatus.COMPLETED)
    task_manager.update_task(created_tasks[0].id, status=TaskStatus.COMPLETED)
    
    # 设置第二个任务为进行中
    created_tasks[1].update_status(TaskStatus.IN_PROGRESS)
    task_manager.update_task(created_tasks[1].id, status=TaskStatus.IN_PROGRESS)
    
    # 设置第三个任务为被阻塞
    created_tasks[2].update_status(TaskStatus.BLOCKED)
    task_manager.update_task(created_tasks[2].id, status=TaskStatus.BLOCKED)
    
    # 为完成的任务添加一些标签
    created_tasks[0].add_tag("已完成")
    created_tasks[0].add_tag("需求分析")
    task_manager.update_task(created_tasks[0].id, tags=created_tasks[0].tags)
    
    return task_manager


def create_test_scenarios():
    """创建测试场景数据"""
    task_manager = TaskManager("test_scenarios.json")
    
    # 场景1: 逾期任务
    overdue_task = task_manager.create_task(
        title="逾期的报告撰写",
        description="这个任务已经逾期了",
        priority=TaskPriority.HIGH,
        due_date=datetime.now() - timedelta(days=2)
    )
    
    # 场景2: 即将到期任务
    due_soon_task = task_manager.create_task(
        title="即将到期的演示准备",
        description="明天就要演示了",
        priority=TaskPriority.URGENT,
        due_date=datetime.now() + timedelta(days=1)
    )
    
    # 场景3: 长时间运行的任务
    long_running_task = task_manager.create_task(
        title="长时间运行的数据处理",
        description="这个任务已经运行很久了",
        priority=TaskPriority.MEDIUM
    )
    long_running_task.update_status(TaskStatus.IN_PROGRESS)
    # 模拟一周前的更新时间
    long_running_task.updated_at = datetime.now() - timedelta(days=8)
    task_manager.update_task(
        long_running_task.id, 
        status=TaskStatus.IN_PROGRESS,
        updated_at=long_running_task.updated_at
    )
    
    # 场景4: 长时间未更新的任务
    stale_task = task_manager.create_task(
        title="被遗忘的任务",
        description="这个任务很久没更新了",
        priority=TaskPriority.LOW
    )
    # 模拟两周前的更新时间
    stale_task.updated_at = datetime.now() - timedelta(days=15)
    task_manager.update_task(
        stale_task.id,
        updated_at=stale_task.updated_at
    )
    
    return task_manager


def generate_demo_data():
    """生成演示数据"""
    print("正在生成示例数据...")
    
    # 创建示例任务
    sample_manager = create_sample_tasks()
    print(f"✓ 创建了 {len(sample_manager.get_all_tasks())} 个示例任务")
    
    # 创建测试场景
    test_manager = create_test_scenarios()
    print(f"✓ 创建了 {len(test_manager.get_all_tasks())} 个测试场景任务")
    
    print("\n示例数据生成完成！")
    print("\n生成的文件:")
    print("- sample_tasks.json: 示例任务数据")
    print("- test_scenarios.json: 测试场景数据")
    
    return sample_manager, test_manager


if __name__ == "__main__":
    generate_demo_data()