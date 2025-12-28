import json
import os
import uuid
import re
from typing import Dict, Any, Optional, Set, List

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
        
        # Assign UUIDs to new tasks by comparing with existing tasks in database
        updated_tree = self._assign_uuids_to_new_tasks(updated_tree)
        
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
        Reset the task tree to its initial state and clear the database.
        
        Returns:
            The new initial task tree as a dictionary
        """
        # Reset task tree file
        initial_tree = self._initialize_task_tree()
        self.save_task_tree(initial_tree)
        
        # Clear all tasks from database (except root)
        try:
            all_tasks = self.db.get_all_tasks()
            for task in all_tasks:
                if task['id'] != 'root':  # Don't delete the root task
                    self.db.delete_task(task['id'])
            print("✓ Database reset - all tasks cleared")
        except Exception as e:
            print(f"Warning: Could not reset database: {e}")
        
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
    
    def _is_valid_uuid(self, task_id: str) -> bool:
        """
        Check if a string is a valid UUID.
        
        Args:
            task_id: The ID to check
            
        Returns:
            True if valid UUID, False otherwise
        """
        if not task_id or task_id == "root":
            return True
        
        try:
            uuid.UUID(task_id)
            return True
        except (ValueError, TypeError):
            return False
    
    def _extract_all_task_ids(self, task_tree: Dict[str, Any]) -> Set[str]:
        """
        Extract all task IDs from a task tree recursively.
        
        Args:
            task_tree: The task tree to extract IDs from
            
        Returns:
            Set of all task IDs in the tree
        """
        task_ids = set()
        
        def _extract_from_node(node: Dict[str, Any]):
            if 'id' in node and node['id'] != 'root':
                task_ids.add(node['id'])
            
            # Process subtasks recursively
            for subtask in node.get('subtasks', []):
                _extract_from_node(subtask)
        
        _extract_from_node(task_tree)
        return task_ids
    
    def _get_existing_task_ids_from_db(self) -> Set[str]:
        """
        Get all existing task IDs from the database.
        
        Returns:
            Set of existing task IDs
        """
        try:
            all_tasks = self.db.get_all_tasks()
            return {task['id'] for task in all_tasks if task['id'] != 'root'}
        except Exception as e:
            print(f"Error getting existing task IDs from database: {e}")
            return set()
    
    def _identify_new_tasks(self, current_tree: Dict[str, Any], new_tree: Dict[str, Any]) -> Set[str]:
        """
        Identify new tasks by comparing current tree with new tree and database.
        
        Args:
            current_tree: Current task tree
            new_tree: New task tree from LLM
            
        Returns:
            Set of IDs for new tasks that need UUID assignment
        """
        # Get existing IDs from current tree
        current_ids = self._extract_all_task_ids(current_tree)
        
        # Get existing IDs from database
        db_ids = self._get_existing_task_ids_from_db()
        
        # Combine all existing IDs
        all_existing_ids = current_ids.union(db_ids)
        
        # Get all IDs from new tree
        new_ids = self._extract_all_task_ids(new_tree)
        
        # New tasks are those in new_tree but not in existing IDs
        new_task_ids = new_ids - all_existing_ids
        
        # Also include tasks with non-UUID IDs that should be converted
        non_uuid_ids = {task_id for task_id in new_ids if not self._is_valid_uuid(task_id)}
        
        return new_task_ids.union(non_uuid_ids)
    
    def _assign_uuids_to_new_tasks(self, task_tree: Dict[str, Any], new_task_ids: Set[str] = None) -> Dict[str, Any]:
        """
        Assign UUIDs to new tasks in the task tree.
        
        Args:
            task_tree: The task tree to process
            new_task_ids: Set of IDs that should be assigned new UUIDs. 
                         If None, will identify new tasks automatically.
                         
        Returns:
            Processed task tree with UUIDs assigned to new tasks
        """
        if new_task_ids is None:
            # If no specific IDs provided, identify new tasks by comparing with database
            current_tree = self.load_task_tree()
            new_task_ids = self._identify_new_tasks(current_tree, task_tree)
        
        # Create a mapping of old IDs to new UUIDs for tasks that need conversion
        id_mapping = {}
        
        def _process_node(node: Dict[str, Any]) -> Dict[str, Any]:
            """Process a single node and its subtasks."""
            processed_node = node.copy()
            
            # Assign new UUID if this is a new task or has invalid UUID
            task_id = node.get('id')
            if task_id and task_id != 'root' and (task_id in new_task_ids or not self._is_valid_uuid(task_id)):
                # Generate new UUID and store mapping
                new_uuid = str(uuid.uuid4())
                id_mapping[task_id] = new_uuid
                processed_node['id'] = new_uuid
            
            # Process subtasks
            if 'subtasks' in node:
                processed_node['subtasks'] = [_process_node(subtask) for subtask in node['subtasks']]
            
            return processed_node
        
        result = _process_node(task_tree)
        
        # If any IDs were changed, we need to handle the database updates
        if id_mapping:
            self._handle_id_changes_in_database(id_mapping)
        
        return result
    
    def _handle_id_changes_in_database(self, id_mapping: Dict[str, str]) -> None:
        """
        Handle ID changes in the database when tasks get new UUIDs.
        
        Args:
            id_mapping: Dictionary mapping old IDs to new UUIDs
        """
        try:
            for old_id, new_id in id_mapping.items():
                # Check if task with old ID exists in database
                existing_task = self.db.get_task(old_id)
                if existing_task:
                    # Create new task with new UUID
                    existing_task['id'] = new_id
                    self.db.create_or_update_task(existing_task, {})
                    
                    # Delete the old task
                    self.db.delete_task(old_id)
                    
                    print(f"✓ Updated task ID: {old_id} → {new_id}")
        except Exception as e:
            print(f"Error handling ID changes in database: {e}")