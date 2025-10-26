"""
任务管理数据模型
定义任务的数据结构和相关操作
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"    # 已完成
    CANCELLED = "cancelled"  # 已取消
    BLOCKED = "blocked"      # 被阻塞


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    """任务数据模型"""
    id: str = Field(description="任务唯一标识")
    title: str = Field(description="任务标题")
    description: str = Field(description="任务描述")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="任务优先级")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    parent_id: Optional[str] = Field(None, description="父任务ID")
    subtask_ids: List[str] = Field(default_factory=list, description="子任务ID列表")
    tags: List[str] = Field(default_factory=list, description="任务标签")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    def update_status(self, new_status: TaskStatus):
        """更新任务状态"""
        self.status = new_status
        self.updated_at = datetime.now()
        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.now()
    
    def add_subtask(self, subtask_id: str):
        """添加子任务"""
        if subtask_id not in self.subtask_ids:
            self.subtask_ids.append(subtask_id)
            self.updated_at = datetime.now()
    
    def add_tag(self, tag: str):
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()


class TaskManager:
    """任务管理器"""
    
    def __init__(self, data_file: str = "tasks.json"):
        self.data_file = data_file
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
    
    def load_tasks(self):
        """从JSON文件加载任务"""
        import json
        import os
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data.get('tasks', []):
                        task = Task(**task_data)
                        # 转换字符串时间为datetime对象
                        if isinstance(task.created_at, str):
                            task.created_at = datetime.fromisoformat(task.created_at)
                        if isinstance(task.updated_at, str):
                            task.updated_at = datetime.fromisoformat(task.updated_at)
                        if task.due_date and isinstance(task.due_date, str):
                            task.due_date = datetime.fromisoformat(task.due_date)
                        if task.completed_at and isinstance(task.completed_at, str):
                            task.completed_at = datetime.fromisoformat(task.completed_at)
                        self.tasks[task.id] = task
            except Exception as e:
                print(f"加载任务数据失败: {e}")
                self.tasks = {}
    
    def save_tasks(self):
        """保存任务到JSON文件"""
        import json
        
        try:
            data = {
                "tasks": [task.model_dump(mode='json') for task in self.tasks.values()],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务数据失败: {e}")
    
    def create_task(self, title: str, description: str = "", 
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   due_date: Optional[datetime] = None,
                   parent_id: Optional[str] = None) -> Task:
        """创建新任务"""
        import uuid
        
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            parent_id=parent_id
        )
        
        self.tasks[task_id] = task
        
        # 如果有父任务，添加到父任务的子任务列表
        if parent_id and parent_id in self.tasks:
            self.tasks[parent_id].add_subtask(task_id)
        
        self.save_tasks()
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """更新任务"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        self.save_tasks()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id not in self.tasks:
            return False
        
        # 删除所有子任务
        task = self.tasks[task_id]
        for subtask_id in task.subtask_ids:
            self.delete_task(subtask_id)
        
        # 从父任务的子任务列表中移除
        if task.parent_id and task.parent_id in self.tasks:
            parent_task = self.tasks[task.parent_id]
            if task_id in parent_task.subtask_ids:
                parent_task.subtask_ids.remove(task_id)
        
        del self.tasks[task_id]
        self.save_tasks()
        return True
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态获取任务"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """按优先级获取任务"""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def search_tasks(self, keyword: str) -> List[Task]:
        """搜索任务"""
        keyword = keyword.lower()
        return [task for task in self.tasks.values() 
                if keyword in task.title.lower() or keyword in task.description.lower()]
    
    def get_task_tree(self, task_id: str) -> Dict[str, Any]:
        """获取任务树结构"""
        if task_id not in self.tasks:
            return {}
        
        task = self.tasks[task_id]
        return {
            "task": task,
            "subtasks": [self.get_task_tree(subtask_id) for subtask_id in task.subtask_ids]
        }