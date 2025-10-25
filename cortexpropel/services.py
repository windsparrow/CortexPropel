
import os
import json
from typing import Dict, List
from datetime import datetime, date, timedelta
from litellm import completion
from .models import Task, TaskStatus, TaskPriority
from .database import read_tasks, write_tasks, get_task_by_id, update_task, get_tasks_by_status, get_overdue_tasks, get_tasks_by_priority

# Set the deepseek API key from environment variables
# Make sure you have DEEPSEEK_API_KEY set in your environment
# os.environ["DEEPSEEK_API_KEY"] = "your_deepseek_api_key"

def create_task_from_natural_language(user_input: str) -> Task:
    """
    Creates a task from a natural language user input by using an LLM to parse it.

    Args:
        user_input: The natural language input from the user.

    Returns:
        The created task.
    """
    prompt = f"""
    Parse the following user input to create a task. Extract the task name, description, due date, and priority.
    The user input is: "{user_input}"
    Return a JSON object with the following keys: "name", "description", "due_date", "priority".
    "name" should be a concise summary of the task.
    "description" should be a more detailed explanation.
    "due_date" should be in a string format like YYYY-MM-DD, if specified.
    "priority" should be one of "low", "medium", or "high". If not specified, default to "medium".
    Example:
    User input: "I need to finish the report for the Q3 review by next Friday, which is 2025-11-07. This is high priority."
    {{
        "name": "Finish Q3 review report",
        "description": "Complete the report for the third-quarter review.",
        "due_date": "2025-11-07",
        "priority": "high"
    }}
    """

    # Call the LLM to parse the user input
    # In a real scenario, you would have error handling and retry logic here.
    response = completion(
        model="deepseek/deepseek-coder",
        messages=[{"content": prompt, "role": "user"}],
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
    )

    # Extract the JSON from the response
    # This is a simplification. A more robust solution would handle cases where the response is not valid JSON.
    try:
        # The response content is a string that contains a JSON object.
        response_content = response.choices[0].message.content
        # Find the start and end of the JSON block
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        json_str = response_content[json_start:json_end]
        task_data = json.loads(json_str)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing LLM response: {e}")
        # Return a default task or raise an exception
        raise ValueError("Failed to parse task from user input.")

    # Parse priority
    priority_str = task_data.get("priority", "medium").lower()
    priority = TaskPriority.MEDIUM
    if priority_str == "low":
        priority = TaskPriority.LOW
    elif priority_str == "high":
        priority = TaskPriority.HIGH

    # Parse due date
    due_date = None
    if task_data.get("due_date"):
        try:
            due_date = date.fromisoformat(task_data["due_date"])
        except ValueError:
            print(f"Invalid due date format: {task_data['due_date']}. Expected YYYY-MM-DD.")

    # Create a new task object
    new_task = Task(
        name=task_data.get("name"),
        description=task_data.get("description"),
        due_date=due_date,
        priority=priority,
    )

    # Read the existing tasks, add the new one, and write them back
    tasks = read_tasks()
    tasks.append(new_task)
    write_tasks(tasks)

    return new_task

def check_task_execution() -> Dict[str, List[Task]]:
    """
    Checks the execution status of all tasks and categorizes them.

    Returns:
        A dictionary with task categories as keys and lists of tasks as values.
    """
    overdue_tasks = get_overdue_tasks()
    in_progress_tasks = get_tasks_by_status(TaskStatus.IN_PROGRESS)
    todo_tasks = get_tasks_by_status(TaskStatus.TODO)
    
    # Get high priority tasks that are not done
    high_priority_tasks = get_tasks_by_priority(TaskPriority.HIGH)
    high_priority_tasks = [task for task in high_priority_tasks if task.status != TaskStatus.DONE]
    
    return {
        "overdue": overdue_tasks,
        "in_progress": in_progress_tasks,
        "todo": todo_tasks,
        "high_priority": high_priority_tasks
    }

def schedule_tasks() -> List[Task]:
    """
    Schedules tasks based on priority and due date.

    Returns:
        A list of tasks sorted by priority and due date.
    """
    tasks = read_tasks()
    
    # Filter out completed tasks
    incomplete_tasks = [task for task in tasks if task.status != TaskStatus.DONE]
    
    # Sort tasks by priority (high to low) and then by due date (earliest to latest)
    priority_order = {TaskPriority.HIGH: 0, TaskPriority.MEDIUM: 1, TaskPriority.LOW: 2}
    
    # Sort by priority first, then by due date
    incomplete_tasks.sort(key=lambda task: (
        priority_order[task.priority],
        task.due_date if task.due_date else date.max
    ))
    
    return incomplete_tasks

def update_task_progress(task_id: str, progress: int) -> bool:
    """
    Updates the progress of a task.

    Args:
        task_id: The ID of the task to update.
        progress: The progress percentage (0-100).

    Returns:
        True if the task was updated successfully, False otherwise.
    """
    if progress < 0 or progress > 100:
        return False
    
    # Determine the status based on progress
    status = TaskStatus.TODO
    if progress > 0 and progress < 100:
        status = TaskStatus.IN_PROGRESS
    elif progress == 100:
        status = TaskStatus.DONE
    
    return update_task(task_id, {"progress": progress, "status": status})

def generate_task_report() -> Dict[str, int]:
    """
    Generates a summary report of tasks.

    Returns:
        A dictionary with task statistics.
    """
    tasks = read_tasks()
    
    total_tasks = len(tasks)
    completed_tasks = len([task for task in tasks if task.status == TaskStatus.DONE])
    in_progress_tasks = len([task for task in tasks if task.status == TaskStatus.IN_PROGRESS])
    todo_tasks = len([task for task in tasks if task.status == TaskStatus.TODO])
    overdue_tasks = len(get_overdue_tasks())
    
    # Calculate average progress
    if total_tasks > 0:
        avg_progress = sum(task.progress for task in tasks) / total_tasks
    else:
        avg_progress = 0
    
    return {
        "total": total_tasks,
        "completed": completed_tasks,
        "in_progress": in_progress_tasks,
        "todo": todo_tasks,
        "overdue": overdue_tasks,
        "avg_progress": round(avg_progress, 1)
    }
