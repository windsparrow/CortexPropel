#!/usr/bin/env python3
"""
Test script to verify the complete task management workflow.
"""
import json
import sys
import os
import uuid
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from task_manager import TaskManager

class MockLLM:
    """A mock LLM that actually processes tasks"""
    
    def run(self, **kwargs):
        current_task_tree = json.loads(kwargs.get('current_task_tree', '{}'))
        user_input = kwargs.get('user_input', '')
        
        # Simple task processing logic
        updated_tree = self._process_task(current_task_tree, user_input)
        
        return json.dumps(updated_tree, ensure_ascii=False, indent=2)
    
    def _process_task(self, current_tree: dict, user_input: str) -> dict:
        """Simple task processing logic"""
        if not current_tree:
            return current_tree
        
        # Create a new task based on user input
        new_task = {
            "id": f"task-{uuid.uuid4().hex[:8]}",
            "title": user_input[:50],  # Truncate for title
            "description": user_input,
            "status": "pending",
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "subtasks": []
        }
        
        # Add the task to the root's subtasks
        if "subtasks" not in current_tree:
            current_tree["subtasks"] = []
        
        current_tree["subtasks"].append(new_task)
        current_tree["updated_at"] = datetime.now().isoformat() + "Z"
        
        return current_tree

def test_workflow():
    print("=== Testing CortexPropel Task Management Workflow ===\n")
    
    # Initialize task manager
    task_manager = TaskManager()
    
    # Replace the LLM client with our mock
    task_manager.llm_client.llm = MockLLM()
    task_manager.llm_client.chain.llm = MockLLM()
    
    # Step 1: Reset task tree to initial state
    print("1. Resetting task tree to initial state...")
    initial_tree = task_manager.reset_task_tree()
    print("Initial task tree:")
    print(json.dumps(initial_tree, ensure_ascii=False, indent=2))
    print()
    
    # Step 2: Add first task
    print("2. Adding first task: 'Implement project structure'")
    updated_tree_1 = task_manager.process_user_input("Implement project structure")
    print("Updated task tree after first task:")
    print(json.dumps(updated_tree_1, ensure_ascii=False, indent=2))
    print()
    
    # Step 3: Add second task with context
    print("3. Adding second task: 'Create configuration files and load model settings'")
    updated_tree_2 = task_manager.process_user_input("Create configuration files and load model settings")
    print("Updated task tree after second task:")
    print(json.dumps(updated_tree_2, ensure_ascii=False, indent=2))
    print()
    
    # Step 4: Add third task with more context
    print("4. Adding third task: 'Implement LLM integration with ByteDance model'")
    updated_tree_3 = task_manager.process_user_input("Implement LLM integration with ByteDance model")
    print("Final task tree:")
    print(json.dumps(updated_tree_3, ensure_ascii=False, indent=2))
    print()
    
    print("=== Workflow Test Complete ===")

if __name__ == "__main__":
    test_workflow()
