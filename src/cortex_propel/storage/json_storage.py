import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class JSONStorage:
    """JSON-based storage for CortexPropel data models."""
    
    def __init__(self, data_dir: str = "~/.cortex_propel"):
        """Initialize the JSON storage.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir).expanduser()
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all necessary directories exist."""
        directories = [
            self.data_dir,
            self.data_dir / "projects",
            self.data_dir / "tasks",
            self.data_dir / "backups",
            self.data_dir / "config"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _get_project_path(self, project_id: str) -> Path:
        """Get the file path for a project."""
        return self.data_dir / "projects" / f"{project_id}.json"
    
    def _get_task_path(self, task_id: str, project_id: str = "personal") -> Path:
        """Get the file path for a task."""
        project_dir = self.data_dir / "tasks" / project_id
        project_dir.mkdir(exist_ok=True)
        return project_dir / f"{task_id}.json"
    
    def _backup_file(self, file_path: Path) -> None:
        """Create a backup of a file."""
        if not file_path.exists():
            return
            
        backup_dir = self.data_dir / "backups" / datetime.now().strftime("%Y-%m-%d")
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"{file_path.stem}_{datetime.now().strftime('%H%M%S')}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
    
    def save_model(self, model: BaseModel, model_type: str, 
                   model_id: str, project_id: Optional[str] = None) -> None:
        """Save a model to JSON file.
        
        Args:
            model: The model to save
            model_type: Type of model ('task' or 'project')
            model_id: ID of the model
            project_id: Project ID (only used for tasks)
        """
        if model_type == "task":
            if project_id is None:
                project_id = "personal"
            file_path = self._get_task_path(model_id, project_id)
        elif model_type == "project":
            file_path = self._get_project_path(model_id)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Create backup before saving
        self._backup_file(file_path)
        
        # Save the model
        with open(file_path, 'w') as f:
            json.dump(model.dict(), f, indent=2, default=str)
    
    def load_model(self, model_class: Type[T], model_type: str, 
                   model_id: str, project_id: Optional[str] = None) -> Optional[T]:
        """Load a model from JSON file.
        
        Args:
            model_class: The model class to instantiate
            model_type: Type of model ('task' or 'project')
            model_id: ID of the model
            project_id: Project ID (only used for tasks)
            
        Returns:
            The loaded model or None if not found
        """
        if model_type == "task":
            if project_id is None:
                project_id = "personal"
            file_path = self._get_task_path(model_id, project_id)
        elif model_type == "project":
            file_path = self._get_project_path(model_id)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return model_class(**data)
        except (json.JSONDecodeError, TypeError, ValueError):
            return None
    
    def delete_model(self, model_type: str, model_id: str, 
                    project_id: Optional[str] = None) -> bool:
        """Delete a model file.
        
        Args:
            model_type: Type of model ('task' or 'project')
            model_id: ID of the model
            project_id: Project ID (only used for tasks)
            
        Returns:
            True if deleted, False if not found
        """
        if model_type == "task":
            if project_id is None:
                project_id = "personal"
            file_path = self._get_task_path(model_id, project_id)
        elif model_type == "project":
            file_path = self._get_project_path(model_id)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Create backup before deleting
        self._backup_file(file_path)
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def list_models(self, model_type: str, project_id: Optional[str] = None) -> List[str]:
        """List all model IDs of a given type.
        
        Args:
            model_type: Type of model ('task' or 'project')
            project_id: Project ID (only used for tasks)
            
        Returns:
            List of model IDs
        """
        if model_type == "task":
            if project_id is None:
                project_id = "personal"
            dir_path = self.data_dir / "tasks" / project_id
        elif model_type == "project":
            dir_path = self.data_dir / "projects"
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if not dir_path.exists():
            return []
        
        return [f.stem for f in dir_path.glob("*.json")]
    
    def save_config(self, config: Dict[str, Any], config_name: str = "settings") -> None:
        """Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary
            config_name: Name of the configuration file
        """
        file_path = self.data_dir / "config" / f"{config_name}.json"
        
        # Create backup before saving
        self._backup_file(file_path)
        
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self, config_name: str = "settings") -> Dict[str, Any]:
        """Load configuration from JSON file.
        
        Args:
            config_name: Name of the configuration file
            
        Returns:
            Configuration dictionary
        """
        file_path = self.data_dir / "config" / f"{config_name}.json"
        
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> None:
        """Clean up old backup files.
        
        Args:
            days_to_keep: Number of days to keep backups
        """
        backup_dir = self.data_dir / "backups"
        if not backup_dir.exists():
            return
        
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        for backup_day in backup_dir.iterdir():
            if backup_day.is_dir():
                try:
                    day_timestamp = datetime.strptime(backup_day.name, "%Y-%m-%d").timestamp()
                    if day_timestamp < cutoff_date:
                        shutil.rmtree(backup_day)
                except ValueError:
                    # Skip directories that don't match the expected date format
                    continue