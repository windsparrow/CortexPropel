#!/usr/bin/env python3
"""
Detailed debug script to trace the task addition process.
"""
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from task_manager import TaskManager
from llm_client import LLMClient

def detailed_debug():
    print("=== Detailed Debug Trace ===\n")
    
    # Test LLMClient directly
    print("1. Testing LLMClient directly...")
    llm_client = LLMClient()
    
    # Create a test task tree
    test_tree = {
        "id": "root",
        "title": "Root Task", 
        "description": "Main project task",
        "status": "pending",
        "created_at": "2025-12-27T10:00:00Z",
        "updated_at": "2025-12-27T10:00:00Z",
        "subtasks": []
    }
    
    print("Input task tree:")
    print(json.dumps(test_tree, ensure_ascii=False, indent=2))
    print()
    
    print("2. Processing task with LLMClient...")
    try:
        result = llm_client.process_task_input(test_tree, "准备项目文档")
        print("LLMClient result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
        
        # Check if subtasks were added
        subtask_count = len(result.get("subtasks", []))
        print(f"Result subtask count: {subtask_count}")
        
        if subtask_count > 0:
            print("✓ LLMClient is working correctly!")
        else:
            print("✗ LLMClient is not adding tasks")
            
    except Exception as e:
        print(f"LLMClient error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing TaskManager...")
    task_manager = TaskManager()
    
    # Reset to ensure clean state
    print("Resetting task tree...")
    task_manager.reset_task_tree()
    
    print("Adding task through TaskManager...")
    try:
        result = task_manager.process_user_input("准备项目文档")
        print("TaskManager result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        subtask_count = len(result.get("subtasks", []))
        print(f"TaskManager subtask count: {subtask_count}")
        
    except Exception as e:
        print(f"TaskManager error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_debug()