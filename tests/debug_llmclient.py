#!/usr/bin/env python3
"""
Debug script to trace the LLMClient process.
"""
import sys
import os
import json

from src.llm_client import LLMClient

def debug_llmclient():
    print("=== Debug LLMClient ===\n")
    
    llm_client = LLMClient()
    
    # Check what type of LLM is being used
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
    
    print("\n1. Testing LLM chain directly...")
    task_tree_json = json.dumps(test_tree, ensure_ascii=False, indent=2)
    
    try:
        # Test the chain directly
        response = llm_client.chain.invoke({
            "current_task_tree": task_tree_json,
            "user_input": "准备项目文档"
        })
        print("Chain response:")
        print(response)
        print()
        
        # Check if response contains JSON
        if "{" in response:
            print("✓ Response contains JSON structure")
            json_start = response.index("{")
            json_end = response.rindex("}") + 1
            response_json = response[json_start:json_end]
            
            try:
                result = json.loads(response_json)
                print("Parsed JSON result:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
                subtask_count = len(result.get("subtasks", []))
                print(f"\nSubtask count: {subtask_count}")
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response JSON: {response_json}")
        else:
            print("✗ Response does not contain JSON")
            
    except Exception as e:
        print(f"Chain error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_llmclient()