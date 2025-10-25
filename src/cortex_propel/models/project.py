from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class WorkingHours(BaseModel):
    """Working hours configuration."""
    start_time: str = Field("09:00", description="Start time in HH:MM format")
    end_time: str = Field("17:00", description="End time in HH:MM format")
    weekdays: List[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5], 
                               description="Working days as integers [1-7] where 1 is Monday")
    
    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        """Validate time format."""
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
    
    @validator('weekdays')
    def validate_weekdays(cls, v):
        """Validate weekdays."""
        for day in v:
            if not 1 <= day <= 7:
                raise ValueError("Weekdays must be integers between 1 and 7")
        return v


class TaskDefaults(BaseModel):
    """Default settings for new tasks."""
    estimated_duration: int = Field(60, description="Default estimated duration in minutes")
    priority: str = Field("medium", description="Default priority level")


class ProjectSettings(BaseModel):
    """Project-specific settings."""
    default_priority: str = Field("medium", description="Default priority for tasks")
    working_hours: WorkingHours = Field(default_factory=WorkingHours, 
                                      description="Working hours configuration")
    task_defaults: TaskDefaults = Field(default_factory=TaskDefaults, 
                                      description="Default task settings")


class Project(BaseModel):
    """Project model for CortexPropel."""
    
    id: str = Field(..., description="Unique identifier for the project")
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Description of the project")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    tasks: List[str] = Field(default_factory=list, description="List of task IDs in this project")
    settings: ProjectSettings = Field(default_factory=ProjectSettings, 
                                    description="Project-specific settings")
    
    @validator('updated_at', always=True)
    def update_timestamp(cls, v, values):
        """Always update the timestamp when the model is updated."""
        return datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_task(self, task_id: str) -> None:
        """Add a task to this project."""
        if task_id not in self.tasks:
            self.tasks.append(task_id)
            self.updated_at = datetime.now()
    
    def remove_task(self, task_id: str) -> None:
        """Remove a task from this project."""
        if task_id in self.tasks:
            self.tasks.remove(task_id)
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the project to a dictionary."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        """Create a project from a dictionary."""
        return cls(**data)