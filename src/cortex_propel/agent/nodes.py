import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from ..models.task import Task, TaskStatus, TaskPriority
from ..storage.file_manager import FileManager
from .state import AgentState


class TaskParserNode:
    """Node for parsing user input and extracting task information."""
    
    def __init__(self, llm, file_manager: FileManager):
        """Initialize the task parser node.
        
        Args:
            llm: Language model for natural language processing
            file_manager: File manager for data access
        """
        self.llm = llm
        self.file_manager = file_manager
        
        # Intent recognition prompt
        self.intent_prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""
            Analyze the user's input and determine their intent. 
            Possible intents:
            - create_task: User wants to create a new task
            - update_task: User wants to update an existing task
            - query_task: User wants to query for tasks
            - delete_task: User wants to delete a task
            - decompose_task: User wants to break down a task into subtasks
            - help: User is asking for help
            - other: Any other intent
            
            User input: {user_input}
            
            Respond with a JSON object:
            {{
                "intent": "intent_name",
                "confidence": 0.9,
                "reasoning": "Explanation of why this intent was chosen"
            }}
            """
        )
        
        # Task extraction prompt
        self.task_extraction_prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""
            Extract task information from the user's input.
            
            User input: {user_input}
            
            Respond with a JSON object containing any of the following fields that are present:
            {{
                "title": "Task title",
                "description": "Detailed description",
                "priority": "low|medium|high|critical",
                "due_date": "YYYY-MM-DD or relative date like 'tomorrow', 'next week'",
                "estimated_duration": 60,
                "tags": ["tag1", "tag2"],
                "task_id": "ID of existing task if mentioned",
                "status": "pending|in_progress|completed|cancelled",
                "progress": 0-100
            }}
            
            Only include fields that are explicitly mentioned or can be reasonably inferred.
            """
        )
    
    def __call__(self, state: AgentState) -> AgentState:
        """Process the user input and extract intent and entities.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated agent state
        """
        user_input = state.get("user_input", "")
        if not user_input:
            state["error"] = "No user input provided"
            return state
        
        # Add user message to conversation history
        state["messages"].append({"role": "user", "content": user_input})
        
        try:
            # Determine intent
            intent_result = self._determine_intent(user_input)
            state["intent"] = intent_result.get("intent", "other")
            
            # Extract entities based on intent
            entities = self._extract_entities(user_input, state["intent"])
            state["entities"] = entities
            
            # Set project ID if provided
            if "project_id" in entities:
                state["project_id"] = entities["project_id"]
            
            # Set task ID if provided
            if "task_id" in entities:
                state["task_id"] = entities["task_id"]
            
            # Update timestamp
            state["timestamp"] = datetime.now()
            
        except Exception as e:
            state["error"] = f"Error parsing input: {str(e)}"
        
        return state
    
    def _determine_intent(self, user_input: str) -> Dict[str, Any]:
        """Determine the user's intent from their input.
        
        Args:
            user_input: The user's input
            
        Returns:
            Dictionary containing intent and confidence
        """
        # Simple keyword-based intent recognition as fallback
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ["create", "add", "new", "make"]):
            if "task" in input_lower:
                return {"intent": "create_task", "confidence": 0.9}
        elif any(word in input_lower for word in ["update", "change", "modify", "edit"]):
            if "task" in input_lower:
                return {"intent": "update_task", "confidence": 0.9}
        elif any(word in input_lower for word in ["show", "list", "find", "search", "query"]):
            if "task" in input_lower:
                return {"intent": "query_task", "confidence": 0.9}
        elif any(word in input_lower for word in ["delete", "remove"]):
            if "task" in input_lower:
                return {"intent": "delete_task", "confidence": 0.9}
        elif any(word in input_lower for word in ["break down", "decompose", "split"]):
            if "task" in input_lower:
                return {"intent": "decompose_task", "confidence": 0.9}
        elif any(word in input_lower for word in ["help", "how to"]):
            return {"intent": "help", "confidence": 0.9}
        
        # Use LLM for more complex intent recognition
        try:
            prompt = self.intent_prompt.format(user_input=user_input)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Try to parse JSON response
            import json
            return json.loads(result)
        except:
            # Fallback to "other" intent
            return {"intent": "other", "confidence": 0.5}
    
    def _extract_entities(self, user_input: str, intent: str) -> Dict[str, Any]:
        """Extract entities from user input based on intent.
        
        Args:
            user_input: The user's input
            intent: The determined intent
            
        Returns:
            Dictionary of extracted entities
        """
        # Use LLM for entity extraction
        try:
            prompt = self.task_extraction_prompt.format(user_input=user_input)
            response = self.llm.invoke([HumanMessage(content=prompt)])
            result = response.content.strip()
            
            # Try to parse JSON response
            import json
            entities = json.loads(result)
            
            # Process special fields
            if "due_date" in entities and entities["due_date"]:
                entities["due_date"] = self._parse_date(entities["due_date"])
            
            if "priority" in entities and entities["priority"]:
                entities["priority"] = self._parse_priority(entities["priority"])
            
            if "status" in entities and entities["status"]:
                entities["status"] = self._parse_status(entities["status"])
            
            return entities
        except:
            # Fallback to simple regex-based extraction
            return self._extract_entities_fallback(user_input, intent)
    
    def _extract_entities_fallback(self, user_input: str, intent: str) -> Dict[str, Any]:
        """Fallback method for entity extraction using regex.
        
        Args:
            user_input: The user's input
            intent: The determined intent
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Extract task ID (assuming format like "task-123" or "task_123")
        task_id_match = re.search(r'(?:task[-_]?)([a-zA-Z0-9]+)', user_input, re.IGNORECASE)
        if task_id_match:
            entities["task_id"] = f"task-{task_id_match.group(1)}"
        
        # Extract priority
        priority_match = re.search(r'(?:priority|level)\s*[:=]?\s*(low|medium|high|critical)', user_input, re.IGNORECASE)
        if priority_match:
            entities["priority"] = priority_match.group(1).lower()
        
        # Extract due date
        date_match = re.search(r'(?:due|by|before)\s*[:=]?\s*(\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2}|tomorrow|today|next week)', user_input, re.IGNORECASE)
        if date_match:
            entities["due_date"] = self._parse_date(date_match.group(1))
        
        # Extract estimated duration
        duration_match = re.search(r'(?:duration|estimate|take)\s*[:=]?\s*(\d+)\s*(?:minutes?|hours?|hrs?)', user_input, re.IGNORECASE)
        if duration_match:
            duration = int(duration_match.group(1))
            unit = duration_match.group(2).lower()
            if unit.startswith("hour"):
                duration *= 60
            entities["estimated_duration"] = duration
        
        # Extract status
        status_match = re.search(r'(?:status|state)\s*[:=]?\s*(pending|in progress|completed|cancelled)', user_input, re.IGNORECASE)
        if status_match:
            entities["status"] = status_match.group(1).lower().replace(" ", "_")
        
        # Extract progress
        progress_match = re.search(r'(?:progress)\s*[:=]?\s*(\d{1,3})%?', user_input, re.IGNORECASE)
        if progress_match:
            entities["progress"] = min(100, max(0, int(progress_match.group(1))))
        
        # Extract tags (words starting with #)
        tags = re.findall(r'#(\w+)', user_input)
        if tags:
            entities["tags"] = tags
        
        # Extract title (for create_task intent)
        if intent == "create_task":
            # Try to extract a title from the input
            # Remove common command words and extract the remaining text
            cleaned_input = re.sub(r'(?:create|add|new)\s+(?:task\s+)?', '', user_input, flags=re.IGNORECASE)
            cleaned_input = re.sub(r'\s+(?:with|for|by|due|priority|duration|tag).*$', '', cleaned_input, flags=re.IGNORECASE)
            cleaned_input = re.sub(r'#\w+', '', cleaned_input)  # Remove tags
            cleaned_input = cleaned_input.strip()
            
            if cleaned_input:
                entities["title"] = cleaned_input
        
        return entities
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into a datetime object.
        
        Args:
            date_str: The date string to parse
            
        Returns:
            Parsed datetime or None if parsing failed
        """
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str)
        except:
            pass
        
        try:
            # Try common formats
            date_str_lower = date_str.lower()
            
            if date_str_lower == "today":
                return datetime.now()
            elif date_str_lower == "tomorrow":
                return datetime.now() + timedelta(days=1)
            elif date_str_lower == "next week":
                return datetime.now() + timedelta(weeks=1)
            elif "next" in date_str_lower and "week" in date_str_lower:
                # Extract day of week
                days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                for i, day in enumerate(days):
                    if day in date_str_lower:
                        today = datetime.now().weekday()
                        days_ahead = i - today
                        if days_ahead <= 0:  # Target day already happened this week
                            days_ahead += 7
                        return datetime.now() + timedelta(days=days_ahead)
            
            # Try to parse with dateutil if available
            try:
                from dateutil import parser
                return parser.parse(date_str)
            except ImportError:
                pass
            
            # Try simple MM-DD or YYYY-MM-DD format
            if re.match(r'\d{1,2}-\d{1,2}$', date_str):
                month, day = date_str.split('-')
                year = datetime.now().year
                return datetime(year, int(month), int(day))
            elif re.match(r'\d{4}-\d{1,2}-\d{1,2}$', date_str):
                year, month, day = date_str.split('-')
                return datetime(int(year), int(month), int(day))
        except:
            pass
        
        return None
    
    def _parse_priority(self, priority_str: str) -> str:
        """Parse a priority string.
        
        Args:
            priority_str: The priority string to parse
            
        Returns:
            Normalized priority string
        """
        priority_str = priority_str.lower()
        
        if priority_str in ["low", "lowest"]:
            return TaskPriority.LOW
        elif priority_str in ["medium", "normal", "mid"]:
            return TaskPriority.MEDIUM
        elif priority_str in ["high", "urgent"]:
            return TaskPriority.HIGH
        elif priority_str in ["critical", "asap", "immediate"]:
            return TaskPriority.CRITICAL
        
        return TaskPriority.MEDIUM
    
    def _parse_status(self, status_str: str) -> str:
        """Parse a status string.
        
        Args:
            status_str: The status string to parse
            
        Returns:
            Normalized status string
        """
        status_str = status_str.lower().replace(" ", "_")
        
        if status_str in ["pending", "todo", "to_do"]:
            return TaskStatus.PENDING
        elif status_str in ["in_progress", "doing", "working"]:
            return TaskStatus.IN_PROGRESS
        elif status_str in ["completed", "done", "finished"]:
            return TaskStatus.COMPLETED
        elif status_str in ["cancelled", "canceled", "abandoned"]:
            return TaskStatus.CANCELLED
        
        return TaskStatus.PENDING