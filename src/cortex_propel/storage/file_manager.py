from typing import Dict, List, Any, Optional
from pathlib import Path

from ..models.task import Task, TaskStatus, TaskPriority
from ..models.project import Project
from .json_storage import JSONStorage


class FileManager:
    """High-level file management for CortexPropel."""
    
    def __init__(self, data_dir: str = "~/.cortex_propel"):
        """Initialize the file manager.
        
        Args:
            data_dir: Directory to store data files
        """
        self.storage = JSONStorage(data_dir)
        self._default_project_id = "personal"
    
    def save_task(self, task: Task, project_id: Optional[str] = None) -> None:
        """Save a task to storage.
        
        Args:
            task: The task to save
            project_id: Project ID (defaults to "personal")
        """
        if project_id is None:
            project_id = self._default_project_id
        
        self.storage.save_model(task, "task", task.id, project_id)
    
    def load_task(self, task_id: str, project_id: Optional[str] = None) -> Optional[Task]:
        """Load a task from storage.
        
        Args:
            task_id: ID of the task to load
            project_id: Project ID (defaults to "personal")
            
        Returns:
            The loaded task or None if not found
        """
        if project_id is None:
            project_id = self._default_project_id
            
        return self.storage.load_model(Task, "task", task_id, project_id)
    
    def delete_task(self, task_id: str, project_id: Optional[str] = None) -> bool:
        """Delete a task from storage.
        
        Args:
            task_id: ID of the task to delete
            project_id: Project ID (defaults to "personal")
            
        Returns:
            True if deleted, False if not found
        """
        if project_id is None:
            project_id = self._default_project_id
            
        return self.storage.delete_model("task", task_id, project_id)
    
    def list_tasks(self, project_id: Optional[str] = None) -> List[str]:
        """List all task IDs.
        
        Args:
            project_id: Project ID (defaults to "personal")
            
        Returns:
            List of task IDs
        """
        if project_id is None:
            project_id = self._default_project_id
            
        return self.storage.list_models("task", project_id)
    
    def save_project(self, project: Project) -> None:
        """Save a project to storage.
        
        Args:
            project: The project to save
        """
        self.storage.save_model(project, "project", project.id)
    
    def create_project(self, project_id: str, name: str, description: str = "") -> Project:
        """Create a new project.
        
        Args:
            project_id: ID of the project
            name: Name of the project
            description: Description of the project
            
        Returns:
            The created project
        """
        project = Project(
            id=project_id,
            name=name,
            description=description
        )
        self.save_project(project)
        return project
    
    def load_project(self, project_id: str) -> Optional[Project]:
        """Load a project from storage.
        
        Args:
            project_id: ID of the project to load
            
        Returns:
            The loaded project or None if not found
        """
        return self.storage.load_model(Project, "project", project_id)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project from storage.
        
        Args:
            project_id: ID of the project to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.storage.delete_model("project", project_id)
    
    def list_projects(self) -> List[str]:
        """List all project IDs.
        
        Returns:
            List of project IDs
        """
        return self.storage.list_models("project")
    
    def get_tasks_by_status(self, status: TaskStatus, project_id: Optional[str] = None) -> List[Task]:
        """Get all tasks with a specific status.
        
        Args:
            status: The status to filter by
            project_id: Project ID (defaults to "personal")
            
        Returns:
            List of tasks with the specified status
        """
        if project_id is None:
            project_id = self._default_project_id
            
        task_ids = self.list_tasks(project_id)
        tasks = []
        
        for task_id in task_ids:
            task = self.load_task(task_id, project_id)
            if task and task.status == status:
                tasks.append(task)
                
        return tasks
    
    def get_tasks_by_priority(self, priority: TaskPriority, project_id: Optional[str] = None) -> List[Task]:
        """Get all tasks with a specific priority.
        
        Args:
            priority: The priority to filter by
            project_id: Project ID (defaults to "personal")
            
        Returns:
            List of tasks with the specified priority
        """
        if project_id is None:
            project_id = self._default_project_id
            
        task_ids = self.list_tasks(project_id)
        tasks = []
        
        for task_id in task_ids:
            task = self.load_task(task_id, project_id)
            if task and task.priority == priority:
                tasks.append(task)
                
        return tasks
    
    def search_tasks(self, query: str, project_id: Optional[str] = None) -> List[Task]:
        """Search for tasks by title or description.
        
        Args:
            query: Search query
            project_id: Project ID (defaults to "personal")
            
        Returns:
            List of tasks matching the query
        """
        if project_id is None:
            project_id = self._default_project_id
            
        task_ids = self.list_tasks(project_id)
        tasks = []
        query_lower = query.lower()
        
        for task_id in task_ids:
            task = self.load_task(task_id, project_id)
            if task:
                title_match = query_lower in task.title.lower()
                desc_match = task.description and query_lower in task.description.lower()
                tags_match = any(query_lower in tag.lower() for tag in task.tags)
                
                if title_match or desc_match or tags_match:
                    tasks.append(task)
                    
        return tasks
    
    def get_task_hierarchy(self, task_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get the full hierarchy of a task (parent, subtasks, dependencies).
        
        Args:
            task_id: ID of the task
            project_id: Project ID (defaults to "personal")
            
        Returns:
            Dictionary containing the task hierarchy
        """
        if project_id is None:
            project_id = self._default_project_id
            
        task = self.load_task(task_id, project_id)
        if not task:
            return {}
            
        result = {
            "task": task,
            "parent": None,
            "subtasks": [],
            "dependencies": [],
            "dependents": []
        }
        
        # Get parent task
        if task.parent_id:
            result["parent"] = self.load_task(task.parent_id, project_id)
        
        # Get subtasks
        for subtask_id in task.subtasks:
            subtask = self.load_task(subtask_id, project_id)
            if subtask:
                result["subtasks"].append(subtask)
        
        # Get dependencies
        for dep_id in task.dependencies:
            dep_task = self.load_task(dep_id, project_id)
            if dep_task:
                result["dependencies"].append(dep_task)
        
        # Get dependents (tasks that depend on this task)
        all_task_ids = self.list_tasks(project_id)
        for other_task_id in all_task_ids:
            if other_task_id == task_id:
                continue
                
            other_task = self.load_task(other_task_id, project_id)
            if other_task and task_id in other_task.dependencies:
                result["dependents"].append(other_task)
                
        return result
    
    def save_config(self, config: Dict[str, Any], config_name: str = "settings") -> None:
        """Save configuration.
        
        Args:
            config: Configuration dictionary
            config_name: Name of the configuration
        """
        self.storage.save_config(config, config_name)
    
    def load_config(self, config_name: str = "settings") -> Dict[str, Any]:
        """Load configuration.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Configuration dictionary
        """
        return self.storage.load_config(config_name)
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> None:
        """Clean up old backup files.
        
        Args:
            days_to_keep: Number of days to keep backups
        """
        self.storage.cleanup_old_backups(days_to_keep)