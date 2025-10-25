#!/usr/bin/env python3
"""
Example usage of CortexPropel for task management.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.cortex_propel.agent import TaskAgent
from src.cortex_propel.storage.file_manager import FileManager
from src.cortex_propel.config.settings import load_settings
from src.cortex_propel.llm import LLMProviderFactory


def main():
    """Main example function."""
    print("CortexPropel Task Management Example")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key and try again")
        return
    
    # Load settings
    settings = load_settings()
    
    # Initialize file manager
    file_manager = FileManager(settings)
    
    # Initialize LLM using the factory
    llm = LLMProviderFactory.create_llm(settings.llm)
    
    # Initialize agent
    agent = TaskAgent(llm, file_manager)
    
    # Create a project for work tasks
    project_id = "work_example"
    
    print(f"\nWorking with project: {project_id}")
    print("\n1. Creating tasks...")
    
    # Create some example tasks
    task_examples = [
        "Create a presentation for the client meeting next week, priority: high",
        "Review the quarterly financial report, due: 2023-12-15",
        "Schedule team building activity for next month #team #planning",
        "Update project documentation #documentation"
    ]
    
    created_tasks = []
    for example in task_examples:
        print(f"\nCreating task: {example}")
        result = agent.run(example, project_id)
        print(f"Response: {result.get('response', 'No response')}")
        
        if "task" in result:
            task = result["task"]
            created_tasks.append(task.id)
            print(f"Created task with ID: {task.id}")
    
    print("\n\n2. Querying tasks...")
    
    # Query all tasks
    print("\nQuery: Show all tasks")
    result = agent.run("Show all tasks", project_id)
    print(f"Response: {result.get('response', 'No response')}")
    
    # Query high priority tasks
    print("\nQuery: Find tasks with high priority")
    result = agent.run("Find tasks with high priority", project_id)
    print(f"Response: {result.get('response', 'No response')}")
    
    # Query tasks with specific tags
    print("\nQuery: Find tasks tagged with #team")
    result = agent.run("Find tasks tagged with #team", project_id)
    print(f"Response: {result.get('response', 'No response')}")
    
    print("\n\n3. Updating tasks...")
    
    # Update a task status
    if created_tasks:
        task_id = created_tasks[0]
        print(f"\nUpdating task {task_id} status to in progress")
        result = agent.run(f"Update task {task_id} status: in progress", project_id)
        print(f"Response: {result.get('response', 'No response')}")
        
        # Update task progress
        print(f"\nUpdating task {task_id} progress to 50%")
        result = agent.run(f"Update task {task_id} progress: 50%", project_id)
        print(f"Response: {result.get('response', 'No response')}")
    
    print("\n\n4. Decomposing a task...")
    
    # Decompose a task into subtasks
    if created_tasks:
        task_id = created_tasks[1] if len(created_tasks) > 1 else created_tasks[0]
        print(f"\nDecomposing task {task_id}")
        result = agent.run(f"Decompose task {task_id}", project_id)
        print(f"Response: {result.get('response', 'No response')}")
        
        # Show subtasks
        if "task" in result:
            task = result["task"]
            if task.subtasks:
                print(f"Created {len(task.subtasks)} subtasks:")
                for subtask_id in task.subtasks:
                    subtask = file_manager.load_task(subtask_id, project_id)
                    if subtask:
                        print(f"  - {subtask.title} (ID: {subtask_id})")
    
    print("\n\n5. Project summary...")
    
    # Show project summary
    summary = agent.get_project_summary(project_id)
    print(f"Project Summary: {project_id}")
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Pending tasks: {summary['pending_tasks']}")
    print(f"In progress: {summary['in_progress_tasks']}")
    print(f"Completed: {summary['completed_tasks']}")
    print(f"Overdue: {summary['overdue_tasks']}")
    print(f"High priority: {summary['high_priority_tasks']}")
    print(f"Average progress: {summary['average_progress']:.1f}%")
    
    print("\n\n6. Task suggestions...")
    
    # Get task suggestions
    suggestions = agent.get_task_suggestions(project_id)
    if suggestions:
        print("Suggestions:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    
    print("\n\nExample completed successfully!")
    print("\nYou can now use the CLI interface to interact with your tasks:")
    print("  python cortex_propel.py add \"Create a new task\"")
    print("  python cortex_propel.py list")
    print("  python cortex_propel.py chat")


if __name__ == "__main__":
    main()