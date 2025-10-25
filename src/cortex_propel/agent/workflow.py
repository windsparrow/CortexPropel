from typing import Dict, Any, List, Literal, Optional
from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import TaskParserNode
from .task_nodes import (
    TaskCreationNode,
    TaskUpdateNode,
    TaskQueryNode,
    TaskDeletionNode,
    TaskDecompositionNode,
    ResponseGenerationNode
)
from ..storage.file_manager import FileManager


class TaskAgent:
    """LangGraph-based agent for task management."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task agent.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
        
        # Initialize nodes
        self.parser_node = TaskParserNode(llm, file_manager)
        self.creation_node = TaskCreationNode(llm, file_manager)
        self.update_node = TaskUpdateNode(llm, file_manager)
        self.query_node = TaskQueryNode(llm, file_manager)
        self.deletion_node = TaskDeletionNode(llm, file_manager)
        self.decomposition_node = TaskDecompositionNode(llm, file_manager)
        self.response_node = ResponseGenerationNode(llm, file_manager)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        # Compile the workflow
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow.
        
        Returns:
            Compiled workflow graph
        """
        # Create a new graph
        workflow = StateGraph(AgentState)
        
        # Add nodes to the graph
        workflow.add_node("parse_input", self.parser_node)
        workflow.add_node("create_task", self.creation_node)
        workflow.add_node("update_task", self.update_node)
        workflow.add_node("query_tasks", self.query_node)
        workflow.add_node("delete_task", self.deletion_node)
        workflow.add_node("decompose_task", self.decomposition_node)
        workflow.add_node("generate_response", self.response_node)
        
        # Set the entry point
        workflow.set_entry_point("parse_input")
        
        # Add conditional edges based on intent
        workflow.add_conditional_edges(
            "parse_input",
            self._route_based_on_intent,
            {
                "create": "create_task",
                "update": "update_task",
                "query": "query_tasks",
                "delete": "delete_task",
                "decompose": "decompose_task",
                "help": "generate_response",
                "other": "generate_response"
            }
        )
        
        # All task operations lead to response generation
        workflow.add_edge("create_task", "generate_response")
        workflow.add_edge("update_task", "generate_response")
        workflow.add_edge("query_tasks", "generate_response")
        workflow.add_edge("delete_task", "generate_response")
        workflow.add_edge("decompose_task", "generate_response")
        
        # End at response generation
        workflow.add_edge("generate_response", END)
        
        return workflow
    
    def _route_based_on_intent(self, state: AgentState) -> str:
        """Route to the appropriate node based on intent.
        
        Args:
            state: Current agent state
            
        Returns:
            Name of the next node to route to
        """
        intent = state.get("intent", "other")
        
        # If there's an error, go to response generation
        if "error" in state:
            return "generate_response"
        
        return intent
    
    def run(self, input_text: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Run the agent with the given input.
        
        Args:
            input_text: User input text
            project_id: Optional project ID to work with
            
        Returns:
            Agent response
        """
        # Initialize state
        state = {
            "user_input": input_text,
            "project_id": project_id or "personal",
            "messages": [{"role": "user", "content": input_text}]
        }
        
        # Run the workflow
        result = self.app.invoke(state)
        
        return result
    
    def get_task_suggestions(self, project_id: Optional[str] = None) -> List[str]:
        """Get task suggestions for the user.
        
        Args:
            project_id: Optional project ID to get suggestions for
            
        Returns:
            List of suggested actions
        """
        project_id = project_id or "personal"
        suggestions = []
        
        try:
            # Get pending tasks
            pending_tasks = self.file_manager.get_tasks_by_status("pending", project_id)
            if pending_tasks:
                suggestions.append(f"You have {len(pending_tasks)} pending task(s)")
                
                # Suggest working on high priority tasks
                high_priority_tasks = [t for t in pending_tasks if t.priority.value >= 4]
                if high_priority_tasks:
                    suggestions.append(f"Consider working on {len(high_priority_tasks)} high priority task(s)")
            
            # Get overdue tasks
            from datetime import datetime
            today = datetime.now().date()
            overdue_tasks = []
            
            for task in pending_tasks:
                if task.due_date and task.due_date.date() < today:
                    overdue_tasks.append(task)
            
            if overdue_tasks:
                suggestions.append(f"You have {len(overdue_tasks)} overdue task(s)")
            
            # Get in-progress tasks
            in_progress_tasks = self.file_manager.get_tasks_by_status("in_progress", project_id)
            if in_progress_tasks:
                suggestions.append(f"You have {len(in_progress_tasks)} task(s) in progress")
            
            # Get completed tasks
            completed_tasks = self.file_manager.get_tasks_by_status("completed", project_id)
            if completed_tasks:
                suggestions.append(f"You have completed {len(completed_tasks)} task(s)")
            
            # If no tasks, suggest creating one
            if not pending_tasks and not in_progress_tasks:
                suggestions.append("You have no tasks. Consider creating a new task.")
            
        except Exception as e:
            suggestions.append(f"Error getting suggestions: {str(e)}")
        
        return suggestions
    
    def get_project_summary(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of the project.
        
        Args:
            project_id: Optional project ID to get summary for
            
        Returns:
            Project summary
        """
        project_id = project_id or "personal"
        summary = {
            "project_id": project_id,
            "total_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "high_priority_tasks": 0,
            "average_progress": 0
        }
        
        try:
            # Get all tasks
            task_ids = self.file_manager.list_tasks(project_id)
            tasks = []
            
            for task_id in task_ids:
                task = self.file_manager.load_task(task_id, project_id)
                if task:
                    tasks.append(task)
            
            # Count tasks by status
            summary["total_tasks"] = len(tasks)
            summary["pending_tasks"] = len([t for t in tasks if t.status.value == "pending"])
            summary["in_progress_tasks"] = len([t for t in tasks if t.status.value == "in_progress"])
            summary["completed_tasks"] = len([t for t in tasks if t.status.value == "completed"])
            
            # Count overdue tasks
            from datetime import datetime
            today = datetime.now().date()
            
            for task in tasks:
                if task.due_date and task.due_date.date() < today and task.status.value != "completed":
                    summary["overdue_tasks"] += 1
                
                # Count high priority tasks
                if task.priority.value >= 4 and task.status.value != "completed":
                    summary["high_priority_tasks"] += 1
            
            # Calculate average progress
            if tasks:
                total_progress = sum(task.progress for task in tasks)
                summary["average_progress"] = total_progress / len(tasks)
            
        except Exception as e:
            summary["error"] = str(e)
        
        return summary