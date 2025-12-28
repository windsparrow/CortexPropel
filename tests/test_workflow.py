#!/usr/bin/env python3
"""
Test script to verify the complete task management workflow.
"""
import json
import os
from src.task_manager import TaskManager

# Clean up for fresh test
def clean_test_environment():
    """Clean up test files for fresh start."""
    db_path = "data/tasks.db"
    task_tree_path = "data/task_tree.json"
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✓ Cleaned up existing database")
    
    if os.path.exists(task_tree_path):
        os.remove(task_tree_path)
        print("✓ Cleaned up existing task tree")

def test_workflow():
    print("=== Testing CortexPropel Task Management Workflow ===\n")
    
    # Clean up for fresh test
    clean_test_environment()
    
    # Initialize task manager
    task_manager = TaskManager()
    
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
    
    # Step 4: Add third task
    print("4. Adding third task: 'Write unit tests for task processing'")
    updated_tree_3 = task_manager.process_user_input("Write unit tests for task processing")
    print("Updated task tree after third task:")
    print(json.dumps(updated_tree_3, ensure_ascii=False, indent=2))
    print()
    
    # Step 5: Verify database integration
    print("5. Verifying database integration...")
    all_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Found {len(all_tasks)} tasks in database")
    
    # Check UUID assignment
    valid_uuid_count = 0
    for task in all_tasks:
        task_id = task['id']
        if task_id and task_manager._is_valid_uuid(task_id):
            valid_uuid_count += 1
    
    print(f"✓ {valid_uuid_count} out of {len(all_tasks)} tasks have valid UUIDs")
    
    print("\n=== Workflow Test Complete ===")

if __name__ == "__main__":
    test_workflow()
