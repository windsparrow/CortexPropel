"""CLI entry point for CortexPropel."""

import argparse
import os
import sys
from typing import Optional

from ..llm import LLMProviderFactory
from ..agent import TaskAgent
from ..config.settings import load_settings
from ..storage.file_manager import FileManager


class CLI:
    """Command-line interface for CortexPropel."""
    
    def __init__(self, config_path: Optional[str] = None, project_id: Optional[str] = None, create_llm: bool = True):
        """Initialize the CLI.
        
        Args:
            config_path: Path to configuration file
            project_id: Default project ID
            create_llm: Whether to create LLM instance (default: True)
        """
        self.settings = load_settings(config_path)
        self.llm = None
        if create_llm:
            self.llm = LLMProviderFactory.create_llm(self.settings.llm)
        self.file_manager = FileManager(self.settings.storage.data_dir)
        self.agent = None
        if self.llm:
            self.agent = TaskAgent(self.llm, self.file_manager)
        self.project_id = project_id
    
    def run(self):
        """Run the CLI application."""
        parser = argparse.ArgumentParser(description="CortexPropel - AI-powered task management")
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Add task command
        add_parser = subparsers.add_parser("add", help="Add a new task")
        add_parser.add_argument("task", help="Task description")
        add_parser.add_argument("--project", help="Project ID", default=None)
        
        # Update task command
        update_parser = subparsers.add_parser("update", help="Update a task")
        update_parser.add_argument("task_id", help="Task ID")
        update_parser.add_argument("--status", help="New status")
        update_parser.add_argument("--progress", type=int, help="Progress percentage")
        update_parser.add_argument("--priority", help="New priority")
        update_parser.add_argument("--project", help="Project ID", default=None)
        
        # List tasks command
        list_parser = subparsers.add_parser("list", help="List tasks")
        list_parser.add_argument("--status", help="Filter by status")
        list_parser.add_argument("--priority", help="Filter by priority")
        list_parser.add_argument("--project", help="Project ID", default=None)
        
        # Query task command
        query_parser = subparsers.add_parser("query", help="Query tasks using natural language")
        query_parser.add_argument("query", help="Natural language query")
        query_parser.add_argument("--project", help="Project ID", default=None)
        
        # Delete task command
        delete_parser = subparsers.add_parser("delete", help="Delete a task")
        delete_parser.add_argument("task_id", help="Task ID")
        delete_parser.add_argument("--project", help="Project ID", default=None)
        
        # Decompose task command
        decompose_parser = subparsers.add_parser("decompose", help="Decompose a task into subtasks")
        decompose_parser.add_argument("task_id", help="Task ID")
        decompose_parser.add_argument("--project", help="Project ID", default=None)
        
        # Interactive mode command
        interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
        interactive_parser.add_argument("--project", help="Project ID", default=None)
        
        # Summary command
        summary_parser = subparsers.add_parser("summary", help="Show project summary")
        summary_parser.add_argument("--project", help="Project ID", default=None)
        
        # LLM management commands
        llm_subparsers = subparsers.add_parser("llm", help="Manage LLM provider configurations")
        llm_subparsers = llm_subparsers.add_subparsers(dest="llm_command", help="LLM commands")
        
        # LLM list providers command
        llm_subparsers.add_parser("list", help="List all supported LLM providers")
        
        # LLM current config command
        llm_subparsers.add_parser("current", help="Show current LLM provider configuration")
        
        # LLM configure command
        configure_parser = llm_subparsers.add_parser("configure", help="Configure LLM provider")
        configure_parser.add_argument("provider", help="LLM provider name")
        configure_parser.add_argument("--model", help="Model name")
        configure_parser.add_argument("--api-key", help="API key")
        configure_parser.add_argument("--api-base", help="API base URL")
        configure_parser.add_argument("--api-version", help="API version")
        configure_parser.add_argument("--temperature", type=float, help="Temperature")
        configure_parser.add_argument("--max-tokens", type=int, help="Maximum tokens")
        
        # LLM models command
        models_parser = llm_subparsers.add_parser("models", help="List available models for a provider")
        models_parser.add_argument("provider", help="LLM provider name")
        
        # LLM test command
        test_parser = llm_subparsers.add_parser("test", help="Test connection to an LLM provider")
        test_parser.add_argument("provider", help="LLM provider name")
        
        # Parse arguments
        args = parser.parse_args()
        
        # Handle commands
        if args.command == "add":
            self._add_task(args.task, args.project)
        elif args.command == "update":
            self._update_task(args.task_id, args.status, args.progress, args.priority, args.project)
        elif args.command == "list":
            self._list_tasks(args.status, args.priority, args.project)
        elif args.command == "query":
            self._query_tasks(args.query, args.project)
        elif args.command == "delete":
            self._delete_task(args.task_id, args.project)
        elif args.command == "decompose":
            self._decompose_task(args.task_id, args.project)
        elif args.command == "interactive":
            self._start_interactive_mode(args.project)
        elif args.command == "summary":
            self._show_summary(args.project)
        elif args.command == "llm":
            if args.llm_command == "list":
                self._list_llm_providers()
            elif args.llm_command == "current":
                self._show_llm_config()
            elif args.llm_command == "configure":
                self._configure_llm(args.provider, args.model, args.api_key, 
                                   args.api_base, args.api_version, 
                                   args.temperature, args.max_tokens)
            elif args.llm_command == "models":
                self._list_llm_models(args.provider)
            elif args.llm_command == "test":
                self._test_llm_connection(args.provider)
            else:
                parser.print_help()
        else:
            parser.print_help()
    
    def _add_task(self, task_description: str, project_id: Optional[str] = None):
        """Add a new task.
        
        Args:
            task_description: Description of the task to add
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        input_text = f"Create a task: {task_description}"
        
        result = self.agent.run(input_text, project_id)
        print(result.get("response", "No response"))
    
    def _update_task(self, task_id: str, status: Optional[str] = None, 
                    progress: Optional[int] = None, priority: Optional[str] = None,
                    project_id: Optional[str] = None):
        """Update a task.
        
        Args:
            task_id: ID of the task to update
            status: New status
            progress: New progress
            priority: New priority
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        input_text = f"Update task {task_id}"
        
        if status:
            input_text += f" status: {status}"
        if progress is not None:
            input_text += f" progress: {progress}%"
        if priority:
            input_text += f" priority: {priority}"
        
        result = self.agent.run(input_text, project_id)
        print(result.get("response", "No response"))
    
    def _list_tasks(self, status: Optional[str] = None, priority: Optional[str] = None,
                   project_id: Optional[str] = None):
        """List tasks.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        input_text = "Show tasks"
        
        if status:
            input_text += f" with status: {status}"
        if priority:
            input_text += f" with priority: {priority}"
        
        result = self.agent.run(input_text, project_id)
        
        # Print response
        print(result.get("response", "No response"))
        
        # If there are query results, print them
        if "query_results" in result:
            tasks = result["query_results"]
            if tasks:
                print("\nTasks:")
                for task in tasks:
                    status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(task.status.value, "❓")
                    priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(task.priority.value, "⚪")
                    
                    print(f"{status_emoji} {priority_emoji} [{task.id}] {task.title}")
                    if task.description:
                        print(f"   Description: {task.description}")
                    if task.due_date:
                        print(f"   Due: {task.due_date.strftime('%Y-%m-%d')}")
                    if task.progress > 0:
                        print(f"   Progress: {task.progress}%")
                    print()
    
    def _query_tasks(self, query: str, project_id: Optional[str] = None):
        """Query tasks using natural language.
        
        Args:
            query: Natural language query
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        
        result = self.agent.run(query, project_id)
        
        # Print response
        print(result.get("response", "No response"))
        
        # If there are query results, print them
        if "query_results" in result:
            tasks = result["query_results"]
            if tasks:
                print("\nTasks:")
                for task in tasks:
                    status_emoji = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(task.status.value, "❓")
                    priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(task.priority.value, "⚪")
                    
                    print(f"{status_emoji} {priority_emoji} [{task.id}] {task.title}")
                    if task.description:
                        print(f"   Description: {task.description}")
                    if task.due_date:
                        print(f"   Due: {task.due_date.strftime('%Y-%m-%d')}")
                    if task.progress > 0:
                        print(f"   Progress: {task.progress}%")
                    print()
    
    def _delete_task(self, task_id: str, project_id: Optional[str] = None):
        """Delete a task.
        
        Args:
            task_id: ID of the task to delete
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        input_text = f"Delete task {task_id}"
        
        result = self.agent.run(input_text, project_id)
        print(result.get("response", "No response"))
    
    def _decompose_task(self, task_id: str, project_id: Optional[str] = None):
        """Decompose a task into subtasks.
        
        Args:
            task_id: ID of the task to decompose
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        input_text = f"Decompose task {task_id} into subtasks"
        
        result = self.agent.run(input_text, project_id)
        print(result.get("response", "No response"))
    
    def _start_interactive_mode(self, project_id: Optional[str] = None):
        """Start interactive mode.
        
        Args:
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        print("Interactive mode is not yet implemented.")
        print("Please use the CLI commands instead.")
        print("Run 'python -m src.cortex_propel.cli.main --help' for available commands.")
    
    def _show_summary(self, project_id: Optional[str] = None):
        """Show project summary.
        
        Args:
            project_id: Optional project ID
        """
        project_id = project_id or self.project_id
        input_text = "Show project summary"
        
        result = self.agent.run(input_text, project_id)
        print(result.get("response", "No response"))
    
    def _list_llm_providers(self):
        """List all supported LLM providers."""
        from ..llm import LLMProviderFactory
        providers = LLMProviderFactory.get_supported_providers()
        
        print("Supported LLM providers:")
        for provider in providers:
            print(f"  - {provider}")
    
    def _show_llm_config(self):
        """Show current LLM provider configuration."""
        print("Current LLM configuration:")
        print(f"  Provider: {self.settings.llm.provider}")
        print(f"  Model: {self.settings.llm.model}")
        print(f"  Temperature: {self.settings.llm.temperature}")
        print(f"  Max Tokens: {self.settings.llm.max_tokens}")
        
        if hasattr(self.settings.llm, 'api_base') and self.settings.llm.api_base:
            print(f"  API Base: {self.settings.llm.api_base}")
        
        if hasattr(self.settings.llm, 'api_version') and self.settings.llm.api_version:
            print(f"  API Version: {self.settings.llm.api_version}")
        
        # Don't print the API key for security reasons
        print("  API Key: [REDACTED]")
    
    def _configure_llm(self, provider: str, model: Optional[str] = None, 
                      api_key: Optional[str] = None, api_base: Optional[str] = None,
                      api_version: Optional[str] = None, temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None):
        """Configure LLM provider.
        
        Args:
            provider: LLM provider name
            model: Model name
            api_key: API key
            api_base: API base URL
            api_version: API version
            temperature: Temperature
            max_tokens: Maximum tokens
        """
        from ..llm import LLMProviderFactory
        
        # Check if provider is supported
        supported_providers = LLMProviderFactory.get_supported_providers()
        if provider not in supported_providers:
            print(f"Error: Provider '{provider}' is not supported.")
            print(f"Supported providers: {', '.join(supported_providers)}")
            return
        
        # Update settings
        self.settings.llm.provider = provider
        
        if model:
            self.settings.llm.model = model
        
        if api_key:
            self.settings.llm.api_key = api_key
        
        if api_base:
            self.settings.llm.api_base = api_base
        
        if api_version:
            self.settings.llm.api_version = api_version
        
        if temperature is not None:
            self.settings.llm.temperature = temperature
        
        if max_tokens is not None:
            self.settings.llm.max_tokens = max_tokens
        
        # Save settings
        from ..config.settings import save_settings
        save_settings(self.settings)
        
        # Recreate LLM instance
        self.llm = LLMProviderFactory.create_llm(self.settings.llm)
        
        # Update agent if it exists
        if self.agent:
            self.agent.llm = self.llm
        else:
            # Create agent if it doesn't exist
            self.agent = TaskAgent(self.llm, self.file_manager)
        
        print(f"LLM provider configured successfully: {provider}")
    
    def _list_llm_models(self, provider: str):
        """List available models for a provider.
        
        Args:
            provider: LLM provider name
        """
        from ..llm import LLMProviderFactory
        
        # Check if provider is supported
        supported_providers = LLMProviderFactory.get_supported_providers()
        if provider not in supported_providers:
            print(f"Error: Provider '{provider}' is not supported.")
            print(f"Supported providers: {', '.join(supported_providers)}")
            return
        
        # Get available models
        models = LLMProviderFactory.get_available_models(provider)
        
        print(f"Available models for {provider}:")
        for model in models:
            print(f"  - {model}")
    
    def _test_llm_connection(self, provider: str):
        """Test connection to an LLM provider.
        
        Args:
            provider: LLM provider name
        """
        from ..llm import LLMProviderFactory
        
        # Check if provider is supported
        supported_providers = LLMProviderFactory.get_supported_providers()
        if provider not in supported_providers:
            print(f"Error: Provider '{provider}' is not supported.")
            print(f"Supported providers: {', '.join(supported_providers)}")
            return
        
        # Create a temporary LLM instance for testing
        temp_settings = self.settings.llm
        temp_settings.provider = provider
        
        try:
            llm = LLMProviderFactory.create_llm(temp_settings)
            
            # Test with a simple prompt
            response = llm.invoke("Hello, this is a test.")
            
            print(f"Connection to {provider} successful!")
            print(f"Response: {response.content[:100]}...")
        except Exception as e:
            print(f"Error connecting to {provider}: {str(e)}")


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CortexPropel - AI-powered task management")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--project", help="Default project ID")
    
    args, remaining_args = parser.parse_known_args()
    
    # Check if the command is an LLM command that doesn't need an LLM instance
    is_llm_command = False
    if remaining_args and len(remaining_args) > 0:
        if remaining_args[0] == "llm":
            is_llm_command = True
        elif remaining_args[0] == "--help" or remaining_args[0] == "-h":
            is_llm_command = True  # Help command doesn't need LLM
    
    # Initialize CLI with or without LLM instance
    create_llm = not is_llm_command
    cli = CLI(args.config, args.project, create_llm)
    
    # Run CLI with remaining arguments
    sys.argv = [sys.argv[0]] + remaining_args
    cli.run()


if __name__ == "__main__":
    main()