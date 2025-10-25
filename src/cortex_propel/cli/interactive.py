import os
import sys
from typing import Optional, List
from datetime import datetime, timedelta

from ..agent import TaskAgent
from ..storage.file_manager import FileManager
from ..config.settings import load_settings
from ..llm import LLMProviderFactory
from ..models.task import TaskStatus, TaskPriority


class InteractiveCLI:
    """Interactive CLI for CortexPropel with enhanced features."""
    
    def __init__(self):
        """Initialize the interactive CLI."""
        self.settings = load_settings()
        self.file_manager = FileManager(self.settings)
        
        # Initialize LLM using the factory
        self.llm = LLMProviderFactory.create_llm(self.settings.llm)
        
        # Initialize agent
        self.agent = TaskAgent(self.llm, self.file_manager)
        
        # Default project
        self.project_id = self.settings.cli.default_project
        
        # Command history
        self.history = []
        
        # Current context
        self.current_context = {
            "project_id": self.project_id,
            "filter_status": None,
            "filter_priority": None
        }
    
    def run(self):
        """Run the interactive CLI."""
        self._print_welcome()
        
        # Show initial suggestions
        self._show_suggestions()
        
        while True:
            try:
                user_input = input(f"[{self.current_context['project_id']}]> ").strip()
                
                if not user_input:
                    continue
                
                # Add to history
                self.history.append(user_input)
                
                # Process commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
                
                if user_input.lower() in ["help", "h", "?"]:
                    self._show_help()
                    continue
                
                if user_input.lower() == "clear":
                    os.system("clear" if os.name == "posix" else "cls")
                    continue
                
                if user_input.lower() == "history":
                    self._show_history()
                    continue
                
                if user_input.lower() == "suggestions":
                    self._show_suggestions()
                    continue
                
                if user_input.lower() == "summary":
                    self._show_summary()
                    continue
                
                if user_input.lower().startswith("project "):
                    self._switch_project(user_input[8:].strip())
                    continue
                
                if user_input.lower().startswith("filter "):
                    self._set_filter(user_input[7:].strip())
                    continue
                
                if user_input.lower() == "clear filter":
                    self._clear_filter()
                    continue
                
                if user_input.lower() == "context":
                    self._show_context()
                    continue
                
                # Process as task command
                self._process_command(user_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _print_welcome(self):
        """Print welcome message."""
        print("CortexPropel Interactive CLI")
        print("=" * 50)
        print("Type 'help' for available commands or 'exit' to quit")
        print()
    
    def _show_help(self):
        """Show help information."""
        print("\nAvailable commands:")
        print("  help, h, ?          - Show this help message")
        print("  clear                - Clear the screen")
        print("  history              - Show command history")
        print("  suggestions          - Show task suggestions")
        print("  summary              - Show project summary")
        print("  project <name>       - Switch to a different project")
        print("  filter <criteria>    - Set filter (e.g., 'filter status:pending')")
        print("  clear filter         - Clear current filter")
        print("  context              - Show current context")
        print("  exit, quit, q        - Exit the application")
        print()
        print("Task commands (natural language):")
        print("  Create a task to finish the report by Friday")
        print("  Update task-123 status: in progress")
        print("  Show all pending tasks")
        print("  Find tasks with high priority")
        print("  Delete task-456")
        print("  Decompose task-789")
        print()
    
    def _show_history(self):
        """Show command history."""
        print("\nCommand history:")
        for i, cmd in enumerate(self.history[-10:], 1):
            print(f"  {i}. {cmd}")
        print()
    
    def _show_suggestions(self):
        """Show task suggestions."""
        suggestions = self.agent.get_task_suggestions(self.current_context["project_id"])
        
        if suggestions:
            print("\nSuggestions:")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
            print()
    
    def _show_summary(self):
        """Show project summary."""
        summary = self.agent.get_project_summary(self.current_context["project_id"])
        
        print(f"\nProject Summary: {self.current_context['project_id']}")
        print(f"Total tasks: {summary['total_tasks']}")
        print(f"Pending tasks: {summary['pending_tasks']}")
        print(f"In progress: {summary['in_progress_tasks']}")
        print(f"Completed: {summary['completed_tasks']}")
        print(f"Overdue: {summary['overdue_tasks']}")
        print(f"High priority: {summary['high_priority_tasks']}")
        print(f"Average progress: {summary['average_progress']:.1f}%")
        print()
    
    def _switch_project(self, project_name: str):
        """Switch to a different project."""
        if not project_name:
            print("Please specify a project name")
            return
        
        self.current_context["project_id"] = project_name
        print(f"Switched to project: {project_name}")
        
        # Show suggestions for the new project
        self._show_suggestions()
    
    def _set_filter(self, filter_criteria: str):
        """Set filter criteria."""
        if not filter_criteria:
            print("Please specify filter criteria (e.g., 'status:pending' or 'priority:high')")
            return
        
        parts = filter_criteria.split(":")
        if len(parts) != 2:
            print("Invalid filter format. Use 'status:value' or 'priority:value'")
            return
        
        key, value = parts[0].strip().lower(), parts[1].strip().lower()
        
        if key == "status":
            if value in ["pending", "in_progress", "completed"]:
                self.current_context["filter_status"] = value
                print(f"Filter set: status = {value}")
            else:
                print(f"Invalid status value: {value}")
        elif key == "priority":
            if value in ["low", "medium", "high", "critical"]:
                self.current_context["filter_priority"] = value
                print(f"Filter set: priority = {value}")
            else:
                print(f"Invalid priority value: {value}")
        else:
            print(f"Invalid filter key: {key}")
    
    def _clear_filter(self):
        """Clear current filter."""
        self.current_context["filter_status"] = None
        self.current_context["filter_priority"] = None
        print("Filter cleared")
    
    def _show_context(self):
        """Show current context."""
        print("\nCurrent context:")
        print(f"  Project: {self.current_context['project_id']}")
        
        if self.current_context["filter_status"]:
            print(f"  Status filter: {self.current_context['filter_status']}")
        
        if self.current_context["filter_priority"]:
            print(f"  Priority filter: {self.current_context['filter_priority']}")
        
        print()
    
    def _process_command(self, user_input: str):
        """Process a task command."""
        # Apply context to the input
        processed_input = user_input
        
        # If there's a status filter, add it to query commands
        if self.current_context["filter_status"] and any(
            cmd in user_input.lower() for cmd in ["show", "list", "find", "query"]
        ):
            if f"status:{self.current_context['filter_status']}" not in user_input.lower():
                processed_input += f" status:{self.current_context['filter_status']}"
        
        # If there's a priority filter, add it to query commands
        if self.current_context["filter_priority"] and any(
            cmd in user_input.lower() for cmd in ["show", "list", "find", "query"]
        ):
            if f"priority:{self.current_context['filter_priority']}" not in user_input.lower():
                processed_input += f" priority:{self.current_context['filter_priority']}"
        
        # Run the command
        result = self.agent.run(processed_input, self.current_context["project_id"])
        print(result.get("response", "No response"))
        
        # If there are query results, display them
        if "query_results" in result:
            self._display_tasks(result["query_results"])
    
    def _display_tasks(self, tasks: List):
        """Display a list of tasks in a formatted way."""
        if not tasks:
            return
        
        print("\nTasks:")
        for task in tasks:
            status_emoji = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅"
            }.get(task.status, "❓")
            
            priority_emoji = {
                TaskPriority.LOW: "🔵",
                TaskPriority.MEDIUM: "🟡",
                TaskPriority.HIGH: "🟠",
                TaskPriority.CRITICAL: "🔴"
            }.get(task.priority, "⚪")
            
            # Format due date
            due_str = ""
            if task.due_date:
                today = datetime.now().date()
                days_until_due = (task.due_date.date() - today).days
                
                if days_until_due < 0:
                    due_str = f" (Overdue by {abs(days_until_due)} days)"
                elif days_until_due == 0:
                    due_str = " (Due today)"
                elif days_until_due == 1:
                    due_str = " (Due tomorrow)"
                else:
                    due_str = f" (Due in {days_until_due} days)"
            
            # Format progress
            progress_str = ""
            if task.progress > 0:
                progress_str = f" [{task.progress}%]"
            
            # Format tags
            tags_str = ""
            if task.tags:
                tags_str = f" {' '.join('#' + tag for tag in task.tags)}"
            
            print(f"{status_emoji} {priority_emoji} [{task.id}] {task.title}{progress_str}{due_str}{tags_str}")
            
            if task.description:
                print(f"   Description: {task.description}")
            
            # Show subtasks if any
            if task.subtasks:
                print(f"   Subtasks: {len(task.subtasks)}")
            
            print()


def main():
    """Main entry point for the interactive CLI."""
    cli = InteractiveCLI()
    cli.run()


if __name__ == "__main__":
    main()