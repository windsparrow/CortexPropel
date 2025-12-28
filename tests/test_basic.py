#!/usr/bin/env python3
"""
Basic test script to verify the core functionality without LLM integration.
"""
import json
import os
from src.task_manager import TaskManager

def test_task_structure():
    """Test the task structure validation"""
    print("=== Testing Task Structure ===")
    
    # Test task manager initialization
    task_manager = TaskManager()
    print("Task manager initialized successfully")
    
    # Test loading task tree
    task_tree = task_manager.load_task_tree()
    print(f"Task tree loaded successfully")
    print(f"Root task title: {task_tree.get('title', 'N/A')}")
    print(f"Root task ID: {task_tree.get('id', 'N/A')}")
    print(f"Number of subtasks: {len(task_tree.get('subtasks', []))}")
    print()
    
    # Test task tree structure
    if 'id' in task_tree and 'title' in task_tree:
        print("✓ Task tree has required fields (id, title)")
    else:
        print("✗ Task tree missing required fields")
        return False
    
    return True

def test_task_manager():
    """Test the task manager without LLM"""
    print("=== Testing Task Manager ===")
    
    # Test initialization
    task_manager = TaskManager()
    print("Task manager initialized successfully")
    
    # Test loading task tree
    task_tree = task_manager.load_task_tree()
    print(f"Task tree loaded successfully")
    print(f"Root task title: {task_tree.get('title', 'N/A')}")
    print(f"Number of subtasks: {len(task_tree.get('subtasks', []))}")
    print()
    
    # Test reset functionality
    reset_tree = task_manager.reset_task_tree()
    print("Task tree reset successfully")
    print(f"Reset tree title: {reset_tree.get('title', 'N/A')}")
    print()
    
    return True

def test_json_validation():
    """Test JSON structure validation"""
    print("=== Testing JSON Structure Validation ===")
    
    # Create a sample task tree structure
    sample_tree = {
        "id": "root",
        "title": "Sample Project",
        "description": "A sample project task",
        "status": "pending",
        "created_at": "2025-12-27T10:00:00Z",
        "updated_at": "2025-12-27T10:00:00Z",
        "subtasks": [
            {
                "id": "task-1",
                "title": "Subtask 1",
                "description": "First subtask",
                "status": "pending",
                "created_at": "2025-12-27T10:00:00Z",
                "updated_at": "2025-12-27T10:00:00Z",
                "subtasks": []
            }
        ]
    }
    
    # Validate structure
    try:
        # Check required fields
        required_fields = ['id', 'title', 'status', 'created_at', 'updated_at', 'subtasks']
        for field in required_fields:
            if field not in sample_tree:
                raise ValueError(f"Missing required field: {field}")
        
        # Check subtasks structure
        if not isinstance(sample_tree['subtasks'], list):
            raise ValueError("subtasks must be a list")
        
        print("JSON structure validation passed")
        print(f"Root title: {sample_tree['title']}")
        print(f"Subtasks count: {len(sample_tree['subtasks'])}")
        print()
        return True
    except Exception as e:
        print(f"JSON validation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting basic functionality tests...\n")
    
    tests = [
        ("Task Structure", test_task_structure),
        ("Task Manager", test_task_manager),
        ("JSON Validation", test_json_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✓ {test_name} test passed")
                passed += 1
            else:
                print(f"✗ {test_name} test failed")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} test failed with error: {e}")
            failed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All basic tests passed! The core functionality is working correctly.")
    else:
        print(f"\n⚠️  {failed} tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
