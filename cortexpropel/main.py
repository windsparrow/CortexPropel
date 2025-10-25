
import click
import os
from .services import (
    create_task_from_natural_language, 
    check_task_execution, 
    schedule_tasks, 
    update_task_progress,
    generate_task_report
)
from .database import read_tasks, get_task_by_id, update_task
from .models import TaskStatus, TaskPriority
from .charts import generate_all_charts, generate_progress_chart, generate_status_pie_chart, generate_priority_chart, generate_timeline_chart

@click.group()
def cli():
    """
    CortexPropel is a CLI for intelligent task management.
    """
    pass

@cli.command()
@click.argument('user_input')
def add(user_input):
    """
    Adds a new task using natural language.
    """
    try:
        task = create_task_from_natural_language(user_input)
        click.echo(f"Task '{task.name}' created successfully.")
        click.echo(f"ID: {task.id}")
        click.echo(f"Priority: {task.priority.value}")
        if task.due_date:
            click.echo(f"Due Date: {task.due_date}")
    except ValueError as e:
        click.echo(f"Error: {e}")
    except Exception as e:
        # This is a general exception handler. For a real application, you would
        # want to handle different exceptions more specifically.
        click.echo(f"An unexpected error occurred: {e}")
        click.echo("Please ensure your DEEPSEEK_API_KEY is set correctly.")

@cli.command(name="list")
def list_tasks():
    """
    Lists all tasks.
    """
    tasks = read_tasks()
    if not tasks:
        click.echo("No tasks found.")
        return

    for task in tasks:
        click.echo(f"- {task.name} (ID: {task.id}, Status: {task.status.value}, Priority: {task.priority.value})")
        if task.description:
            click.echo(f"  Description: {task.description}")
        if task.due_date:
            click.echo(f"  Due Date: {task.due_date}")
        click.echo(f"  Progress: {task.progress}%")

@cli.command()
@click.argument('task_id')
@click.argument('status')
def status(task_id, status):
    """
    Updates the status of a task.
    """
    task = get_task_by_id(task_id)
    if not task:
        click.echo(f"Task with ID '{task_id}' not found.")
        return

    try:
        new_status = TaskStatus(status)
    except ValueError:
        click.echo(f"Invalid status '{status}'. Possible values are: {', '.join([s.value for s in TaskStatus])}")
        return

    if update_task(task_id, {"status": new_status}):
        click.echo(f"Task '{task.name}' updated to '{new_status.value}'.")
    else:
        click.echo(f"Failed to update task '{task.name}'.")

@cli.command()
@click.argument('task_id')
@click.argument('progress', type=int)
def progress(task_id, progress):
    """
    Updates the progress of a task (0-100).
    """
    if progress < 0 or progress > 100:
        click.echo("Progress must be between 0 and 100.")
        return
    
    if update_task_progress(task_id, progress):
        task = get_task_by_id(task_id)
        click.echo(f"Task '{task.name}' progress updated to {progress}%.")
    else:
        click.echo(f"Failed to update progress for task with ID '{task_id}'.")

@cli.command()
def check():
    """
    Checks the execution status of all tasks.
    """
    task_categories = check_task_execution()
    
    click.echo("Task Execution Status:")
    click.echo(f"Overdue tasks: {len(task_categories['overdue'])}")
    for task in task_categories['overdue']:
        click.echo(f"  - {task.name} (Due: {task.due_date})")
    
    click.echo(f"In-progress tasks: {len(task_categories['in_progress'])}")
    for task in task_categories['in_progress']:
        click.echo(f"  - {task.name} (Progress: {task.progress}%)")
    
    click.echo(f"Todo tasks: {len(task_categories['todo'])}")
    for task in task_categories['todo']:
        click.echo(f"  - {task.name}")
    
    click.echo(f"High priority tasks: {len(task_categories['high_priority'])}")
    for task in task_categories['high_priority']:
        click.echo(f"  - {task.name} (Priority: {task.priority.value})")

@cli.command()
def schedule():
    """
    Shows the recommended task schedule based on priority and due date.
    """
    scheduled_tasks = schedule_tasks()
    
    if not scheduled_tasks:
        click.echo("No tasks to schedule.")
        return
    
    click.echo("Recommended Task Schedule:")
    for i, task in enumerate(scheduled_tasks, 1):
        due_date_str = f" (Due: {task.due_date})" if task.due_date else ""
        click.echo(f"{i}. {task.name} - Priority: {task.priority.value}{due_date_str}")

@cli.command()
def report():
    """
    Generates a summary report of tasks.
    """
    report_data = generate_task_report()
    
    click.echo("Task Summary Report:")
    click.echo(f"Total tasks: {report_data['total']}")
    click.echo(f"Completed tasks: {report_data['completed']}")
    click.echo(f"In-progress tasks: {report_data['in_progress']}")
    click.echo(f"Todo tasks: {report_data['todo']}")
    click.echo(f"Overdue tasks: {report_data['overdue']}")
    click.echo(f"Average progress: {report_data['avg_progress']}%")

@cli.command()
def visualize():
    """
    Generates a simple text-based visualization of task progress.
    """
    tasks = read_tasks()
    
    if not tasks:
        click.echo("No tasks to visualize.")
        return
    
    click.echo("Task Progress Visualization:")
    click.echo("=" * 50)
    
    for task in tasks:
        # Create a simple progress bar
        bar_length = 30
        filled_length = int(bar_length * task.progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        status_color = {
            TaskStatus.TODO: "white",
            TaskStatus.IN_PROGRESS: "yellow",
            TaskStatus.DONE: "green"
        }.get(task.status, "white")
        
        priority_indicator = {
            TaskPriority.LOW: "",
            TaskPriority.MEDIUM: "!",
            TaskPriority.HIGH: "!!"
        }.get(task.priority, "")
        
        click.echo(f"{task.name[:20]:20} {priority_indicator} [{bar}] {task.progress}%")
        click.echo(f"{'':22} Status: {task.status.value}")
        if task.due_date:
            click.echo(f"{'':22} Due: {task.due_date}")
        click.echo()

@cli.group()
def chart():
    """
    Commands for generating charts.
    """
    pass

@chart.command()
def all():
    """
    Generates all available charts.
    """
    generate_all_charts()

@chart.command()
def progress():
    """
    Generates a progress bar chart for all tasks.
    """
    tasks = read_tasks()
    generate_progress_chart(tasks)

@chart.command()
def status():
    """
    Generates a pie chart showing task status distribution.
    """
    tasks = read_tasks()
    generate_status_pie_chart(tasks)

@chart.command()
def priority():
    """
    Generates a bar chart showing task priority distribution.
    """
    tasks = read_tasks()
    generate_priority_chart(tasks)

@chart.command()
def timeline():
    """
    Generates a timeline chart showing task due dates.
    """
    tasks = read_tasks()
    generate_timeline_chart(tasks)

if __name__ == '__main__':
    cli()
