from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

from ..models.task import Task, TaskStatus, TaskPriority
from ..storage.file_manager import FileManager


class TaskQueryEngine:
    """Advanced task query engine with complex filtering and sorting capabilities."""
    
    def __init__(self, file_manager: FileManager):
        """Initialize the task query engine.
        
        Args:
            file_manager: File manager for data access
        """
        self.file_manager = file_manager
    
    def query_tasks(self, project_id: str, query: str = None, 
                   status: TaskStatus = None, priority: TaskPriority = None,
                   tags: List[str] = None, due_before: datetime = None,
                   due_after: datetime = None, created_before: datetime = None,
                   created_after: datetime = None, parent_id: str = None,
                   has_subtasks: bool = None, sort_by: str = "created_at",
                   sort_order: str = "desc", limit: int = None) -> List[Task]:
        """Query tasks with advanced filtering options.
        
        Args:
            project_id: Project ID to query
            query: Natural language query string
            status: Filter by status
            priority: Filter by priority
            tags: Filter by tags (task must have all specified tags)
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            created_before: Filter tasks created before this date
            created_after: Filter tasks created after this date
            parent_id: Filter by parent task ID
            has_subtasks: Filter by whether task has subtasks
            sort_by: Field to sort by (created_at, updated_at, due_date, priority, progress)
            sort_order: Sort order (asc or desc)
            limit: Maximum number of results to return
            
        Returns:
            List of matching tasks
        """
        # Get all tasks for the project
        task_ids = self.file_manager.list_tasks(project_id)
        tasks = []
        
        for task_id in task_ids:
            task = self.file_manager.load_task(task_id, project_id)
            if task:
                tasks.append(task)
        
        # Apply filters
        filtered_tasks = []
        
        for task in tasks:
            # Status filter
            if status and task.status != status:
                continue
            
            # Priority filter
            if priority and task.priority != priority:
                continue
            
            # Tags filter
            if tags and not all(tag in task.tags for tag in tags):
                continue
            
            # Due date filters
            if due_before and (not task.due_date or task.due_date.date() > due_before):
                continue
            
            if due_after and (not task.due_date or task.due_date.date() < due_after):
                continue
            
            # Created date filters
            if created_before and task.created_at > created_before:
                continue
            
            if created_after and task.created_at < created_after:
                continue
            
            # Parent ID filter
            if parent_id and task.parent_id != parent_id:
                continue
            
            # Has subtasks filter
            if has_subtasks is not None:
                if has_subtasks and not task.subtasks:
                    continue
                if not has_subtasks and task.subtasks:
                    continue
            
            # Natural language query filter
            if query:
                if not self._matches_query(task, query):
                    continue
            
            # Task passed all filters
            filtered_tasks.append(task)
        
        # Sort tasks
        if sort_by == "created_at":
            filtered_tasks.sort(key=lambda t: t.created_at, reverse=(sort_order == "desc"))
        elif sort_by == "updated_at":
            filtered_tasks.sort(key=lambda t: t.updated_at, reverse=(sort_order == "desc"))
        elif sort_by == "due_date":
            # Tasks without due dates go to the end
            filtered_tasks.sort(
                key=lambda t: t.due_date or datetime.max, 
                reverse=(sort_order == "desc")
            )
        elif sort_by == "priority":
            # Sort by priority using the enum values
            priority_order = {
                TaskPriority.LOW.value: 0,
                TaskPriority.MEDIUM.value: 1,
                TaskPriority.HIGH.value: 2,
                TaskPriority.CRITICAL.value: 3
            }
            filtered_tasks.sort(
                key=lambda t: priority_order.get(t.priority, 0), 
                reverse=(sort_order == "desc")
            )
        elif sort_by == "progress":
            filtered_tasks.sort(
                key=lambda t: t.progress, 
                reverse=(sort_order == "desc")
            )
        
        # Apply limit
        if limit:
            filtered_tasks = filtered_tasks[:limit]
        
        return filtered_tasks
    
    def _matches_query(self, task: Task, query: str) -> bool:
        """Check if a task matches a natural language query.
        
        Args:
            task: Task to check
            query: Query string
            
        Returns:
            True if task matches the query
        """
        query = query.lower()
        
        # Check title
        if query in task.title.lower():
            return True
        
        # Check description
        if task.description and query in task.description.lower():
            return True
        
        # Check tags
        for tag in task.tags:
            if query in tag.lower():
                return True
        
        # Check for special query patterns
        if "overdue" in query and task.due_date and task.due_date.date() < datetime.now().date():
            return True
        
        if "due today" in query and task.due_date and task.due_date.date() == datetime.now().date():
            return True
        
        if "due this week" in query and task.due_date:
            today = datetime.now().date()
            week_end = today + timedelta(days=7)
            if today <= task.due_date.date() <= week_end:
                return True
        
        if "no due date" in query and not task.due_date:
            return True
        
        return False
    
    def get_task_hierarchy(self, project_id: str) -> List[Dict[str, Any]]:
        """Get tasks organized in a hierarchy.
        
        Args:
            project_id: Project ID to query
            
        Returns:
            List of task dictionaries with subtasks nested
        """
        # Get all tasks
        task_ids = self.file_manager.list_tasks(project_id)
        tasks = {}
        
        for task_id in task_ids:
            task = self.file_manager.load_task(task_id, project_id)
            if task:
                tasks[task_id] = task
        
        # Build hierarchy
        root_tasks = []
        task_dict = {}
        
        # First pass: create task dictionaries
        for task_id, task in tasks.items():
            task_dict[task_id] = {
                "task": task,
                "subtasks": []
            }
        
        # Second pass: build hierarchy
        for task_id, task in tasks.items():
            if task.parent_id and task.parent_id in task_dict:
                # This is a subtask
                task_dict[task.parent_id]["subtasks"].append(task_dict[task_id])
            else:
                # This is a root task
                root_tasks.append(task_dict[task_id])
        
        return root_tasks
    
    def get_task_statistics(self, project_id: str) -> Dict[str, Any]:
        """Get statistics about tasks in a project.
        
        Args:
            project_id: Project ID to analyze
            
        Returns:
            Dictionary with task statistics
        """
        # Get all tasks
        task_ids = self.file_manager.list_tasks(project_id)
        tasks = []
        
        for task_id in task_ids:
            task = self.file_manager.load_task(task_id, project_id)
            if task:
                tasks.append(task)
        
        # Calculate statistics
        stats = {
            "total_tasks": len(tasks),
            "by_status": {},
            "by_priority": {},
            "with_due_date": 0,
            "overdue": 0,
            "due_today": 0,
            "due_this_week": 0,
            "average_progress": 0,
            "with_subtasks": 0,
            "subtasks": 0
        }
        
        total_progress = 0
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        
        for task in tasks:
            # Status statistics
            status_key = task.status
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1
            
            # Priority statistics
            priority_key = task.priority
            stats["by_priority"][priority_key] = stats["by_priority"].get(priority_key, 0) + 1
            
            # Due date statistics
            if task.due_date:
                stats["with_due_date"] += 1
                due_date = task.due_date.date()
                
                if due_date < today and task.status != TaskStatus.COMPLETED:
                    stats["overdue"] += 1
                elif due_date == today:
                    stats["due_today"] += 1
                elif today <= due_date <= week_end:
                    stats["due_this_week"] += 1
            
            # Progress statistics
            total_progress += task.progress
            
            # Subtask statistics
            if task.subtasks:
                stats["with_subtasks"] += 1
                stats["subtasks"] += len(task.subtasks)
        
        # Calculate average progress
        if tasks:
            stats["average_progress"] = total_progress / len(tasks)
        
        return stats


class TaskStatusUpdater:
    """Advanced task status update engine with intelligent progress tracking."""
    
    def __init__(self, file_manager: FileManager):
        """Initialize the task status updater.
        
        Args:
            file_manager: File manager for data access
        """
        self.file_manager = file_manager
    
    def update_task_status(self, project_id: str, task_id: str, 
                          status: TaskStatus = None, progress: int = None,
                          auto_update_subtasks: bool = True,
                          auto_update_parent: bool = True) -> Tuple[Task, List[Task]]:
        """Update task status and optionally update related tasks.
        
        Args:
            project_id: Project ID
            task_id: Task ID to update
            status: New status
            progress: New progress (0-100)
            auto_update_subtasks: Whether to update subtasks when parent is updated
            auto_update_parent: Whether to update parent when subtasks are updated
            
        Returns:
            Tuple of (updated task, list of additionally updated tasks)
        """
        # Load the task
        task = self.file_manager.load_task(task_id, project_id)
        if not task:
            raise ValueError(f"Task {task_id} not found in project {project_id}")
        
        updated_tasks = []
        
        # Update status if provided
        if status:
            task.status = status
            
            # Auto-adjust progress based on status
            if status == TaskStatus.COMPLETED:
                task.progress = 100
            elif status == TaskStatus.IN_PROGRESS and task.progress == 0:
                task.progress = 10
            elif status == TaskStatus.PENDING:
                task.progress = 0
        
        # Update progress if provided
        if progress is not None:
            task.update_progress(progress)
        
        # Update timestamp
        task.updated_at = datetime.now()
        
        # Save the task
        self.file_manager.save_task(task, project_id)
        updated_tasks.append(task)
        
        # Auto-update subtasks if parent is completed
        if auto_update_subtasks and status == TaskStatus.COMPLETED and task.subtasks:
            for subtask_id in task.subtasks:
                subtask = self.file_manager.load_task(subtask_id, project_id)
                if subtask and subtask.status != TaskStatus.COMPLETED:
                    subtask.status = TaskStatus.COMPLETED
                    subtask.progress = 100
                    subtask.updated_at = datetime.now()
                    self.file_manager.save_task(subtask, project_id)
                    updated_tasks.append(subtask)
        
        # Auto-update parent if subtask is updated
        if auto_update_parent and task.parent_id:
            parent = self.file_manager.load_task(task.parent_id, project_id)
            if parent:
                # Get all subtasks
                subtasks = []
                for subtask_id in parent.subtasks:
                    subtask = self.file_manager.load_task(subtask_id, project_id)
                    if subtask:
                        subtasks.append(subtask)
                
                # Calculate parent progress based on subtasks
                if subtasks:
                    total_progress = sum(subtask.progress for subtask in subtasks)
                    parent_progress = total_progress / len(subtasks)
                    parent.update_progress(int(parent_progress))
                    
                    # Update parent status based on subtasks
                    all_completed = all(subtask.status == TaskStatus.COMPLETED for subtask in subtasks)
                    any_in_progress = any(subtask.status == TaskStatus.IN_PROGRESS for subtask in subtasks)
                    
                    if all_completed:
                        parent.status = TaskStatus.COMPLETED
                    elif any_in_progress:
                        parent.status = TaskStatus.IN_PROGRESS
                    
                    parent.updated_at = datetime.now()
                    self.file_manager.save_task(parent, project_id)
                    updated_tasks.append(parent)
        
        return task, updated_tasks
    
    def update_task_progress(self, project_id: str, task_id: str, progress: int) -> Tuple[Task, List[Task]]:
        """Update task progress and optionally update related tasks.
        
        Args:
            project_id: Project ID
            task_id: Task ID to update
            progress: New progress (0-100)
            
        Returns:
            Tuple of (updated task, list of additionally updated tasks)
        """
        return self.update_task_status(project_id, task_id, progress=progress)
    
    def bulk_update_priority(self, project_id: str, task_ids: List[str], priority: TaskPriority) -> List[Task]:
        """Update priority for multiple tasks.
        
        Args:
            project_id: Project ID
            task_ids: List of task IDs to update
            priority: New priority
            
        Returns:
            List of updated tasks
        """
        updated_tasks = []
        
        for task_id in task_ids:
            task = self.file_manager.load_task(task_id, project_id)
            if task:
                task.priority = priority
                task.updated_at = datetime.now()
                self.file_manager.save_task(task, project_id)
                updated_tasks.append(task)
        
        return updated_tasks
    
    def bulk_update_status(self, project_id: str, task_ids: List[str],
                          status: TaskStatus = None, progress: int = None) -> List[Task]:
        """Update status for multiple tasks.
        
        Args:
            project_id: Project ID
            task_ids: List of task IDs to update
            status: New status
            progress: New progress (0-100)
            
        Returns:
            List of updated tasks
        """
        updated_tasks = []
        
        for task_id in task_ids:
            try:
                task, additional = self.update_task_status(
                    project_id, task_id, status, progress,
                    auto_update_subtasks=False,  # Disable auto-update for bulk operations
                    auto_update_parent=False
                )
                updated_tasks.append(task)
                updated_tasks.extend(additional)
            except ValueError:
                # Skip tasks that don't exist
                continue
        
        return updated_tasks
    
    def get_suggested_next_actions(self, project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get suggested next actions based on task status and priorities.
        
        Args:
            project_id: Project ID
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested actions
        """
        # Get all tasks
        task_ids = self.file_manager.list_tasks(project_id)
        tasks = []
        
        for task_id in task_ids:
            task = self.file_manager.load_task(task_id, project_id)
            if task and task.status != TaskStatus.COMPLETED:
                tasks.append(task)
        
        suggestions = []
        today = datetime.now().date()
        
        # Sort tasks by priority and due date
        def task_score(task):
            score = 0
            
            # Higher priority gets higher score
            priority_order = {
                TaskPriority.LOW.value: 0,
                TaskPriority.MEDIUM.value: 1,
                TaskPriority.HIGH.value: 2,
                TaskPriority.CRITICAL.value: 3
            }
            score += priority_order.get(task.priority, 0) * 10
            
            # Overdue tasks get higher score
            if task.due_date:
                days_until_due = (task.due_date.date() - today).days
                if days_until_due < 0:
                    score += 50  # Overdue
                elif days_until_due == 0:
                    score += 30  # Due today
                elif days_until_due <= 3:
                    score += 20  # Due soon
            
            # In-progress tasks get a slight boost
            if task.status == TaskStatus.IN_PROGRESS:
                score += 5
            
            return score
        
        tasks.sort(key=task_score, reverse=True)
        
        # Generate suggestions
        for task in tasks[:limit]:
            suggestion = {
                "task": task,
                "action": "",
                "reason": ""
            }
            
            if task.status == TaskStatus.PENDING:
                suggestion["action"] = f"Start working on '{task.title}'"
                suggestion["reason"] = "This task is ready to begin"
            elif task.status == TaskStatus.IN_PROGRESS:
                suggestion["action"] = f"Continue working on '{task.title}'"
                suggestion["reason"] = f"This task is {task.progress}% complete"
            
            if task.due_date:
                days_until_due = (task.due_date.date() - today).days
                if days_until_due < 0:
                    suggestion["reason"] += f" (OVERDUE by {abs(days_until_due)} days)"
                elif days_until_due == 0:
                    suggestion["reason"] += " (DUE TODAY)"
                elif days_until_due <= 3:
                    suggestion["reason"] += f" (Due in {days_until_due} days)"
            
            suggestions.append(suggestion)
        
        return suggestions