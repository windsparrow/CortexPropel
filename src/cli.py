#!/usr/bin/env python3
import argparse
import json
from .task_manager import TaskManager


def main():
    """
    Command-line interface for the task management system.
    """
    parser = argparse.ArgumentParser(description="CortexPropel Task Management System")
    
    # Define commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("task_description", type=str, help="The task description")
    
    # Show task tree command
    show_parser = subparsers.add_parser("show", help="Show the current task tree")
    
    # Reset task tree command
    reset_parser = subparsers.add_parser("reset", help="Reset the task tree to its initial state")
    
    # Process command-line arguments
    args = parser.parse_args()
    
    # Initialize task manager
    task_manager = TaskManager()
    
    # Execute command
    if args.command == "add":
        # Process user input and update task tree
        updated_tree = task_manager.process_user_input(args.task_description)
        print("Task added successfully!")
        print("Updated task tree:")
        print(json.dumps(updated_tree, ensure_ascii=False, indent=2))
    
    elif args.command == "show":
        # Show current task tree
        task_tree = task_manager.get_task_tree()
        print(json.dumps(task_tree, ensure_ascii=False, indent=2))
    
    elif args.command == "reset":
        # Reset task tree
        reset_tree = task_manager.reset_task_tree()
        print("Task tree reset successfully!")
        print("Initial task tree:")
        print(json.dumps(reset_tree, ensure_ascii=False, indent=2))
    
    else:
        # Print help if no command is provided
        parser.print_help()


if __name__ == "__main__":
    main()
