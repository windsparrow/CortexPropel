#!/usr/bin/env python3
"""
Test database reset functionality when resetting task tree.
"""

import os
from src.task_manager import TaskManager


def test_reset_with_database():
    """Test that resetting task tree also resets the database."""
    print("=== Testing Task Tree Reset with Database ===\n")
    
    # Initialize task manager
    task_manager = TaskManager()
    
    print("1. Adding some tasks first...")
    
    # Add some tasks
    task_manager.process_user_input("下午3点去买菜")
    task_manager.process_user_input("晚上7点做饭")
    task_manager.process_user_input("准备周末聚会，包括买食材和打扫卫生")
    
    # Check initial state
    initial_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Added {len(initial_tasks)} tasks to database")
    
    task_tree = task_manager.get_task_tree()
    print(f"✓ Task tree has {len(task_tree.get('subtasks', []))} top-level tasks")
    
    print("\n2. Resetting task tree...")
    
    # Reset task tree
    reset_tree = task_manager.reset_task_tree()
    
    print("✓ Task tree reset completed")
    
    # Check database after reset
    remaining_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Database now has {len(remaining_tasks)} tasks")
    
    # Check task tree after reset
    reset_task_tree = task_manager.get_task_tree()
    print(f"✓ Task tree now has {len(reset_task_tree.get('subtasks', []))} top-level tasks")
    
    print("\n3. Verifying reset results...")
    
    # Should only have root task remaining
    non_root_tasks = [task for task in remaining_tasks if task['id'] != 'root']
    
    if len(non_root_tasks) == 0:
        print("✅ Database properly cleared - no tasks remaining")
    else:
        print(f"❌ Database not properly cleared - {len(non_root_tasks)} tasks still exist")
        for task in non_root_tasks:
            print(f"  - Task: {task['title']} (ID: {task['id']})")
    
    # Task tree should be empty except for root
    if len(reset_task_tree.get('subtasks', [])) == 0:
        print("✅ Task tree properly reset - no subtasks")
    else:
        print(f"❌ Task tree not properly reset - {len(reset_task_tree.get('subtasks', []))} subtasks remain")
    
    # Root task should exist
    root_task = next((task for task in remaining_tasks if task['id'] == 'root'), None)
    if root_task:
        print("✅ Root task preserved")
    else:
        print("❌ Root task missing")
    
    print("\n4. Testing that we can add new tasks after reset...")
    
    # Add a new task after reset
    result = task_manager.process_user_input("测试重置后的新任务")
    
    final_tasks = task_manager.get_all_tasks_metadata()
    final_tree = task_manager.get_task_tree()
    
    print(f"✓ Added new task after reset")
    print(f"✓ Database now has {len(final_tasks)} tasks")
    print(f"✓ Task tree now has {len(final_tree.get('subtasks', []))} top-level tasks")
    
    # Verify the new task has proper UUID
    new_task = next((task for task in final_tasks if task['title'] == '测试重置后的新任务'), None)
    if new_task and task_manager._is_valid_uuid(new_task['id']):
        print("✅ New task has valid UUID")
    else:
        print("❌ New task missing or has invalid UUID")
    
    print("\n=== Test Complete ===")
    
    if len(non_root_tasks) == 0 and len(reset_task_tree.get('subtasks', [])) == 0 and new_task and task_manager._is_valid_uuid(new_task['id']):
        print("✅ Reset functionality working correctly!")
        print("✅ Database cleared properly!")
        print("✅ Task tree reset properly!")
        print("✅ Can add new tasks after reset!")
    else:
        print("❌ Some issues with reset functionality!")


if __name__ == "__main__":
    test_reset_with_database()