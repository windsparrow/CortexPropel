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
    You are a smart personal assistant that helps users manage tasks, record information, and track progress.
    
    Current Task Tree:
    {current_task_tree}
    
    User's Request:
    {user_input}
    
    Your Role:
    You help users with:
    1. **Task Management**: Create, update, and organize tasks and subtasks
    2. **Information Recording**: Log data entries like daily weight, expenses, notes, ideas, etc.
    3. **Progress Tracking**: Track project milestones, habit records, learning progress, etc.
    
    Understanding User Intent:
    - If the user wants to create a plan or project, create a parent task with subtasks
    - If the user wants to log data / information (like "今天体重65kg"), add it as a subtask under the relevant parent
    - If no suitable parent exists, intelligently create one or use "root"
    - If the user mentions a task name, find the matching task by title similarity
    - If the user wants to update status (完成/进行中), update that task
    
    Instructions:
    1. Analyze the current task tree and understand the user's intent
    2. Generate the minimum operations needed (add, update, or delete)
    3. Return ONLY the operations, NOT the entire task tree
    4. Choose appropriate parent_id to organize information logically
    5. Use descriptive titles and include any data/info in the description field
    
    Operation Types:
    - "add": Add a new task/record under a parent node (requires parent_id)
    - "update": Update an existing task's fields (requires task id)
    - "delete": Delete a task and its subtasks (requires task id)
    
    Output Format (JSON only, no other text):
    {{
      "operations": [
        {{
          "operation": "add",
          "parent_id": "parent-task-id-or-root",
          "task": {{
            "title": "Task or Record Title",
            "description": "Detailed description, data values, notes, or any info to remember",
            "status": "pending"
          }}
        }},
        {{
          "operation": "update",
          "task": {{
            "id": "existing-task-id",
            "status": "completed",
            "description": "Updated info"
          }}
        }},
        {{
          "operation": "delete",
          "task": {{
            "id": "task-id-to-delete"
          }}
        }}
      ],
      "message": "A friendly message describing what was done (in Chinese)"
    }}
    
    Important Rules:
    - Use "root" as parent_id for top-level items
    - Only output valid JSON, no markdown or extra text
    - Always include a helpful message in Chinese
    - Be smart about organizing: group related items under appropriate parents
    - For data logging (like weight), include the date and value in description
    - If request is unclear, ask for clarification in the message with empty operations
    """

# Create a global config instance
config = Config()
