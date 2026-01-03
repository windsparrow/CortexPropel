import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "bytedance_model")
    MODEL_API_KEY = os.getenv("MODEL_API_KEY", "")
    MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "")
    
    # Task Tree Configuration
    # Use absolute path to ensure we always use the project root data folder
    _PROJECT_ROOT = Path(__file__).parent.parent
    TASK_TREE_FILE = str(_PROJECT_ROOT / "data" / "task_tree.json")
    
    # LLM Configuration
    TEMPERATURE = 0.1
    MAX_TOKENS = 65536
    
    # Prompt Templates
    TASK_PROMPT_TEMPLATE = """
    You are a task management assistant. Your job is to help users organize their tasks into a hierarchical tree structure.
    
    Current Task Tree:
    {current_task_tree}
    
    User's New Task:
    {user_input}
    
    Instructions:
    1. Analyze the current task tree structure
    2. Understand the user's new task request
    3. Update the task tree by adding, modifying, or organizing tasks as appropriate
    4. Ensure the task tree remains a valid JSON structure with proper nesting
    5. Only output the complete updated task tree in JSON format, nothing else
    6. Each task must have: id, title, description, status, created_at, updated_at, and subtasks fields
    7. Generate unique IDs for new tasks
    8. Set appropriate status (pending, in_progress, completed) for tasks
    9. Update timestamps for modified tasks
    
    Output Format:
    {{"id": "root", "title": "Root Task", "description": "Main project task", "status": "pending", "created_at": "2025-12-27T10:00:00Z", "updated_at": "2025-12-27T10:00:00Z", "subtasks": [...]}}
    """

# Create a global config instance
config = Config()
