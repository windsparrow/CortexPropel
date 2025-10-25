
import json
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime, date
from .models import Task, TaskStatus, TaskPriority

TASKS_FILE = "tasks.json"

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            # Convert datetime and date objects to ISO format strings
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def read_tasks() -> List[Task]:
    """
    Reads tasks from the JSON file and returns them as a list of Task objects.
    """
    try:
        with open(TASKS_FILE, "r") as f:
            data = json.load(f)
            tasks = []
            for task_data in data:
                # Convert date strings back to date objects
                if task_data.get("due_date"):
                    task_data["due_date"] = date.fromisoformat(task_data["due_date"])
                
                # Convert datetime strings back to datetime objects
                if task_data.get("created_at"):
                    task_data["created_at"] = datetime.fromisoformat(task_data["created_at"])
                
                if task_data.get("updated_at"):
                    task_data["updated_at"] = datetime.fromisoformat(task_data["updated_at"])
                
                # Convert parent_id string back to UUID
                if task_data.get("parent_id"):
                    task_data["parent_id"] = UUID(task_data["parent_id"])
                
                tasks.append(Task(**task_data))
            return tasks
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_tasks(tasks: List[Task]):
    """
    Writes a list of Task objects to the JSON file.
    """
    with open(TASKS_FILE, "w") as f:
        json.dump([task.dict() for task in tasks], f, indent=4, cls=UUIDEncoder)

def get_task_by_id(task_id: str) -> Optional[Task]:
    """
    Finds a task by its ID.

    Args:
        task_id: The ID of the task to find.

    Returns:
        The task with the specified ID, or None if not found.
    """
    tasks = read_tasks()
    for task in tasks:
        if str(task.id) == task_id:
            return task
    return None

def update_task(task_id: str, updates: Dict) -> bool:
    """
    Updates a task with the given ID.

    Args:
        task_id: The ID of the task to update.
        updates: A dictionary of fields to update.

    Returns:
        True if the task was updated successfully, False otherwise.
    """
    tasks = read_tasks()
    for i, task in enumerate(tasks):
        if str(task.id) == task_id:
            # Update the task with the new values
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # Update the updated_at timestamp
            task.updated_at = datetime.now()
            
            # Save the updated tasks
            tasks[i] = task
            write_tasks(tasks)
            return True
    return False

def get_tasks_by_status(status: TaskStatus) -> List[Task]:
    """
    Gets all tasks with a specific status.

    Args:
        status: The status to filter by.

    Returns:
        A list of tasks with the specified status.
    """
    tasks = read_tasks()
    return [task for task in tasks if task.status == status]

def get_overdue_tasks() -> List[Task]:
    """
    Gets all tasks that are overdue.

    Returns:
        A list of overdue tasks.
    """
    tasks = read_tasks()
    today = date.today()
    return [task for task in tasks if task.due_date and task.due_date < today and task.status != TaskStatus.DONE]

def get_tasks_by_priority(priority: TaskPriority) -> List[Task]:
    """
    Gets all tasks with a specific priority.

    Args:
        priority: The priority to filter by.

    Returns:
        A list of tasks with the specified priority.
    """
    tasks = read_tasks()
    return [task for task in tasks if task.priority == priority]
