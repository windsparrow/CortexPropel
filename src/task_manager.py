import json
import os

# Handle imports for both package and standalone execution
try:
    from .config import config
    from .llm_client import LLMClient
except ImportError:
    # Standalone execution
    from config import config
    from llm_client import LLMClient

class TaskManager:
    def __init__(self):
        self.llm_client = LLMClient()
        self.task_tree_file = config.TASK_TREE_FILE
        
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
        Save the task tree to the JSON file.
        
        Args:
            task_tree: The task tree to save as a dictionary
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.task_tree_file), exist_ok=True)
            
            with open(self.task_tree_file, "w", encoding="utf-8") as f:
                json.dump(task_tree, f, ensure_ascii=False, indent=2)
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
        
        # Save updated task tree
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
