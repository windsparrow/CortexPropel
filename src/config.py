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
    You are a task management assistant. Your job is to help users manage their tasks by generating operation instructions.
    
    Current Task Tree:
    {current_task_tree}
    
    User's Request:
    {user_input}
    
    Instructions:
    1. Analyze the current task tree and the user's request
    2. Determine what operations are needed (add, update, or delete tasks)
    3. Return ONLY the operations needed, NOT the entire task tree
    4. Each operation must include the operation type and affected task data
    5. For "add" operations, you MUST include "parent_id" to specify where to add the new task
    6. For "update" operations, include only the fields that need to be changed
    7. For "delete" operations, only the task "id" is required
    
    Operation Types:
    - "add": Add a new task under a parent node (requires parent_id)
    - "update": Update an existing task's fields (requires task id)
    - "delete": Delete a task and its subtasks (requires task id)
    
    Output Format (JSON only, no other text):
    {{
      "operations": [
        {{
          "operation": "add",
          "parent_id": "parent-task-id-or-root",
          "task": {{
            "title": "New Task Title",
            "description": "Task description",
            "status": "pending"
          }}
        }},
        {{
          "operation": "update",
          "task": {{
            "id": "existing-task-id",
            "status": "completed",
            "title": "Updated Title"
          }}
        }},
        {{
          "operation": "delete",
          "task": {{
            "id": "task-id-to-delete"
          }}
        }}
      ],
      "message": "Brief description of what was done"
    }}
    
    Important Rules:
    - Use "root" as parent_id to add tasks at the top level
    - Only output valid JSON, no markdown or explanations
    - Include a helpful message field to describe the operations
    - If the user's request is unclear, ask for clarification in the message field with empty operations
    """

# Create a global config instance
config = Config()
