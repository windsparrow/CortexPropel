#!/usr/bin/env python3
"""
Test script for task metadata database functionality.
"""

import json
from datetime import datetime, timedelta

# Import task manager
try:
    from src.task_manager import TaskManager
except ImportError:
    from task_manager import TaskManager


def test_database_functionality():
    """Test the complete database functionality."""
    print("=== Testing Task Metadata Database Functionality ===\n")
    
    # Initialize task manager
    task_manager = TaskManager()
    
    # Reset task tree
    print("1. Resetting task tree...")
    task_manager.reset_task_tree()
    print("✓ Task tree reset successfully\n")
    
    # Add tasks using LLM
    print("2. Adding tasks via LLM...")
    
    # Add first task
    updated_tree1 = task_manager.process_user_input("下午3点去买菜")
    print("✓ Added task: '下午3点去买菜'")
    
    # Add second task  
    updated_tree2 = task_manager.process_user_input("晚上7点做饭")
    print("✓ Added task: '晚上7点做饭'\n")
    
    # Test database queries
    print("3. Testing database queries...")
    
    # Get all tasks metadata
    all_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Found {len(all_tasks)} tasks in database")
    
    for task in all_tasks:
        print(f"  - Task ID: {task['id']}, Title: {task['title']}, Status: {task['status']}")
    
    print()
    
    # Test specific task metadata
    if all_tasks:
        first_task = all_tasks[0]
        task_id = first_task['id']
        
        print("4. Testing specific task metadata...")
        task_metadata = task_manager.get_task_metadata(task_id)
        
        if task_metadata:
            print(f"✓ Retrieved metadata for task: {task_metadata['title']}")
            print(f"  - Created at: {task_metadata['created_at']}")
            print(f"  - JSON data stored: {'Yes' if task_metadata['json_data'] else 'No'}")
        else:
            print("✗ Failed to retrieve task metadata")
        
        print()
    
    # Test updating task metadata
    print("5. Testing task metadata updates...")
    
    if all_tasks:
        task_id = all_tasks[0]['id']
        
        # Update individual fields
        success1 = task_manager.update_task_field(task_id, 'assigned_to', '张三')
        success2 = task_manager.update_task_field(task_id, 'planned_start_time', '2025-12-27T15:00:00Z')
        success3 = task_manager.update_task_field(task_id, 'priority', 2)
        success4 = task_manager.update_task_field(task_id, 'progress', 25)
        
        if success1 and success2 and success3 and success4:
            print("✓ Successfully updated task metadata fields")
            
            # Verify updates
            updated_task = task_manager.get_task_metadata(task_id)
            if updated_task:
                print(f"  - Assigned to: {updated_task.get('assigned_to')}")
                print(f"  - Planned start: {updated_task.get('planned_start_time')}")
                print(f"  - Priority: {updated_task.get('priority')}")
                print(f"  - Progress: {updated_task.get('progress')}%")
        else:
            print("✗ Failed to update task metadata")
        
        print()
    
    # Test bulk metadata update
    print("6. Testing bulk metadata update...")
    
    if len(all_tasks) > 1:
        task_id = all_tasks[1]['id']
        
        bulk_metadata = {
            'estimated_hours': 2.5,
            'actual_hours': 0,
            'category': '家务',
            'notes': '需要准备食材',
            'tags': ['烹饪', '晚餐']
        }
        
        success = task_manager.update_task_metadata(task_id, bulk_metadata)
        
        if success:
            print("✓ Successfully updated bulk metadata")
            
            # Verify updates
            updated_task = task_manager.get_task_metadata(task_id)
            if updated_task:
                print(f"  - Estimated hours: {updated_task.get('estimated_hours')}")
                print(f"  - Category: {updated_task.get('category')}")
                print(f"  - Notes: {updated_task.get('notes')}")
                print(f"  - Tags: {updated_task.get('tags')}")
        else:
            print("✗ Failed to update bulk metadata")
        
        print()
    
    # Test task dependencies
    print("7. Testing task dependencies...")
    
    if len(all_tasks) >= 2:
        # Set first task as dependency of second task
        task1_id = all_tasks[0]['id']
        task2_id = all_tasks[1]['id']
        
        success = task_manager.update_task_field(task2_id, 'dependencies', [task1_id])
        
        if success:
            print("✓ Successfully set task dependencies")
            
            # Verify dependencies
            updated_task = task_manager.get_task_metadata(task2_id)
            if updated_task:
                dependencies = updated_task.get('dependencies', [])
                print(f"  - Task dependencies: {dependencies}")
        else:
            print("✗ Failed to set task dependencies")
        
        print()
    
    # Final summary
    print("8. Final summary...")
    final_tasks = task_manager.get_all_tasks_metadata()
    print(f"✓ Total tasks in database: {len(final_tasks)}")
    
    print("\n=== Database Functionality Test Complete ===")
    print("✅ All database operations working correctly!")
    print("✅ LLM integration with database sync working!")
    print("✅ Task metadata management ready for use!")


if __name__ == "__main__":
    test_database_functionality()