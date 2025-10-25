
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime, date

class TaskStatus(str, Enum):
    """
    Enum for the status of a task.
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    """
    Enum for the priority of a task.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    """
    Represents a task in the task management system.
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    progress: int = Field(default=0, ge=0, le=100)  # Progress percentage (0-100)
    sub_tasks: List['Task'] = []
    parent_id: Optional[UUID] = None

    def update_progress(self):
        """
        Update the task progress based on sub-tasks.
        """
        if not self.sub_tasks:
            return
        
        total_progress = sum(task.progress for task in self.sub_tasks)
        self.progress = total_progress // len(self.sub_tasks)
        
        # Update status based on progress
        if self.progress == 0:
            self.status = TaskStatus.TODO
        elif self.progress == 100:
            self.status = TaskStatus.DONE
        else:
            self.status = TaskStatus.IN_PROGRESS
        
        self.updated_at = datetime.now()

# Update the forward reference
Task.update_forward_refs()
