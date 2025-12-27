#!/usr/bin/env python3
"""Test script using direct ByteDance API integration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
from src.config import config

def test_bytedance_api():
    """Test direct ByteDance API integration."""
    print("=== Testing Direct ByteDance API ===\n")
    
    # API configuration
    api_key = config.MODEL_API_KEY
    base_url = config.MODEL_BASE_URL
    model = config.MODEL_NAME
    
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:10]}...")
    
    # Test task tree
    test_tree = {
        "id": "root",
        "title": "Root Task",
        "description": "Main project task",
        "status": "pending",
        "created_at": "2025-12-27T10:00:00Z",
        "updated_at": "2025-12-27T10:00:00Z",
        "subtasks": []
    }
    
    # Create prompt
    prompt = f"""
    You are a task management assistant. Your job is to help users organize their tasks into a hierarchical tree structure.
    
    Current Task Tree:
    {json.dumps(test_tree, ensure_ascii=False, indent=2)}
    
    User's New Task:
    下午3点去买菜
    
    Instructions:
    1. Analyze the current task tree structure
    2. Understand the user's new task request
    3. Update the task tree by adding, modifying, or organizing tasks as appropriate
    4. Ensure the task tree remains a valid JSON structure with proper nesting
    5. Only output the complete updated task tree in JSON format, nothing else
    6. Each task must have: id, title, description, status, created_at, updated_at, and subtasks fields
    7. Generate unique IDs for new tasks
    8. Set appropriate status (pending, in_progress, completed) for tasks
    9. Update timestamps for modified tasks
    
    Output Format:
    {{"id": "root", "title": "Root Task", "description": "Main project task", "status": "pending", "created_at": "2025-12-27T10:00:00Z", "updated_at": "2025-12-27T10:00:00Z", "subtasks": [...]}}
    """
    
    # API request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(f"{base_url}/chat/completions", headers=headers, json=data)
        print(f"\nAPI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # Extract content
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"\nGenerated content:")
                print(content)
                
                # Try to parse JSON
                if "{" in content:
                    json_start = content.index("{")
                    json_end = content.rindex("}") + 1
                    json_str = content[json_start:json_end]
                    task_tree = json.loads(json_str)
                    print(f"\nParsed task tree:")
                    print(json.dumps(task_tree, ensure_ascii=False, indent=2))
                    
                    # Check if task was added
                    subtask_count = len(task_tree.get("subtasks", []))
                    print(f"\nSubtask count: {subtask_count}")
                    
                    if subtask_count > 0:
                        print("✓ New task was successfully added!")
                    else:
                        print("⚠ No new tasks were added")
                        
        else:
            print(f"API Error: {response.status_code}")
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bytedance_api()