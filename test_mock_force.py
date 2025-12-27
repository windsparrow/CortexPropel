#!/usr/bin/env python3
"""
Test script to check environment and force MockLLM usage.
"""
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set environment variables to force mock usage
os.environ["MODEL_API_KEY"] = ""
os.environ["MODEL_NAME"] = "mock_model"

from task_manager import TaskManager
from llm_client import LLMClient

def test_mock_llm():
    print("=== Testing MockLLM Forcing ===\n")
    
    # Test LLMClient directly
    print("1. Testing LLMClient with forced mock...")
    llm_client = LLMClient()
    
    print(f"LLM type: {type(llm_client.llm)}")
    print(f"LLM class: {llm_client.llm.__class__.__name__}")
    
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
    
    print("\n2. Testing task processing...")
    try:
        result = llm_client.process_task_input(test_tree, "下午3点去买菜")
        print("Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        subtask_count = len(result.get("subtasks", []))
        print(f"\nSubtask count: {subtask_count}")
        
        if subtask_count > 0:
            print("✓ MockLLM is working correctly!")
        else:
            print("✗ MockLLM is still not working")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mock_llm()