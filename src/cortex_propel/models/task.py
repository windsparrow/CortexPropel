from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Task model for CortexPropel."""
    
    id: str = Field(..., description="Unique identifier for the task")
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current status of the task")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Priority level of the task")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    actual_duration: Optional[int] = Field(None, description="Actual time spent in minutes")
    parent_id: Optional[str] = Field(None, description="ID of the parent task")
    subtasks: List[str] = Field(default_factory=list, description="List of subtask IDs")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    dependencies: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")
    resources: List[str] = Field(default_factory=list, description="Resources needed for the task")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage (0-100)")
    notes: Optional[str] = Field(None, description="Additional notes about the task")
    
    @validator('updated_at', always=True)
    def update_timestamp(cls, v, values):
        """Always update the timestamp when the model is updated."""
        return datetime.now()
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_subtask(self, subtask_id: str) -> None:
        """Add a subtask to this task."""
        if subtask_id not in self.subtasks:
            self.subtasks.append(subtask_id)
            self.updated_at = datetime.now()
    
    def remove_subtask(self, subtask_id: str) -> None:
        """Remove a subtask from this task."""
        if subtask_id in self.subtasks:
            self.subtasks.remove(subtask_id)
            self.updated_at = datetime.now()
    
    def add_dependency(self, dependency_id: str) -> None:
        """Add a dependency to this task."""
        if dependency_id not in self.dependencies:
            self.dependencies.append(dependency_id)
            self.updated_at = datetime.now()
    
    def remove_dependency(self, dependency_id: str) -> None:
        """Remove a dependency from this task."""
        if dependency_id in self.dependencies:
            self.dependencies.remove(dependency_id)
            self.updated_at = datetime.now()
    
    def update_progress(self, progress: int) -> None:
        """Update the progress of the task."""
        if 0 <= progress <= 100:
            self.progress = progress
            self.updated_at = datetime.now()
            
            # Auto-update status based on progress
            if progress == 100 and self.status != TaskStatus.COMPLETED:
                self.status = TaskStatus.COMPLETED
            elif 0 < progress < 100 and self.status == TaskStatus.PENDING:
                self.status = TaskStatus.IN_PROGRESS
    
    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.progress = 100
        self.updated_at = datetime.now()
    
    def mark_in_progress(self) -> None:
        """Mark the task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        if self.progress == 0:
            self.progress = 10  # Set initial progress
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create a task from a dictionary."""
        return cls(**data)