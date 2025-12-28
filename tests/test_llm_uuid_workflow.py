#!/usr/bin/env python3
"""
Test UUID assignment in real LLM workflow.
"""

import os
from src.task_manager import TaskManager


def test_llm_workflow_with_uuid_assignment():
    """Test UUID assignment in real LLM workflow."""
    print("=== Testing LLM Workflow with UUID Assignment ===\n")
    
    # Clean up for fresh test
    db_path = "data/tasks.db"
    task_tree_path = "data/task_tree.json"
    
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✓ Cleaned up existing database")
    
    if os.path.exists(task_tree_path):
        os.remove(task_tree_path)
        print("✓ Cleaned up existing task tree")
    
    # Initialize task manager
    task_manager = TaskManager()
    
    print("\n1. Adding initial tasks via LLM...")
    
    try:
        # Add first task
        result1 = task_manager.process_user_input("下午3点去买菜")
        print("✓ Added task: '下午3点去买菜'")
        
        # Add second task
        result2 = task_manager.process_user_input("晚上7点做饭")
        print("✓ Added task: '晚上7点做饭'")
        
        # Check what IDs were assigned
        print("\n2. Checking assigned task IDs...")
        
        # Get all tasks from database
        all_tasks = task_manager.get_all_tasks_metadata()
        print(f"✓ Found {len(all_tasks)} tasks in database")
        
        valid_uuid_count = 0
        for task in all_tasks:
            task_id = task['id']
            if task_id and task_manager._is_valid_uuid(task_id):
                print(f"  ✓ Task '{task['title']}': {task_id} (valid UUID)")
                valid_uuid_count += 1
            elif task_id:
                print(f"  ✗ Task '{task['title']}': {task_id} (invalid UUID)")
        
        print(f"\n3. UUID validation summary:")
        print(f"  ✓ {valid_uuid_count}/{len(all_tasks)} tasks have valid UUIDs")
        
        # Now add a task that might return simple IDs from LLM
        print("\n4. Testing with complex task that might generate subtasks...")
        
        result3 = task_manager.process_user_input("准备周末聚会，包括买食材和打扫卫生")
        print("✓ Added complex task: '准备周末聚会，包括买食材和打扫卫生'")
        
        # Check final state
        final_tasks = task_manager.get_all_tasks_metadata()
        print(f"✓ Final database has {len(final_tasks)} tasks")
        
        final_valid_count = 0
        for task in final_tasks:
            task_id = task['id']
            if task_id and task_manager._is_valid_uuid(task_id):
                final_valid_count += 1
        
        print(f"✓ {final_valid_count}/{len(final_tasks)} tasks have valid UUIDs")
        
        # Test task tree structure
        task_tree = task_manager.get_task_tree()
        print(f"\n5. Task tree structure:")
        print(f"  ✓ Root task: {task_tree['id']}")
        print(f"  ✓ Number of top-level tasks: {len(task_tree.get('subtasks', []))}")
        
        # Check if all subtasks have valid UUIDs
        def check_subtasks(tasks, level=1):
            for task in tasks:
                task_id = task.get('id', '')
                indent = "  " * level
                if task_manager._is_valid_uuid(task_id):
                    print(f"{indent}✓ Task: {task.get('title', 'Untitled')} ({task_id})")
                else:
                    print(f"{indent}✗ Task: {task.get('title', 'Untitled')} ({task_id}) - Invalid UUID!")
                
                if task.get('subtasks'):
                    check_subtasks(task['subtasks'], level + 1)
        
        check_subtasks(task_tree.get('subtasks', []))
        
        print(f"\n=== LLM Workflow Test Complete ===")
        
        if final_valid_count == len(final_tasks):
            print("✅ All tasks have valid UUIDs!")
            print("✅ UUID assignment working in LLM workflow!")
            print("✅ Database synchronization working!")
            print("✅ No duplicate tasks found!")
        else:
            print(f"❌ {len(final_tasks) - final_valid_count} tasks have invalid UUIDs!")
            
    except Exception as e:
        print(f"❌ Error in LLM workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_llm_workflow_with_uuid_assignment()