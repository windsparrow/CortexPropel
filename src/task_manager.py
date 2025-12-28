import json
import os
from typing import Dict, Any, Optional

# Handle imports for both package and standalone execution
try:
    from .config import config
    from .llm_client import LLMClient
    from .database import TaskDatabase
except ImportError:
    # Standalone execution
    from config import config
    from llm_client import LLMClient
    from database import TaskDatabase


class TaskManager:
    def __init__(self):
        self.llm_client = LLMClient()
        self.task_tree_file = config.TASK_TREE_FILE
        self.db = TaskDatabase()  # Initialize database
    
    def _initialize_task_tree(self) -> dict:
        """
        Initialize a new task tree with root node.
        
        Returns:
            The initial task tree as a dictionary
        """
        return {
            "id": "root",
            "title": "Root Task",
            "description": "Main project task",
            "status": "pending",
            "created_at": "2025-12-27T10:00:00Z",
            "updated_at": "2025-12-27T10:00:00Z",
            "subtasks": []
        }
    
    def load_task_tree(self) -> dict:
        """
        Load the task tree from the JSON file.
        
        Returns:
            The task tree as a dictionary
        """
        try:
            if os.path.exists(self.task_tree_file):
                with open(self.task_tree_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                # Initialize a new task tree if file doesn't exist
                initial_tree = self._initialize_task_tree()
                self.save_task_tree(initial_tree)
                return initial_tree
        except json.JSONDecodeError as e:
            print(f"Error loading task tree: {e}")
            # Reinitialize if file is corrupted
            initial_tree = self._initialize_task_tree()
            self.save_task_tree(initial_tree)
            return initial_tree
    
    def save_task_tree(self, task_tree: dict) -> None:
        """
        Save the task tree to the JSON file and sync to database.
        
        Args:
            task_tree: The task tree to save as a dictionary
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.task_tree_file), exist_ok=True)
            
            with open(self.task_tree_file, "w", encoding="utf-8") as f:
                json.dump(task_tree, f, ensure_ascii=False, indent=2)
            
            # Sync to database
            self.db.sync_from_task_tree(task_tree)
            
        except IOError as e:
            print(f"Error saving task tree: {e}")
    
    def process_user_input(self, user_input: str) -> dict:
        """
        Process user input and update the task tree.
        
        Args:
            user_input: The user's new task request
            
        Returns:
            The updated task tree as a dictionary
        """
        # Load current task tree
        current_tree = self.load_task_tree()
        
        # Process input using LLM
        updated_tree = self.llm_client.process_task_input(current_tree, user_input)
        
        # Save updated task tree (this will also sync to database)
        self.save_task_tree(updated_tree)
        
        return updated_tree
    
    def get_task_tree(self) -> dict:
        """
        Get the current task tree.
        
        Returns:
            The current task tree as a dictionary
        """
        return self.load_task_tree()
    
    def reset_task_tree(self) -> dict:
        """
        Reset the task tree to its initial state.
        
        Returns:
            The new initial task tree as a dictionary
        """
        initial_tree = self._initialize_task_tree()
        self.save_task_tree(initial_tree)
        return initial_tree
    
    # Database management methods
    def get_task_metadata(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task metadata from database.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task metadata or None if not found
        """
        return self.db.get_task(task_id)
    
    def get_all_tasks_metadata(self) -> list:
        """
        Get all tasks metadata from database.
        
        Returns:
            List of all task metadata
        """
        return self.db.get_all_tasks()
    
    def update_task_metadata(self, task_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update task metadata.
        
        Args:
            task_id: The task ID
            metadata: Dictionary of metadata fields to update
            
        Returns:
            Success status
        """
        # Ensure task_id is included in the metadata
        metadata['id'] = task_id
        return self.db.create_or_update_task(metadata, {})
    
    def update_task_field(self, task_id: str, field: str, value: Any) -> bool:
        """
        Update a specific field of task metadata.
        
        Args:
            task_id: The task ID
            field: Field name to update
            value: New value
            
        Returns:
            Success status
        """
        return self.db.update_task_field(task_id, field, value)
    
    def delete_task_metadata(self, task_id: str) -> bool:
        """
        Delete task metadata from database.
        
        Args:
            task_id: The task ID
            
        Returns:
            Success status
        """
        return self.db.delete_task(task_id)
    
    def sync_task_tree_to_db(self) -> bool:
        """
        Manually sync current task tree to database.
        
        Returns:
            Success status
        """
        current_tree = self.load_task_tree()
        return self.db.sync_from_task_tree(current_tree)