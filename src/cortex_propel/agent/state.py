from typing import List, Dict, Any, Optional, TypedDict
from datetime import datetime

from ..models.task import Task, TaskStatus, TaskPriority


class AgentState(TypedDict):
    """State for the CortexPropel agent."""
    
    # User input and context
    user_input: str
    messages: List[Dict[str, str]]  # Conversation history
    
    # Parsed information
    intent: str  # User's intent (create_task, update_task, query_task, etc.)
    entities: Dict[str, Any]  # Extracted entities from user input
    
    # Task information
    task: Optional[Task]  # Current task being processed
    task_id: Optional[str]  # ID of the task being processed
    project_id: str  # Current project ID
    
    # Query results
    query_results: List[Task]  # Results from task queries
    
    # Response
    response: str  # Response to be shown to the user
    suggestions: List[str]  # Suggested next actions
    
    # System state
    error: Optional[str]  # Any error that occurred
    timestamp: datetime  # Current timestamp