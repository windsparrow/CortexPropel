"""
任务数据模型
定义任务的基本属性和方法
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import uuid


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task:
    """任务类"""
    
    def __init__(
        self,
        title: str,
        description: str = "",
        status: TaskStatus = TaskStatus.PENDING,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: Optional[datetime] = None,
        parent_task_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        estimated_hours: Optional[float] = None,
        task_id: Optional[str] = None
    ):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.due_date = due_date
        self.completed_at = None
        self.parent_task_id = parent_task_id
        self.subtasks: List[str] = []
        self.tags = tags or []
        self.estimated_hours = estimated_hours
        self.actual_hours = None
        self.notes: List[Dict[str, Any]] = []
    
    def update_status(self, status: TaskStatus):
        """更新任务状态"""
        self.status = status
        self.updated_at = datetime.now()
        if status == TaskStatus.COMPLETED:
            self.completed_at = datetime.now()
    
    def add_subtask(self, subtask_id: str):
        """添加子任务"""
        if subtask_id not in self.subtasks:
            self.subtasks.append(subtask_id)
            self.updated_at = datetime.now()
    
    def remove_subtask(self, subtask_id: str):
        """移除子任务"""
        if subtask_id in self.subtasks:
            self.subtasks.remove(subtask_id)
            self.updated_at = datetime.now()
    
    def add_note(self, content: str):
        """添加笔记"""
        note = {
            "id": str(uuid.uuid4()),
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        self.notes.append(note)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """将任务转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "tags": self.tags,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建任务"""
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", TaskStatus.PENDING.value)),
            priority=TaskPriority(data.get("priority", TaskPriority.MEDIUM.value)),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            parent_task_id=data.get("parent_task_id"),
            tags=data.get("tags", []),
            estimated_hours=data.get("estimated_hours"),
            task_id=data.get("id")
        )
        
        task.created_at = datetime.fromisoformat(data["created_at"])
        task.updated_at = datetime.fromisoformat(data["updated_at"])
        task.completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        task.subtasks = data.get("subtasks", [])
        task.actual_hours = data.get("actual_hours")
        task.notes = data.get("notes", [])
        
        return task


class TaskManager:
    """任务管理器"""
    
    def __init__(self, data_file: str = "data/tasks.json"):
        self.data_file = data_file
        self.tasks: Dict[str, Task] = {}
        self.load_tasks()
    
    def load_tasks(self):
        """从文件加载任务"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    self.tasks[task.id] = task
        except FileNotFoundError:
            # 如果文件不存在，创建一个空的任务列表
            self.save_tasks()
    
    def save_tasks(self):
        """保存任务到文件"""
        data = {
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "metadata": {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }
        
        # 确保目录存在
        import os
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_task(self, task: Task) -> str:
        """添加任务"""
        self.tasks[task.id] = task
        self.save_tasks()
        return task.id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """更新任务"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id not in self.tasks:
            return False
        
        # 删除任务前，先将其从父任务的子任务列表中移除
        task = self.tasks[task_id]
        if task.parent_task_id and task.parent_task_id in self.tasks:
            self.tasks[task.parent_task_id].remove_subtask(task_id)
        
        # 删除所有子任务
        for subtask_id in task.subtasks[:]:
            self.delete_task(subtask_id)
        
        del self.tasks[task_id]
        self.save_tasks()
        return True
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """根据状态获取任务"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority: TaskPriority) -> List[Task]:
        """根据优先级获取任务"""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_root_tasks(self) -> List[Task]:
        """获取根任务（没有父任务的任务）"""
        return [task for task in self.tasks.values() if task.parent_task_id is None]
    
    def get_subtasks(self, parent_task_id: str) -> List[Task]:
        """获取子任务"""
        parent_task = self.get_task(parent_task_id)
        if not parent_task:
            return []
        
        return [self.tasks[subtask_id] for subtask_id in parent_task.subtasks if subtask_id in self.tasks]