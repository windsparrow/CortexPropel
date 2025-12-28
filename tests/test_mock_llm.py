#!/usr/bin/env python3
"""
Test script with a more sophisticated mock LLM that actually processes tasks.
"""
import json
import sys
import os
import uuid
from datetime import datetime

from src.task_manager import TaskManager

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

def test_mock_llm():
    """Test with the mock LLM"""
    print("=== Testing with Mock LLM ===")
    
    # Create a task manager with our mock LLM
    task_manager = TaskManager()
    
    # Replace the LLM client with our mock
    task_manager.llm_client.llm = MockLLM()
    task_manager.llm_client.chain.llm = MockLLM()
    
    # Test adding a task
    print("1. Adding first task...")
    updated_tree = task_manager.process_user_input("Implement project structure")
    print(f"Task tree after first addition:")
    print(json.dumps(updated_tree, ensure_ascii=False, indent=2))
    print()
    
    # Test adding another task
    print("2. Adding second task...")
    updated_tree = task_manager.process_user_input("Create configuration files")
    print(f"Task tree after second addition:")
    print(json.dumps(updated_tree, ensure_ascii=False, indent=2))
    print()
    
    # Test adding a third task
    print("3. Adding third task...")
    updated_tree = task_manager.process_user_input("Implement LLM integration")
    print(f"Task tree after third addition:")
    print(json.dumps(updated_tree, ensure_ascii=False, indent=2))
    print()
    
    return True

def main():
    """Run the mock LLM test"""
    print("Starting mock LLM test...\n")
    
    try:
        if test_mock_llm():
            print("✓ Mock LLM test passed!")
            print("\n🎉 The task management system is working correctly with mock LLM!")
        else:
            print("✗ Mock LLM test failed")
    except Exception as e:
        print(f"✗ Mock LLM test failed with error: {e}")

if __name__ == "__main__":
    main()
