#!/usr/bin/env python3
"""Test script to verify LLM functionality with real ByteDance Tongyi model."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_client import LLMClient
import json

def test_llm_functionality():
    """Test the LLM functionality with a simple task."""
    print("=== Testing ByteDance Tongyi LLM ===\n")
    
    # Initialize LLM client
    try:
        llm_client = LLMClient()
        print("✓ LLMClient initialized successfully")
        print(f"LLM type: {type(llm_client.llm)}")
        print(f"LLM model: {llm_client.llm.model_name}")
    except Exception as e:
        print(f"✗ Failed to initialize LLMClient: {e}")
        return
    
    # Test task processing
    test_tree = {
        "id": "root",
        "title": "Root Task",
        "description": "Main project task",
        "status": "pending",
        "created_at": "2025-12-27T10:00:00Z",
        "updated_at": "2025-12-27T10:00:00Z",
        "subtasks": []
    }
    
    print("\n=== Testing Task Processing ===")
    print("Current task tree:")
    print(json.dumps(test_tree, ensure_ascii=False, indent=2))
    
    try:
        result = llm_client.process_task_input(test_tree, "下午3点去买菜")
        print("\n✓ Task processing completed")
        print("Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Check if task was added
        subtask_count = len(result.get("subtasks", []))
        print(f"\nSubtask count: {subtask_count}")
        
        if subtask_count > 0:
            print("✓ New task was successfully added!")
            print(f"First subtask: {result['subtasks'][0].get('title', 'No title')}")
        else:
            print("⚠ No new tasks were added - LLM may have returned empty response")
            
    except Exception as e:
        print(f"✗ Task processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_functionality()