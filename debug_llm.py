#!/usr/bin/env python3
"""Test script to debug LLM response."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_client import LLMClient
import json

def debug_llm_response():
    """Debug the LLM response to see what's happening."""
    print("=== Debugging LLM Response ===\n")
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Test task processing with debug
    test_tree = {
        "id": "root",
        "title": "Root Task",
        "description": "Main project task",
        "status": "pending",
        "created_at": "2025-12-27T10:00:00Z",
        "updated_at": "2025-12-27T10:00:00Z",
        "subtasks": []
    }
    
    print("Current task tree:")
    print(json.dumps(test_tree, ensure_ascii=False, indent=2))
    
    # Test the chain directly
    task_tree_json = json.dumps(test_tree, ensure_ascii=False, indent=2)
    
    print("\n=== Testing LLM Chain ===")
    print("Input to LLM:")
    print(f"Current task tree: {task_tree_json}")
    print(f"User input: 下午3点去买菜")
    
    try:
        response = llm_client.chain.run(
            current_task_tree=task_tree_json,
            user_input="下午3点去买菜"
        )
        
        print(f"\nRaw LLM response:")
        print(repr(response))
        print(f"\nFormatted response:")
        print(response)
        
        # Check if response contains JSON
        if "{" in response:
            json_start = response.index("{")
            json_end = response.rindex("}") + 1
            response_json = response[json_start:json_end]
            print(f"\nExtracted JSON:")
            print(response_json)
            
            try:
                result = json.loads(response_json)
                print(f"\nParsed result:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
        else:
            print("No JSON found in response")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_llm_response()