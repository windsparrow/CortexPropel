#!/usr/bin/env python3
"""
Test UUID generation with LLM that returns non-UUID IDs.
"""

from src.task_manager import TaskManager

def test_llm_non_uuid_scenario():
    """Test when LLM returns tasks with simple IDs."""
    print("=== LLM Non-UUID Scenario Test ===\n")
    
    task_manager = TaskManager()
    
    # Reset to clean state
    task_manager.reset_task_tree()
    print("✓ Reset task tree")
    
    # Simulate what would happen if LLM returned tasks with simple IDs
    print("\n1. Testing direct task tree with simple IDs...")
    
    # Create a task tree like what LLM might return
    simulated_llm_response = {
        "id": "root",
        "title": "Root Task",
        "subtasks": [
            {
                "id": "task-1",  # Simple ID - should get UUID
                "title": "First task",
                "description": "Task with simple ID"
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID - should preserve
                "title": "Second task", 
                "description": "Task with UUID"
            },
            {
                "id": "simple-123",  # Simple ID - should get UUID
                "title": "Third task",
                "description": "Another task with simple ID",
                "subtasks": [
                    {
                        "id": "subtask-456",  # Simple ID - should get UUID
                        "title": "Subtask",
                        "description": "Nested task with simple ID"
                    }
                ]
            }
        ]
    }
    
    # Process through our UUID assignment
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
    
    print("\n2. Testing with actual task manager save/load...")
    
    # Save the processed tree
    task_manager.save_task_tree(processed_tree)
    print("✓ Saved processed tree")
    
    # Load it back
    loaded_tree = task_manager.load_task_tree()
    print("✓ Loaded tree back")
    
    # Verify all IDs are valid UUIDs (except root)
    print("\n3. Final verification:")
    all_valid = True
    for subtask in loaded_tree['subtasks']:
        task_id = subtask.get('id')
        if task_id and not task_manager._is_valid_uuid(task_id):
            print(f"  ✗ Invalid UUID found: {task_id}")
            all_valid = False
        else:
            print(f"  ✓ Valid UUID: {task_id}")
        
        if subtask.get('subtasks'):
            for subsubtask in subtask['subtasks']:
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

if __name__ == "__main__":
    test_llm_non_uuid_scenario()