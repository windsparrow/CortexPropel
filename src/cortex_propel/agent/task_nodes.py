import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from ..models.task import Task, TaskStatus, TaskPriority
from ..storage.file_manager import FileManager
from .state import AgentState


class TaskCreationNode:
    """Node for creating new tasks."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task creation node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
    
    def __call__(self, state: AgentState) -> AgentState:
        """Create a new task based on the extracted entities.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            entities = state.get("entities", {})
            project_id = state.get("project_id", "personal")
            
            # Generate a unique task ID
            task_id = f"task-{uuid.uuid4().hex[:8]}"
            
            # Create the task
            task_data = {
                "id": task_id,
                "title": entities.get("title", "Untitled Task"),
                "description": entities.get("description"),
                "priority": entities.get("priority", TaskPriority.MEDIUM),
                "due_date": entities.get("due_date"),
                "estimated_duration": entities.get("estimated_duration"),
                "tags": entities.get("tags", []),
                "status": TaskStatus.PENDING,
                "progress": 0
            }
            
            task = Task(**task_data)
            
            # Save the task
            self.file_manager.save_task(task, project_id)
            
            # Update state
            state["task"] = task
            state["task_id"] = task_id
            state["response"] = f"Created new task '{task.title}' with ID {task_id}"
            
            # Add to project if project exists
            project = self.file_manager.load_project(project_id)
            if project:
                project.add_task(task_id)
                self.file_manager.save_project(project)
            
        except Exception as e:
            state["error"] = f"Error creating task: {str(e)}"
        
        return state


class TaskUpdateNode:
    """Node for updating existing tasks."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task update node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
    
    def __call__(self, state: AgentState) -> AgentState:
        """Update an existing task based on the extracted entities.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            entities = state.get("entities", {})
            task_id = state.get("task_id")
            project_id = state.get("project_id", "personal")
            
            if not task_id:
                state["error"] = "No task ID provided for update"
                return state
            
            # Load the task
            task = self.file_manager.load_task(task_id, project_id)
            if not task:
                state["error"] = f"Task with ID {task_id} not found"
                return state
            
            # Update task fields
            if "title" in entities:
                task.title = entities["title"]
            
            if "description" in entities:
                task.description = entities["description"]
            
            if "priority" in entities:
                task.priority = entities["priority"]
            
            if "due_date" in entities:
                task.due_date = entities["due_date"]
            
            if "estimated_duration" in entities:
                task.estimated_duration = entities["estimated_duration"]
            
            if "tags" in entities:
                task.tags = entities["tags"]
            
            if "status" in entities:
                task.status = entities["status"]
                if entities["status"] == TaskStatus.COMPLETED:
                    task.progress = 100
                elif entities["status"] == TaskStatus.IN_PROGRESS and task.progress == 0:
                    task.progress = 10
            
            if "progress" in entities:
                task.update_progress(entities["progress"])
            
            # Save the updated task
            self.file_manager.save_task(task, project_id)
            
            # Update state
            state["task"] = task
            state["response"] = f"Updated task '{task.title}' with ID {task_id}"
            
        except Exception as e:
            state["error"] = f"Error updating task: {str(e)}"
        
        return state


class TaskQueryNode:
    """Node for querying tasks."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task query node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
    
    def __call__(self, state: AgentState) -> AgentState:
        """Query tasks based on the extracted entities.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            entities = state.get("entities", {})
            project_id = state.get("project_id", "personal")
            task_id = state.get("task_id")
            
            # If a specific task ID is provided, load that task
            if task_id:
                task = self.file_manager.load_task(task_id, project_id)
                if task:
                    state["query_results"] = [task]
                    state["response"] = f"Found task: {task.title} (ID: {task.id})"
                else:
                    state["response"] = f"Task with ID {task_id} not found"
                    state["query_results"] = []
                return state
            
            # Otherwise, query based on filters
            tasks = []
            
            # Filter by status
            if "status" in entities:
                status = entities["status"]
                tasks = self.file_manager.get_tasks_by_status(status, project_id)
            
            # Filter by priority
            elif "priority" in entities:
                priority = entities["priority"]
                tasks = self.file_manager.get_tasks_by_priority(priority, project_id)
            
            # Search by text
            elif "title" in entities or "description" in entities or "tags" in entities:
                query = entities.get("title", "") or entities.get("description", "")
                if not query and "tags" in entities:
                    query = " ".join(entities["tags"])
                tasks = self.file_manager.search_tasks(query, project_id)
            
            # If no specific filters, get all tasks
            else:
                task_ids = self.file_manager.list_tasks(project_id)
                for tid in task_ids:
                    task = self.file_manager.load_task(tid, project_id)
                    if task:
                        tasks.append(task)
            
            state["query_results"] = tasks
            
            if tasks:
                state["response"] = f"Found {len(tasks)} task(s)"
            else:
                state["response"] = "No tasks found matching your criteria"
            
        except Exception as e:
            state["error"] = f"Error querying tasks: {str(e)}"
        
        return state


class TaskDeletionNode:
    """Node for deleting tasks."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task deletion node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
    
    def __call__(self, state: AgentState) -> AgentState:
        """Delete a task based on the task ID.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            task_id = state.get("task_id")
            project_id = state.get("project_id", "personal")
            
            if not task_id:
                state["error"] = "No task ID provided for deletion"
                return state
            
            # Load the task to get its title for the response
            task = self.file_manager.load_task(task_id, project_id)
            task_title = task.title if task else f"Task {task_id}"
            
            # Delete the task
            success = self.file_manager.delete_task(task_id, project_id)
            
            if success:
                # Remove from project if project exists
                project = self.file_manager.load_project(project_id)
                if project and task_id in project.tasks:
                    project.remove_task(task_id)
                    self.file_manager.save_project(project)
                
                state["response"] = f"Deleted task '{task_title}' with ID {task_id}"
            else:
                state["response"] = f"Task with ID {task_id} not found"
            
        except Exception as e:
            state["error"] = f"Error deleting task: {str(e)}"
        
        return state


class TaskDecompositionNode:
    """Node for decomposing tasks into subtasks."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task decomposition node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
        
        # Task decomposition prompt
        self.decomposition_prompt = PromptTemplate(
            input_variables=["task_title", "task_description"],
            template="""
            Break down the following task into smaller, manageable subtasks:
            
            Task: {task_title}
            Description: {task_description}
            
            Provide a list of 3-7 subtasks that would help complete this task.
            Each subtask should be specific, actionable, and clearly defined.
            
            Respond with a JSON array of objects:
            [
                {{
                    "title": "Subtask title",
                    "description": "Brief description of what needs to be done",
                    "estimated_duration": 30
                }},
                ...
            ]
            """
        )
    
    def __call__(self, state: AgentState) -> AgentState:
        """Decompose a task into subtasks.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            task_id = state.get("task_id")
            project_id = state.get("project_id", "personal")
            
            if not task_id:
                state["error"] = "No task ID provided for decomposition"
                return state
            
            # Load the task
            task = self.file_manager.load_task(task_id, project_id)
            if not task:
                state["error"] = f"Task with ID {task_id} not found"
                return state
            
            # Use LLM to decompose the task
            prompt = self.decomposition_prompt.format(
                task_title=task.title,
                task_description=task.description or ""
            )
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Parse the JSON response
            import json
            try:
                subtasks_data = json.loads(result)
                if not isinstance(subtasks_data, list):
                    subtasks_data = [subtasks_data]
            except json.JSONDecodeError:
                # Fallback to simple subtask creation
                subtasks_data = [
                    {"title": "Research requirements", "description": "Research what needs to be done", "estimated_duration": 30},
                    {"title": "Plan implementation", "description": "Create a plan for implementation", "estimated_duration": 30},
                    {"title": "Execute task", "description": "Complete the main work", "estimated_duration": 60}
                ]
            
            # Create subtasks
            subtask_ids = []
            for subtask_data in subtasks_data:
                subtask_id = f"task-{uuid.uuid4().hex[:8]}"
                
                subtask = Task(
                    id=subtask_id,
                    title=subtask_data.get("title", "Untitled Subtask"),
                    description=subtask_data.get("description", ""),
                    priority=task.priority,
                    estimated_duration=subtask_data.get("estimated_duration", 30),
                    parent_id=task_id,
                    status=TaskStatus.PENDING,
                    progress=0
                )
                
                # Save the subtask
                self.file_manager.save_task(subtask, project_id)
                subtask_ids.append(subtask_id)
            
            # Update the parent task with subtasks
            task.subtasks = subtask_ids
            self.file_manager.save_task(task, project_id)
            
            # Update state
            state["task"] = task
            state["response"] = f"Decomposed task '{task.title}' into {len(subtask_ids)} subtasks"
            
            # Add subtasks to suggestions for user to see
            state["suggestions"] = [f"View subtasks of {task.title}"]
            
        except Exception as e:
            state["error"] = f"Error decomposing task: {str(e)}"
        
        return state


class ResponseGenerationNode:
    """Node for generating user-friendly responses."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the response generation node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
    
    def __call__(self, state: AgentState) -> AgentState:
        """Generate a user-friendly response based on the current state.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        try:
            # If there's an error, prioritize that in the response
            if "error" in state:
                state["response"] = f"Error: {state['error']}"
                return state
            
            # If we already have a response, just add it to the conversation history
            if "response" in state:
                state["messages"].append({"role": "assistant", "content": state["response"]})
                return state
            
            # Generate a default response based on intent
            intent = state.get("intent", "other")
            
            if intent == "help":
                state["response"] = self._generate_help_response()
            else:
                state["response"] = "I'm not sure how to help with that. Try 'help' for available commands."
            
            # Add response to conversation history
            state["messages"].append({"role": "assistant", "content": state["response"]})
            
        except Exception as e:
            state["error"] = f"Error generating response: {str(e)}"
        
        return state
    
    def _generate_help_response(self) -> str:
        """Generate a help response.
        
        Returns:
            Help message
        """
        return """
        I can help you manage your tasks. Here are some examples of what you can ask me:
        
        **Create a task:**
        - "Create a task to finish the report by Friday"
        - "Add task: Prepare presentation #work"
        - "New task: Call the client, priority: high"
        
        **Update a task:**
        - "Update task-123 status: in progress"
        - "Change task-456 priority to critical"
        - "Mark task-789 as completed"
        
        **Query tasks:**
        - "Show all pending tasks"
        - "Find tasks with high priority"
        - "List tasks tagged with #work"
        - "Search for tasks about report"
        
        **Delete a task:**
        - "Delete task-123"
        
        **Decompose a task:**
        - "Break down task-456 into subtasks"
        
        **General:**
        - "What tasks do I have?"
        - "Help"
        """