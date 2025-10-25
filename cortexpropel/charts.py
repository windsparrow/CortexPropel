import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta
from typing import List, Dict
from .models import Task, TaskStatus, TaskPriority
from .database import read_tasks

def generate_progress_chart(tasks: List[Task], output_file: str = "task_progress.png"):
    """
    Generates a bar chart showing the progress of all tasks.

    Args:
        tasks: List of tasks to include in the chart.
        output_file: File path to save the chart.
    """
    if not tasks:
        print("No tasks to visualize.")
        return
    
    # Prepare data for the chart
    task_names = [task.name[:20] for task in tasks]  # Limit name length for display
    progress_values = [task.progress for task in tasks]
    
    # Create the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(task_names, progress_values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    
    # Add labels and title
    plt.xlabel('Tasks')
    plt.ylabel('Progress (%)')
    plt.title('Task Progress')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    
    # Add value labels on top of bars
    for bar, value in zip(bars, progress_values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, 
                 f'{value}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Progress chart saved to {output_file}")

def generate_status_pie_chart(tasks: List[Task], output_file: str = "task_status.png"):
    """
    Generates a pie chart showing the distribution of task statuses.

    Args:
        tasks: List of tasks to include in the chart.
        output_file: File path to save the chart.
    """
    if not tasks:
        print("No tasks to visualize.")
        return
    
    # Count tasks by status
    status_counts = {
        TaskStatus.TODO.value: 0,
        TaskStatus.IN_PROGRESS.value: 0,
        TaskStatus.DONE.value: 0
    }
    
    for task in tasks:
        status_counts[task.status.value] += 1
    
    # Filter out zero values
    labels = []
    sizes = []
    colors = []
    
    if status_counts[TaskStatus.TODO.value] > 0:
        labels.append(TaskStatus.TODO.value)
        sizes.append(status_counts[TaskStatus.TODO.value])
        colors.append('#ff9999')
    
    if status_counts[TaskStatus.IN_PROGRESS.value] > 0:
        labels.append(TaskStatus.IN_PROGRESS.value)
        sizes.append(status_counts[TaskStatus.IN_PROGRESS.value])
        colors.append('#66b3ff')
    
    if status_counts[TaskStatus.DONE.value] > 0:
        labels.append(TaskStatus.DONE.value)
        sizes.append(status_counts[TaskStatus.DONE.value])
        colors.append('#99ff99')
    
    # Create the pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Task Status Distribution')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Status pie chart saved to {output_file}")

def generate_priority_chart(tasks: List[Task], output_file: str = "task_priority.png"):
    """
    Generates a bar chart showing the distribution of task priorities.

    Args:
        tasks: List of tasks to include in the chart.
        output_file: File path to save the chart.
    """
    if not tasks:
        print("No tasks to visualize.")
        return
    
    # Count tasks by priority
    priority_counts = {
        TaskPriority.LOW.value: 0,
        TaskPriority.MEDIUM.value: 0,
        TaskPriority.HIGH.value: 0
    }
    
    for task in tasks:
        priority_counts[task.priority.value] += 1
    
    # Create the bar chart
    priorities = list(priority_counts.keys())
    counts = list(priority_counts.values())
    colors = ['#99ff99', '#ffcc99', '#ff9999']  # Green, Orange, Red
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(priorities, counts, color=colors)
    
    # Add labels and title
    plt.xlabel('Priority')
    plt.ylabel('Number of Tasks')
    plt.title('Task Priority Distribution')
    
    # Add value labels on top of bars
    for bar, value in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1, 
                 str(value), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Priority chart saved to {output_file}")

def generate_timeline_chart(tasks: List[Task], output_file: str = "task_timeline.png"):
    """
    Generates a timeline chart showing task due dates.

    Args:
        tasks: List of tasks to include in the chart.
        output_file: File path to save the chart.
    """
    # Filter tasks with due dates
    tasks_with_due_dates = [task for task in tasks if task.due_date]
    
    if not tasks_with_due_dates:
        print("No tasks with due dates to visualize.")
        return
    
    # Sort tasks by due date
    tasks_with_due_dates.sort(key=lambda task: task.due_date)
    
    # Prepare data for the chart
    task_names = [task.name[:20] for task in tasks_with_due_dates]
    due_dates = [task.due_date for task in tasks_with_due_dates]
    
    # Create the timeline chart
    plt.figure(figsize=(12, 6))
    
    # Convert dates to matplotlib format
    dates = mdates.date2num(due_dates)
    
    # Create a horizontal bar chart
    y_pos = range(len(task_names))
    colors = ['#ff9999' if task.status != TaskStatus.DONE else '#99ff99' for task in tasks_with_due_dates]
    
    plt.barh(y_pos, dates, height=0.5, color=colors, alpha=0.7)
    
    # Add labels and title
    plt.yticks(y_pos, task_names)
    plt.xlabel('Due Date')
    plt.title('Task Timeline')
    
    # Format the x-axis to show dates
    date_format = mdates.DateFormatter('%Y-%m-%d')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(due_dates)//10)))
    
    # Add a legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#ff9999', alpha=0.7, label='Incomplete'),
        Patch(facecolor='#99ff99', alpha=0.7, label='Complete')
    ]
    plt.legend(handles=legend_elements)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    print(f"Timeline chart saved to {output_file}")

def generate_all_charts():
    """
    Generates all available charts for the current tasks.
    """
    tasks = read_tasks()
    
    if not tasks:
        print("No tasks found. Cannot generate charts.")
        return
    
    # Generate all charts
    generate_progress_chart(tasks)
    generate_status_pie_chart(tasks)
    generate_priority_chart(tasks)
    generate_timeline_chart(tasks)
    
    print("All charts generated successfully.")