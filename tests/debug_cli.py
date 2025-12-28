#!/usr/bin/env python3
"""
Debug version of the CLI to test task addition.
"""
import sys
import os
import json

from src.task_manager import TaskManager

def debug_cli():
    print("=== Debug CLI Test ===\n")
    
    # Initialize task manager
    task_manager = TaskManager()
    
    print("1. Initial task tree:")
    initial_tree = task_manager.get_task_tree()
    print(json.dumps(initial_tree, ensure_ascii=False, indent=2))
    print()
    
    print("2. Adding task '准备项目文档'...")
    try:
        updated_tree = task_manager.process_user_input("准备项目文档")
        print("Updated task tree:")
        print(json.dumps(updated_tree, ensure_ascii=False, indent=2))
        print()
        
        print("3. Verifying task was saved...")
        saved_tree = task_manager.get_task_tree()
        print("Saved task tree:")
        print(json.dumps(saved_tree, ensure_ascii=False, indent=2))
        print()
        
        subtask_count = len(saved_tree.get("subtasks", []))
        print(f"Subtask count: {subtask_count}")
        
        if subtask_count > 0:
            print("✓ Task was successfully added!")
        else:
            print("✗ Task was not added - debugging needed")
            
    except Exception as e:
        print(f"Error adding task: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cli()