import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .config import config


class TaskDatabase:
    """SQLite database manager for task metadata."""
    
    def __init__(self, db_path: str = "data/tasks.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database with task_metadata table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_metadata (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 1,
                    planned_start_time TEXT,
                    planned_end_time TEXT,
                    actual_start_time TEXT,
                    actual_end_time TEXT,
                    assigned_to TEXT,
                    created_by TEXT,
                    tags TEXT,
                    progress INTEGER DEFAULT 0,
                    estimated_hours REAL,
                    actual_hours REAL,
                    dependencies TEXT,
                    category TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    json_data TEXT
                )
            """)
            conn.commit()
    
    def create_or_update_task(self, task_data: Dict[str, Any], json_data: Dict[str, Any]) -> bool:
        """
        Create or update task metadata.
        
        Args:
            task_data: Task metadata fields
            json_data: Complete task JSON from task tree
            
        Returns:
            Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                
                # Check if task exists to get current values
                existing_task = None
                if task_data.get('id') or json_data.get('id'):
                    task_id = task_data.get('id') or json_data.get('id')
                    cursor = conn.execute("SELECT * FROM task_metadata WHERE id = ?", (task_id,))
                    existing_task = cursor.fetchone()
                
                if existing_task:
                    # Update existing task - use task_data values or existing values
                    merged_data = {
                        'id': task_id,
                        'title': task_data.get('title', existing_task['title']),
                        'description': task_data.get('description', existing_task['description']),
                        'status': task_data.get('status', existing_task['status']),
                        'priority': task_data.get('priority', existing_task['priority']),
                        'planned_start_time': task_data.get('planned_start_time', existing_task['planned_start_time']),
                        'planned_end_time': task_data.get('planned_end_time', existing_task['planned_end_time']),
                        'actual_start_time': task_data.get('actual_start_time', existing_task['actual_start_time']),
                        'actual_end_time': task_data.get('actual_end_time', existing_task['actual_end_time']),
                        'assigned_to': task_data.get('assigned_to', existing_task['assigned_to']),
                        'created_by': task_data.get('created_by', existing_task['created_by']),
                        'tags': json.dumps(task_data.get('tags', json.loads(existing_task['tags'] or '[]'))),
                        'progress': task_data.get('progress', existing_task['progress']),
                        'estimated_hours': task_data.get('estimated_hours', existing_task['estimated_hours']),
                        'actual_hours': task_data.get('actual_hours', existing_task['actual_hours']),
                        'dependencies': json.dumps(task_data.get('dependencies', json.loads(existing_task['dependencies'] or '[]'))),
                        'category': task_data.get('category', existing_task['category']),
                        'notes': task_data.get('notes', existing_task['notes']),
                        'created_at': existing_task['created_at'],
                        'updated_at': datetime.now().isoformat(),
                        'json_data': json.dumps(json_data, ensure_ascii=False) if json_data else existing_task['json_data']
                    }
                else:
                    # Create new task - use provided data or defaults
                    task_id = task_data.get('id') or json_data.get('id', '')
                    title = task_data.get('title') or json_data.get('title', '')
                    description = task_data.get('description') or json_data.get('description', '')
                    status = task_data.get('status') or json_data.get('status', 'pending')
                    created_at = task_data.get('created_at') or json_data.get('created_at', datetime.now().isoformat())
                    
                    merged_data = {
                        'id': task_id,
                        'title': title,
                        'description': description,
                        'status': status,
                        'priority': task_data.get('priority', 1),
                        'planned_start_time': task_data.get('planned_start_time'),
                        'planned_end_time': task_data.get('planned_end_time'),
                        'actual_start_time': task_data.get('actual_start_time'),
                        'actual_end_time': task_data.get('actual_end_time'),
                        'assigned_to': task_data.get('assigned_to'),
                        'created_by': task_data.get('created_by'),
                        'tags': json.dumps(task_data.get('tags', [])),
                        'progress': task_data.get('progress', 0),
                        'estimated_hours': task_data.get('estimated_hours'),
                        'actual_hours': task_data.get('actual_hours'),
                        'dependencies': json.dumps(task_data.get('dependencies', [])),
                        'category': task_data.get('category'),
                        'notes': task_data.get('notes'),
                        'created_at': created_at,
                        'updated_at': task_data.get('updated_at', datetime.now().isoformat()),
                        'json_data': json.dumps(json_data, ensure_ascii=False)
                    }
                
                # Insert or replace
                conn.execute("""
                    INSERT OR REPLACE INTO task_metadata (
                        id, title, description, status, priority,
                        planned_start_time, planned_end_time, actual_start_time, actual_end_time,
                        assigned_to, created_by, tags, progress, estimated_hours, actual_hours,
                        dependencies, category, notes, created_at, updated_at, json_data
                    ) VALUES (
                        :id, :title, :description, :status, :priority,
                        :planned_start_time, :planned_end_time, :actual_start_time, :actual_end_time,
                        :assigned_to, :created_by, :tags, :progress, :estimated_hours, :actual_hours,
                        :dependencies, :category, :notes, :created_at, :updated_at, :json_data
                    )
                """, merged_data)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating/updating task: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task metadata by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM task_metadata WHERE id = ?", (task_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    task = dict(row)
                    # Parse JSON fields
                    task['tags'] = json.loads(task['tags']) if task['tags'] else []
                    task['dependencies'] = json.loads(task['dependencies']) if task['dependencies'] else []
                    task['json_data'] = json.loads(task['json_data']) if task['json_data'] else {}
                    return task
                return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all task metadata."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM task_metadata ORDER BY created_at DESC")
                rows = cursor.fetchall()
                
                tasks = []
                for row in rows:
                    task = dict(row)
                    task['tags'] = json.loads(task['tags']) if task['tags'] else []
                    task['dependencies'] = json.loads(task['dependencies']) if task['dependencies'] else []
                    task['json_data'] = json.loads(task['json_data']) if task['json_data'] else {}
                    tasks.append(task)
                
                return tasks
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            return []
    
    def update_task_field(self, task_id: str, field: str, value: Any) -> bool:
        """Update a specific field of a task."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Handle JSON fields
                if field in ['tags', 'dependencies']:
                    value = json.dumps(value)
                
                conn.execute(
                    f"UPDATE task_metadata SET {field} = ?, updated_at = ? WHERE id = ?",
                    (value, datetime.now().isoformat(), task_id)
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating task field: {e}")
            return False
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task metadata."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM task_metadata WHERE id = ?", (task_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    def sync_from_task_tree(self, task_tree: Dict[str, Any]) -> bool:
        """
        Sync all tasks from task tree JSON to database.
        
        Args:
            task_tree: Complete task tree from JSON file
            
        Returns:
            Success status
        """
        try:
            def extract_tasks(node: Dict[str, Any], parent_id: str = None) -> List[Dict[str, Any]]:
                """Recursively extract all tasks from tree."""
                tasks = []
                
                if node.get('id') != 'root' or node.get('subtasks'):
                    task_copy = node.copy()
                    if parent_id:
                        task_copy['parent_id'] = parent_id
                    tasks.append(task_copy)
                
                # Process subtasks
                for subtask in node.get('subtasks', []):
                    tasks.extend(extract_tasks(subtask, node.get('id')))
                
                return tasks
            
            all_tasks = extract_tasks(task_tree)
            success_count = 0
            
            for task in all_tasks:
                if self.create_or_update_task({}, task):
                    success_count += 1
            
            print(f"Synced {success_count}/{len(all_tasks)} tasks to database")
            return success_count == len(all_tasks)
            
        except Exception as e:
            print(f"Error syncing from task tree: {e}")
            return False


# Global database instance
db = TaskDatabase()