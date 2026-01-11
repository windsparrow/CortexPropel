#!/usr/bin/env python3
"""
FastAPI server for task visualization.
Provides read-only endpoints to inspect task tree and database.
"""

import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task_manager import TaskManager
from src.database import TaskDatabase

app = FastAPI(title="Task Visualization Server", version="1.0.0")

# Initialize database with correct paths
# Use main data folder instead of visualization/data
data_dir = Path(__file__).parent.parent / "data"
task_tree_file = data_dir / "task_tree.json"
chat_history_file = data_dir / "chat_history.json"
database = TaskDatabase(db_path=str(data_dir / "tasks.db"))
task_manager = TaskManager()  # Initialize TaskManager for chat functionality

def load_task_tree_local():
    """Load task tree directly from JSON file."""
    try:
        if task_tree_file.exists():
            with open(task_tree_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"subtasks": []} # Fallback
    except Exception as e:
        logger.error(f"Error loading task tree: {e}")
        return {"subtasks": []}

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

class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    success: bool
    message: str
    tree: Dict[str, Any]
    tasks: List[Dict[str, Any]]
    error: Optional[str] = None
    report: Optional[str] = None  # Analysis report for query operations

class ChatMessage(BaseModel):
    """Model for a single chat message."""
    role: str
    content: str
    timestamp: str

class ChatHistoryRequest(BaseModel):
    """Request model for saving chat history."""
    messages: List[ChatMessage]

class ChatHistoryResponse(BaseModel):
    """Response model for loading chat history."""
    messages: List[Dict[str, str]]

@app.get("/")
async def read_index():
    """Serve the main visualization page."""
    index_path = Path(__file__).parent / "index.html"
    return FileResponse(str(index_path))

@app.get("/api/tree", response_model=TaskTreeResponse)
async def get_task_tree():
    """Get the current task tree from JSON file."""
    try:
        tree = load_task_tree_local()
        
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
        tree = load_task_tree_local()
        
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

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest):
    """Process chat message and update task tree."""
    try:
        # Log user input
        logger.info(f"[用户输入] {request.message}")
        
        # Process user input through TaskManager
        # Now returns dict with tree, operations_applied, message
        result = task_manager.process_user_input(request.message)
        
        # Get updated task list from database
        tasks = database.get_all_tasks()
        
        # Log operation results and collect reports
        ops = result.get("operations_applied", [])
        logger.info(f"[操作结果] 执行了 {len(ops)} 个操作")
        
        report = None
        for op in ops:
            status = "✓" if op.get("success") else "✗"
            op_type = op.get('operation', '')
            logger.info(f"  {status} {op_type}: {op.get('title') or op.get('target_title') or op.get('task_id', '')[:8]}")
            
            # Extract report from query operations
            if op_type == "query" and op.get("report"):
                report = op.get("report")
                logger.info(f"  [分析报告] 生成报告，{op.get('task_count', 0)} 条记录")
        
        # Use message from LLM or default
        response_message = result.get("message", "任务已更新")
        
        return ChatResponse(
            success=True,
            message=response_message,
            tree=result.get("tree", load_task_tree_local()),
            tasks=tasks,
            report=report
        )
    except Exception as e:
        # Log error
        logger.error(f"[LLM处理失败] {str(e)}")
        
        # On error, still return current state
        current_tree = load_task_tree_local()
        current_tasks = database.get_all_tasks()
        
        return ChatResponse(
            success=False,
            message=f"处理失败: {str(e)}",
            tree=current_tree,
            tasks=current_tasks,
            error=str(e)
        )

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

@app.post("/api/reset")
async def reset_task_tree():
    """Reset the task tree and database to initial state."""
    try:
        # Reset task tree using TaskManager
        reset_tree = task_manager.reset_task_tree()
        logger.info("Task tree reset successfully")
        
        return {
            "success": True,
            "message": "任务树已重置",
            "tree": reset_tree
        }
    except Exception as e:
        logger.error(f"Error resetting task tree: {e}")
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Custom uvicorn log config with timestamps
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": "%(asctime)s [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        },
    }
    
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True, log_config=log_config)
@app.get("/api/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history():
    """Get chat history from file."""
    try:
        if chat_history_file.exists():
            with open(chat_history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ChatHistoryResponse(messages=data.get("messages", []))
        return ChatHistoryResponse(messages=[])
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return ChatHistoryResponse(messages=[])

@app.post("/api/chat/history")
async def save_chat_history(request: ChatHistoryRequest):
    """Save chat history to file."""
    try:
        # Ensure data directory exists
        chat_history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(chat_history_file, "w", encoding="utf-8") as f:
            json.dump({
                "messages": [msg.dict() for msg in request.messages]
            }, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "message": "Chat history saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save chat history: {str(e)}")
