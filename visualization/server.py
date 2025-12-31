#!/usr/bin/env python3
"""
FastAPI server for task visualization.
Provides read-only endpoints to inspect task tree and database.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task_manager import TaskManager
from src.database import TaskDatabase

app = FastAPI(title="Task Visualization Server", version="1.0.0")

# Initialize task manager and database with correct paths
# Use main data folder instead of visualization/data
task_manager = TaskManager()
task_manager.task_tree_file = str(Path(__file__).parent.parent / "data" / "task_tree.json")
database = TaskDatabase(db_path=str(Path(__file__).parent.parent / "data" / "tasks.db"))

class TaskTreeResponse(BaseModel):
    """Response model for task tree data."""
    tree: Dict[str, Any]
    total_tasks: int
    max_depth: int

class TaskListResponse(BaseModel):
    """Response model for task list data."""
    tasks: List[Dict[str, Any]]
    total_count: int
    status_breakdown: Dict[str, int]

class ValidationResponse(BaseModel):
    """Response model for data validation."""
    json_only_tasks: List[str]
    db_only_tasks: List[str]
    common_tasks: List[str]
    consistency_score: float
    issues: List[str]

@app.get("/")
async def read_index():
    """Serve the main visualization page."""
    index_path = Path(__file__).parent / "index.html"
    return FileResponse(str(index_path))

@app.get("/api/tree", response_model=TaskTreeResponse)
async def get_task_tree():
    """Get the current task tree from JSON file."""
    try:
        tree = task_manager.load_task_tree()
        
        # Calculate tree statistics
        def count_tasks(node: Dict[str, Any]) -> int:
            count = 1
            for subtask in node.get("subtasks", []):
                count += count_tasks(subtask)
            return count
        
        def max_depth(node: Dict[str, Any], current_depth: int = 0) -> int:
            max_subtask_depth = current_depth
            for subtask in node.get("subtasks", []):
                subtask_depth = max_depth(subtask, current_depth + 1)
                max_subtask_depth = max(max_subtask_depth, subtask_depth)
            return max_subtask_depth
        
        return TaskTreeResponse(
            tree=tree,
            total_tasks=count_tasks(tree),
            max_depth=max_depth(tree)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading task tree: {str(e)}")

@app.get("/api/tasks", response_model=TaskListResponse)
async def get_all_tasks():
    """Get all tasks from database."""
    try:
        tasks = database.get_all_tasks()
        
        # Calculate status breakdown
        status_breakdown = {}
        for task in tasks:
            status = task.get("status", "unknown")
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        return TaskListResponse(
            tasks=tasks,
            total_count=len(tasks),
            status_breakdown=status_breakdown
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading tasks from database: {str(e)}")

@app.get("/api/validate", response_model=ValidationResponse)
async def validate_data_consistency():
    """Compare task tree JSON with database and check consistency."""
    try:
        # Get task tree from JSON
        tree = task_manager.load_task_tree()
        
        # Get all task IDs from tree
        def extract_task_ids(node: Dict[str, Any]) -> List[str]:
            ids = [node.get("id", "")]
            for subtask in node.get("subtasks", []):
                ids.extend(extract_task_ids(subtask))
            return ids
        
        json_task_ids = set(extract_task_ids(tree))
        
        # Get all task IDs from database
        db_tasks = database.get_all_tasks()
        db_task_ids = {task.get("id", "") for task in db_tasks}
        
        # Find differences
        json_only_tasks = list(json_task_ids - db_task_ids)
        db_only_tasks = list(db_task_ids - json_task_ids)
        common_tasks = list(json_task_ids & db_task_ids)
        
        # Calculate consistency score
        total_unique_tasks = len(json_task_ids | db_task_ids)
        if total_unique_tasks > 0:
            consistency_score = len(common_tasks) / total_unique_tasks
        else:
            consistency_score = 1.0
        
        # Generate issues list
        issues = []
        if json_only_tasks:
            issues.append(f"Tasks only in JSON: {len(json_only_tasks)}")
        if db_only_tasks:
            issues.append(f"Tasks only in database: {len(db_only_tasks)}")
        if consistency_score < 1.0:
            issues.append(f"Data inconsistency detected: {consistency_score:.1%} consistency")
        
        return ValidationResponse(
            json_only_tasks=json_only_tasks,
            db_only_tasks=db_only_tasks,
            common_tasks=common_tasks,
            consistency_score=consistency_score,
            issues=issues
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating data: {str(e)}")

@app.get("/api/task/{task_id}")
async def get_task_details(task_id: str):
    """Get detailed information about a specific task."""
    try:
        task = database.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found in database")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading task details: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)