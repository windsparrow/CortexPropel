#!/usr/bin/env python3
"""
Test UUID assignment for new tasks by comparing with existing database tasks.
"""

import json
import uuid
from src.task_manager import TaskManager


def test_uuid_assignment():
    """Test UUID assignment for new tasks."""
    print("=== Testing UUID Assignment for New Tasks ===\n")
    
    # Initialize task manager
    task_manager = TaskManager()
    
    # Reset to clean state
    task_manager.reset_task_tree()
    print("✓ Reset task tree")
    
    # Add some initial tasks to the database
    print("\n1. Adding initial tasks to database...")
    
    # Create initial task tree with some tasks
    initial_tree = {
        "id": "root",
        "title": "Root Task",
        "subtasks": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Existing task with UUID",
                "description": "This task already has a valid UUID"
            },
            {
                "id": "existing-simple-1",
                "title": "Existing task with simple ID",
                "description": "This task has a simple ID that should be converted to UUID"
            }
        ]
    }
    
    # Save initial tree (this will sync to database)
    task_manager.save_task_tree(initial_tree)
    print("✓ Saved initial task tree with 2 tasks")
    
    # Verify tasks are in database
    all_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Found {len(all_tasks)} tasks in database")
    for task in all_tasks:
        print(f"  - Task ID: {task['id']}, Title: {task['title']}")
    
    # Now simulate LLM returning new tasks
    print("\n2. Testing with new tasks from LLM...")
    
    # Simulate what LLM might return - mix of existing and new tasks
    simulated_llm_response = {
        "id": "root",
        "title": "Root Task",
        "subtasks": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",  # Existing UUID - should preserve
                "title": "Existing task with UUID",
                "description": "This task already has a valid UUID"
            },
            {
                "id": "existing-simple-1",  # Existing simple ID - should convert to UUID
                "title": "Existing task with simple ID",
                "description": "This task has a simple ID that should be converted to UUID"
            },
            {
                "id": "new-task-1",  # New simple ID - should get UUID
                "title": "New task 1",
                "description": "This is a completely new task"
            },
            {
                "id": "new-task-2",  # New simple ID - should get UUID
                "title": "New task 2",
                "description": "Another new task",
                "subtasks": [
                    {
                        "id": "new-subtask-1",  # New subtask - should get UUID
                        "title": "New subtask",
                        "description": "A new subtask"
                    }
                ]
            }
        ]
    }
    
    print("\n3. Processing new task tree with UUID assignment...")
    
    # Test the UUID assignment
    processed_tree = task_manager._assign_uuids_to_new_tasks(simulated_llm_response)
    
    print("✓ Processed task tree:")
    for i, subtask in enumerate(processed_tree['subtasks']):
        original_id = simulated_llm_response['subtasks'][i].get('id')
        processed_id = subtask.get('id')
        
        if original_id != processed_id:
            print(f"  Task {i+1}: {original_id} → {processed_id} ✓ (UUID assigned)")
        else:
            print(f"  Task {i+1}: {processed_id} ✓ (preserved)")
        
        # Check subtasks
        if subtask.get('subtasks'):
            for j, subsubtask in enumerate(subtask['subtasks']):
                orig_sub_id = simulated_llm_response['subtasks'][i]['subtasks'][j].get('id')
                proc_sub_id = subsubtask.get('id')
                if orig_sub_id != proc_sub_id:
                    print(f"    Subtask {j+1}: {orig_sub_id} → {proc_sub_id} ✓ (UUID assigned)")
                else:
                    print(f"    Subtask {j+1}: {proc_sub_id} ✓ (preserved)")
    
    # Verify all IDs are valid UUIDs (except root)
    print("\n4. Final verification:")
    all_valid = True
    for i, subtask in enumerate(processed_tree['subtasks']):
        task_id = subtask.get('id')
        if task_id and not task_manager._is_valid_uuid(task_id):
            print(f"  ✗ Invalid UUID found: {task_id}")
            all_valid = False
        else:
            print(f"  ✓ Valid UUID: {task_id}")
        
        if subtask.get('subtasks'):
            for j, subsubtask in enumerate(subtask['subtasks']):
                sub_id = subsubtask.get('id')
                if sub_id and not task_manager._is_valid_uuid(sub_id):
                    print(f"    ✗ Invalid subtask UUID: {sub_id}")
                    all_valid = False
                else:
                    print(f"    ✓ Valid subtask UUID: {sub_id}")
    
    if all_valid:
        print("\n✅ All tasks have valid UUIDs!")
    else:
        print("\n❌ Some tasks have invalid UUIDs!")
    
    # Test the complete workflow
    print("\n5. Testing complete workflow...")
    
    # Save the processed tree
    task_manager.save_task_tree(processed_tree)
    print("✓ Saved processed tree")
    
    # Load it back and verify
    loaded_tree = task_manager.load_task_tree()
    print("✓ Loaded tree back")
    
    # Check database again
    final_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Final database has {len(final_tasks)} tasks")
    for task in final_tasks:
        print(f"  - Task ID: {task['id']}, Title: {task['title']}")
    
    print("\n=== UUID Assignment Test Complete ===")
    
    if all_valid and len(final_tasks) == 4:  # Should have 4 tasks total
        print("✅ UUID assignment working correctly!")
        print("✅ New tasks get UUIDs assigned!")
        print("✅ Existing tasks are preserved!")
        print("✅ Database synchronization working!")
    else:
        print("❌ Some issues found with UUID assignment!")


if __name__ == "__main__":
    test_uuid_assignment()