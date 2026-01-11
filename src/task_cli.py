#!/usr/bin/env python3
"""
Task metadata management CLI tool.
"""

import argparse
import json
from datetime import datetime

# Import task manager (now in the same directory)
try:
    from .task_manager import TaskManager
except ImportError:
    from task_manager import TaskManager


def list_tasks(args):
    """List all tasks with metadata."""
    task_manager = TaskManager()
    tasks = task_manager.get_all_tasks_metadata()
    
    if not tasks:
        print("No tasks found in database.")
        return
    
    print(f"\nFound {len(tasks)} tasks:\n")
    
    for task in tasks:
        print(f"📋 Task ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Status: {task['status']}")
        print(f"   Priority: {task['priority']}")
        
        if task.get('assigned_to'):
            print(f"   Assigned to: {task['assigned_to']}")
        
        if task.get('planned_start_time'):
            print(f"   Planned start: {task['planned_start_time']}")
        
        if task.get('planned_end_time'):
            print(f"   Planned end: {task['planned_end_time']}")
        
        if task.get('progress', 0) > 0:
            print(f"   Progress: {task['progress']}%")
        
        if task.get('category'):
            print(f"   Category: {task['category']}")
        
        if task.get('tags'):
            tags = ', '.join(task['tags'])
            print(f"   Tags: {tags}")
        
        print()


def show_task(args):
    """Show detailed information for a specific task."""
    task_manager = TaskManager()
    task = task_manager.get_task_metadata(args.task_id)
    
    if not task:
        print(f"Task with ID '{args.task_id}' not found.")
        return
    
    print(f"\n📋 Task Details for {args.task_id}:\n")
    print(f"Title: {task['title']}")
    print(f"Description: {task['description']}")
    print(f"Status: {task['status']}")
    print(f"Priority: {task['priority']}")
    print(f"Created: {task['created_at']}")
    print(f"Updated: {task['updated_at']}")
    
    # Optional fields
    if task.get('planned_start_time'):
        print(f"Planned start: {task['planned_start_time']}")
    
    if task.get('planned_end_time'):
        print(f"Planned end: {task['planned_end_time']}")
    
    if task.get('actual_start_time'):
        print(f"Actual start: {task['actual_start_time']}")
    
    if task.get('actual_end_time'):
        print(f"Actual end: {task['actual_end_time']}")
    
    if task.get('assigned_to'):
        print(f"Assigned to: {task['assigned_to']}")
    
    if task.get('created_by'):
        print(f"Created by: {task['created_by']}")
    
    if task.get('progress', 0) > 0:
        print(f"Progress: {task['progress']}%")
    
    if task.get('estimated_hours'):
        print(f"Estimated hours: {task['estimated_hours']}")
    
    if task.get('actual_hours'):
        print(f"Actual hours: {task['actual_hours']}")
    
    if task.get('category'):
        print(f"Category: {task['category']}")
    
    if task.get('tags'):
        tags = ', '.join(task['tags'])
        print(f"Tags: {tags}")
    
    if task.get('dependencies'):
        deps = ', '.join(task['dependencies'])
        print(f"Dependencies: {deps}")
    
    if task.get('notes'):
        print(f"Notes: {task['notes']}")
    
    print()


def update_task(args):
    """Update task metadata."""
    task_manager = TaskManager()
    
    # Build update data
    update_data = {}
    
    if args.title:
        update_data['title'] = args.title
    
    if args.description:
        update_data['description'] = args.description
    
    if args.status:
        update_data['status'] = args.status
    
    if args.priority:
        update_data['priority'] = args.priority
    
    if args.assigned_to:
        update_data['assigned_to'] = args.assigned_to
    
    if args.planned_start:
        update_data['planned_start_time'] = args.planned_start
    
    if args.planned_end:
        update_data['planned_end_time'] = args.planned_end
    
    if args.progress:
        update_data['progress'] = args.progress
    
    if args.category:
        update_data['category'] = args.category
    
    if args.estimated_hours:
        update_data['estimated_hours'] = args.estimated_hours
    
    if args.tags:
        update_data['tags'] = args.tags.split(',')
    
    if args.notes:
        update_data['notes'] = args.notes
    
    if not update_data:
        print("No update data provided.")
        return
    
    # Update task
    success = task_manager.update_task_metadata(args.task_id, update_data)
    
    if success:
        print(f"✓ Task {args.task_id} updated successfully.")
    else:
        print(f"✗ Failed to update task {args.task_id}.")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Task Metadata Management Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List tasks
    list_parser = subparsers.add_parser('list', help='List all tasks')
    
    # Show task
    show_parser = subparsers.add_parser('show', help='Show task details')
    show_parser.add_argument('task_id', help='Task ID')
    
    # Update task
    update_parser = subparsers.add_parser('update', help='Update task metadata')
    update_parser.add_argument('task_id', help='Task ID')
    update_parser.add_argument('--title', help='Task title')
    update_parser.add_argument('--description', help='Task description')
    update_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed'], help='Task status')
    update_parser.add_argument('--priority', type=int, choices=range(1, 6), help='Task priority (1-5)')
    update_parser.add_argument('--assigned-to', help='Person assigned to this task')
    update_parser.add_argument('--planned-start', help='Planned start time (ISO format)')
    update_parser.add_argument('--planned-end', help='Planned end time (ISO format)')
    update_parser.add_argument('--progress', type=int, choices=range(0, 101), help='Progress percentage (0-100)')
    update_parser.add_argument('--category', help='Task category')
    update_parser.add_argument('--estimated-hours', type=float, help='Estimated hours')
    update_parser.add_argument('--tags', help='Comma-separated tags')
    update_parser.add_argument('--notes', help='Additional notes')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_tasks(args)
    elif args.command == 'show':
        show_task(args)
    elif args.command == 'update':
        update_task(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
