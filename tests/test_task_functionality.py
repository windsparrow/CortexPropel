#!/usr/bin/env python3
"""
Simple test script for CortexPropel task creation and decomposition functionality.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from langchain_openai import ChatOpenAI
from cortex_propel.agent import TaskAgent
from cortex_propel.storage.file_manager import FileManager
from cortex_propel.config.settings import load_settings


def test_task_creation():
    """Test task creation functionality."""
    print("Testing task creation...")
    
    # Load settings
    settings = load_settings()
    
    # Initialize file manager
    file_manager = FileManager(settings)
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens
    )
    
    # Initialize agent
    agent = TaskAgent(llm, file_manager)
    
    # Test task creation
    test_inputs = [
        "Create a task to finish the project report by Friday",
        "Add task: Prepare presentation for the client meeting #work",
        "New task: Call the dentist to schedule an appointment, priority: high"
    ]
    
    for input_text in test_inputs:
        print(f"\nInput: {input_text}")
        result = agent.run(input_text)
        print(f"Response: {result.get('response', 'No response')}")
        
        # Check if task was created
        if "task" in result:
            task = result["task"]
            print(f"Created task: {task.title} (ID: {task.id})")
            print(f"Description: {task.description}")
            print(f"Priority: {task.priority}")
            print(f"Due date: {task.due_date}")
            print(f"Tags: {task.tags}")


def test_task_decomposition():
    """Test task decomposition functionality."""
    print("\n\nTesting task decomposition...")
    
    # Load settings
    settings = load_settings()
    
    # Initialize file manager
    file_manager = FileManager(settings)
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens
    )
    
    # Initialize agent
    agent = TaskAgent(llm, file_manager)
    
    # First, create a task to decompose
    create_result = agent.run("Create a task: Plan and execute a marketing campaign")
    
    if "task" in create_result:
        task_id = create_result["task"].id
        print(f"Created task for decomposition: {task_id}")
        
        # Now decompose the task
        decompose_result = agent.run(f"Decompose task {task_id}")
        print(f"Decomposition response: {decompose_result.get('response', 'No response')}")
        
        # Check if subtasks were created
        if "task" in decompose_result:
            task = decompose_result["task"]
            if task.subtasks:
                print(f"Created {len(task.subtasks)} subtasks:")
                for subtask_id in task.subtasks:
                    subtask = file_manager.load_task(subtask_id)
                    if subtask:
                        print(f"  - {subtask.title} (ID: {subtask.id})")
                        print(f"    Description: {subtask.description}")
                        print(f"    Estimated duration: {subtask.estimated_duration} minutes")
            else:
                print("No subtasks were created")
    else:
        print("Failed to create task for decomposition")


def test_task_query():
    """Test task query functionality."""
    print("\n\nTesting task query...")
    
    # Load settings
    settings = load_settings()
    
    # Initialize file manager
    file_manager = FileManager(settings)
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens
    )
    
    # Initialize agent
    agent = TaskAgent(llm, file_manager)
    
    # Test queries
    test_queries = [
        "Show all pending tasks",
        "Find tasks with high priority",
        "What tasks do I have?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = agent.run(query)
        print(f"Response: {result.get('response', 'No response')}")
        
        # Check if query results were returned
        if "query_results" in result:
            tasks = result["query_results"]
            if tasks:
                print(f"Found {len(tasks)} tasks:")
                for task in tasks:
                    print(f"  - {task.title} (ID: {task.id}, Status: {task.status}, Priority: {task.priority})")


if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    print("CortexPropel Test Script")
    print("=" * 50)
    
    try:
        test_task_creation()
        test_task_decomposition()
        test_task_query()
        
        print("\n\nAll tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)