"""
CortexPropel CLI界面
提供命令行交互功能
"""

import click
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import CortexPropelEngine
from core.task_checker import TaskChecker


console = Console()


def format_task_status(status: str) -> str:
    """格式化任务状态显示"""
    status_colors = {
        "pending": "[yellow]待开始[/yellow]",
        "in_progress": "[blue]进行中[/blue]",
        "completed": "[green]已完成[/green]",
        "cancelled": "[red]已取消[/red]",
        "blocked": "[red]被阻塞[/red]"
    }
    return status_colors.get(status, status)


def format_task_priority(priority: str) -> str:
    """格式化任务优先级显示"""
    priority_colors = {
        "low": "[green]低[/green]",
        "medium": "[yellow]中[/yellow]",
        "high": "[orange1]高[/orange1]",
        "urgent": "[red]紧急[/red]"
    }
    return priority_colors.get(priority, priority)


def display_tasks(tasks: list, title: str = "任务列表"):
    """显示任务列表"""
    if not tasks:
        console.print(Panel("[yellow]暂无任务[/yellow]", title=title))
        return
    
    table = Table(title=title)
    table.add_column("ID", style="cyan", width=8)
    table.add_column("标题", style="magenta", width=30)
    table.add_column("状态", justify="center", width=10)
    table.add_column("优先级", justify="center", width=8)
    table.add_column("创建时间", style="dim", width=20)
    table.add_column("截止日期", style="dim", width=20)
    
    for task in tasks:
        # 格式化日期
        created_at = datetime.fromisoformat(task['created_at']).strftime("%Y-%m-%d %H:%M") if task.get('created_at') else "-"
        due_date = datetime.fromisoformat(task['due_date']).strftime("%Y-%m-%d %H:%M") if task.get('due_date') else "-"
        
        table.add_row(
            task['id'][:8],
            task['title'][:28] + "..." if len(task['title']) > 30 else task['title'],
            format_task_status(task['status']),
            format_task_priority(task['priority']),
            created_at,
            due_date
        )
    
    console.print(table)


def display_task_details(task: dict):
    """显示任务详情"""
    if not task:
        console.print("[red]任务不存在[/red]")
        return
    
    # 创建任务详情面板
    content = Text()
    content.append("标题: ", style="bold")
    content.append(f"{task['title']}\n", style="cyan")
    content.append("描述: ", style="bold")
    content.append(f"{task['description']}\n\n", style="white")
    content.append("状态: ", style="bold")
    content.append(f"{task['status']}\n", style="yellow")
    content.append("优先级: ", style="bold")
    content.append(f"{task['priority']}\n", style="magenta")
    
    # 时间信息
    created_at = datetime.fromisoformat(task['created_at']).strftime("%Y-%m-%d %H:%M") if task.get('created_at') else "-"
    content.append("创建时间: ", style="bold")
    content.append(f"{created_at}\n", style="dim")
    
    if task.get('due_date'):
        due_date = datetime.fromisoformat(task['due_date']).strftime("%Y-%m-%d %H:%M")
        content.append("截止日期: ", style="bold")
        content.append(f"{due_date}\n", style="dim")
    
    if task.get('completed_at'):
        completed_at = datetime.fromisoformat(task['completed_at']).strftime("%Y-%m-%d %H:%M")
        content.append("完成时间: ", style="bold")
        content.append(f"{completed_at}\n", style="green")
    
    # 标签和子任务
    if task.get('tags'):
        content.append("\n标签: ", style="bold")
        content.append(", ".join(task['tags']), style="blue")
    
    if task.get('subtask_ids'):
        content.append(f"\n子任务数: {len(task['subtask_ids'])}", style="bold")
    
    panel = Panel(content, title="任务详情", border_style="blue")
    console.print(panel)


@click.group()
@click.option('--tasks-file', '-f', default='tasks.json', help='任务数据文件路径')
@click.version_option(version="1.0.0")
@click.pass_context
def cli(ctx, tasks_file):
    """CortexPropel - 智能任务管理工具"""
    ctx.ensure_object(dict)
    ctx.obj['tasks_file'] = tasks_file


@cli.command()
@click.argument('user_input', required=True)
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.pass_context
def process(ctx, user_input: str, config: str):
    """处理自然语言输入"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        result = engine.process_natural_language_input(user_input)
        
        if "error" in result:
            console.print(f"[red]错误: {result['error']}[/red]")
            if "suggestion" in result:
                console.print(f"[yellow]建议: {result['suggestion']}[/yellow]")
        else:
            action = result.get('action', 'unknown')
            message = result.get('message', '处理完成')
            
            console.print(f"[green]✓ {message}[/green]")
            
            # 显示任务详情（如果是创建或更新任务）
            if action in ['create_task', 'update_task'] and 'task' in result:
                console.print("\n")
                display_task_details(result['task'])
            
            # 显示任务列表（如果是列出任务）
            elif action == 'list_tasks' and 'tasks' in result:
                display_tasks(result['tasks'])
            
            # 显示搜索结果
            elif action == 'search_tasks' and 'tasks' in result:
                display_tasks(result['tasks'], f"搜索结果 ({result['count']}个任务)")
    
    except Exception as e:
        console.print(f"[red]系统错误: {str(e)}[/red]")


@cli.command()
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed', 'cancelled', 'blocked']), help='按状态过滤')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), help='按优先级过滤')
@click.pass_context
def list(ctx, config: str, status: str, priority: str):
    """列出所有任务"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        
        # 获取任务
        if status:
            from ..models.task import TaskStatus
            tasks = engine.task_manager.get_tasks_by_status(TaskStatus(status))
        elif priority:
            from ..models.task import TaskPriority
            tasks = engine.task_manager.get_tasks_by_priority(TaskPriority(priority))
        else:
            tasks = engine.task_manager.get_all_tasks()
        
        # 转换为JSON格式用于显示
        tasks_json = [task.model_dump(mode='json') for task in tasks]
        display_tasks(tasks_json)
        
        console.print(f"\n[dim]总计: {len(tasks)} 个任务[/dim]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.pass_context
def show(ctx, task_id: str, config: str):
    """显示任务详情"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        task = engine.get_task_by_id(task_id)
        
        if task:
            display_task_details(task)
        else:
            console.print(f"[red]未找到任务: {task_id}[/red]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('keyword')
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.pass_context
def search(ctx, keyword: str, config: str):
    """搜索任务"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        tasks = engine.search_tasks(keyword)
        
        display_tasks(tasks, f"搜索结果: '{keyword}'")
        console.print(f"\n[dim]找到 {len(tasks)} 个任务[/dim]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.pass_context
def stats(ctx, config: str):
    """显示任务统计信息"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        stats_data = engine.get_task_statistics()
        
        if "error" in stats_data:
            console.print(f"[red]错误: {stats_data['error']}[/red]")
            return
        
        # 创建统计表格
        table = Table(title="任务统计")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="magenta")
        
        table.add_row("总任务数", str(stats_data['total_tasks']))
        table.add_row("完成率", f"{stats_data['completion_rate']:.1%}")
        table.add_row("问题率", f"{stats_data['problem_rate']:.1%}")
        
        console.print(table)
        
        # 状态分布
        status_table = Table(title="状态分布")
        status_table.add_column("状态", style="cyan")
        status_table.add_column("数量", style="magenta")
        
        for status, count in stats_data['status_distribution'].items():
            status_table.add_row(format_task_status(status), str(count))
        
        console.print(status_table)
        
        # 优先级分布
        priority_table = Table(title="优先级分布")
        priority_table.add_column("优先级", style="cyan")
        priority_table.add_column("数量", style="magenta")
        
        for priority, count in stats_data['priority_distribution'].items():
            priority_table.add_row(format_task_priority(priority), str(count))
        
        console.print(priority_table)
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.option('--days', '-d', default=3, help='即将到期天数阈值')
@click.pass_context
def health(ctx, config: str, days: int):
    """显示项目健康报告"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        checker = TaskChecker(engine.task_manager)
        
        # 获取健康报告
        health_report = checker.generate_health_report()
        
        # 显示基本统计
        summary = health_report['summary']
        console.print(Panel(f"""
[bold]项目健康状态: {summary['health_status']}[/bold]
总任务数: {summary['total_tasks']}
完成率: {summary['completion_rate']:.1%}
问题率: {summary['problem_rate']:.1%}
        """.strip(), title="项目概览"))
        
        # 显示问题统计
        issues = health_report['issues']
        if any(count > 0 for count in issues.values() if isinstance(count, (int, float))):
            console.print("\n[yellow]⚠️  发现问题:[/yellow]")
            for issue_type, count in issues.items():
                if isinstance(count, (int, float)) and count > 0:
                    console.print(f"  • {issue_type.replace('_', ' ')}: {count}")
        
        # 显示具体的问题任务
        overdue_tasks = checker.check_overdue_tasks()
        due_soon_tasks = checker.check_tasks_due_soon(days)
        blocked_tasks = checker.check_blocked_tasks()
        
        if overdue_tasks:
            console.print(f"\n[red]🔥 逾期任务 ({len(overdue_tasks)}):[/red]")
            overdue_json = [task.model_dump(mode='json') for task in overdue_tasks]
            display_tasks(overdue_json)
        
        if due_soon_tasks:
            console.print(f"\n[yellow]⏰ 即将到期任务 ({len(due_soon_tasks)}):[/yellow]")
            due_soon_json = [task.model_dump(mode='json') for task in due_soon_tasks]
            display_tasks(due_soon_json)
        
        if blocked_tasks:
            console.print(f"\n[red]🚫 被阻塞任务 ({len(blocked_tasks)}):[/red]")
            blocked_json = [task.model_dump(mode='json') for task in blocked_tasks]
            display_tasks(blocked_json)
        
        # 显示建议
        recommendations = health_report['recommendations']
        if recommendations:
            console.print("\n[blue]💡 建议:[/blue]")
            for rec in recommendations:
                console.print(f"  • {rec}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.option('--config', '-c', default='config.ini', help='配置文件路径')
@click.confirmation_option(prompt='确定要删除这个任务吗？')
@click.pass_context
def delete(ctx, task_id: str, config: str):
    """删除任务"""
    try:
        tasks_file = ctx.obj['tasks_file']
        engine = CortexPropelEngine(config, tasks_file)
        
        # 先显示任务信息确认
        task = engine.get_task_by_id(task_id)
        if not task:
            console.print(f"[red]未找到任务: {task_id}[/red]")
            return
        
        display_task_details(task)
        
        if click.confirm("确定要删除这个任务吗？"):
            if engine.delete_task(task_id):
                console.print(f"[green]✓ 任务已删除[/green]")
            else:
                console.print(f"[red]删除失败[/red]")
        else:
            console.print("[yellow]已取消删除[/yellow]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


if __name__ == '__main__':
    cli()