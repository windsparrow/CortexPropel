"""
CortexPropel CLI 主模块
"""

import click
import os
import sys
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services import TaskService, TaskExecutor, TaskScheduler, SchedulingPolicy, DeepSeekClient
from src.agents import TaskAgent
from src.utils import config
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
import click

# 初始化控制台
console = Console()

# 初始化服务
task_service = TaskService()
task_manager = task_service.task_manager
executor = TaskExecutor(task_manager)
scheduler = TaskScheduler(task_manager, executor)
task_agent = TaskAgent(task_manager)

# 初始化DeepSeek客户端
deepseek_client = DeepSeekClient()

# 启动执行器监控和调度器
executor.start_monitor()
scheduler.start_scheduler()

# 创建CLI上下文对象
class CLIContext:
    def __init__(self):
        self.task_service = task_service
        self.task_agent = task_agent
        self.executor = executor
        self.scheduler = scheduler
        self.deepseek_client = deepseek_client

# 初始化CLI上下文
cli_context = CLIContext()


@click.group()
@click.version_option(version="0.1.0", prog_name="CortexPropel")
def cli():
    """CortexPropel - 智能任务管理工具"""
    # 确保配置有效
    if not config.validate():
        console.print("[red]配置无效，请检查环境变量设置[/red]")
        sys.exit(1)
    
    # 确保必要的目录存在
    config.ensure_directories()


@cli.command()
@click.argument('input_text', required=False)
def chat(input_text: Optional[str]):
    """与智能助手对话，自然语言管理任务"""
    if not input_text:
        # 交互式对话模式
        console.print(Panel.fit("[bold blue]CortexPropel 智能助手[/bold blue]", border_style="blue"))
        console.print("输入 'exit' 或 'quit' 退出对话\n")
        
        while True:
            try:
                user_input = Prompt.ask("[bold cyan]您[/bold cyan]")
                
                if user_input.lower() in ['exit', 'quit']:
                    console.print("[green]再见![/green]")
                    break
                
                if not user_input.strip():
                    continue
                
                # 处理用户输入
                with console.status("[bold green]思考中..."):
                    response = task_agent.process(user_input)
                
                console.print(f"[bold magenta]助手:[/bold magenta] {response}\n")
            
            except KeyboardInterrupt:
                console.print("\n[green]再见![/green]")
                break
            except Exception as e:
                console.print(f"[red]错误: {str(e)}[/red]")
    else:
        # 单次对话模式
        try:
            with console.status("[bold green]思考中..."):
                response = task_agent.process(input_text)
            console.print(f"[bold magenta]助手:[/bold magenta] {response}")
        except Exception as e:
            console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.option('--title', '-t', required=True, help='任务标题')
@click.option('--description', '-d', default='', help='任务描述')
@click.option('--priority', '-p', default='medium', type=click.Choice(['low', 'medium', 'high']), help='任务优先级')
@click.option('--due-date', help='截止日期 (YYYY-MM-DD)')
@click.option('--tags', help='标签，用逗号分隔')
@click.option('--parent', help='父任务ID')
@click.option('--estimated-hours', type=float, help='预估工时')
def add(title, description, priority, due_date, tags, parent, estimated_hours):
    """添加新任务"""
    try:
        # 处理标签
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # 创建任务
        result = task_service.create_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tag_list,
            parent_task_id=parent,
            estimated_hours=estimated_hours
        )
        
        if result['success']:
            console.print(f"[green]✓[/green] {result['message']}")
            console.print(f"任务ID: {result['task_id']}")
        else:
            console.print(f"[red]✗[/red] {result['message']}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed', 'cancelled']), help='按状态过滤')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), help='按优先级过滤')
@click.option('--parent', help='按父任务ID过滤')
def list(status, priority, parent):
    """列出任务"""
    try:
        result = task_service.list_tasks(
            status=status,
            priority=priority,
            parent_task_id=parent
        )
        
        if not result['success']:
            console.print(f"[red]✗[/red] {result['message']}")
            return
        
        tasks = result['tasks']
        
        if not tasks:
            console.print("[yellow]没有找到任务[/yellow]")
            return
        
        # 创建表格
        table = Table(title=f"任务列表 (共 {result['count']} 项)")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("标题", style="magenta")
        table.add_column("状态", style="green")
        table.add_column("优先级", style="yellow")
        table.add_column("截止日期", style="red")
        
        # 添加任务行
        for task in tasks:
            status_style = {
                'pending': 'white',
                'in_progress': 'blue',
                'completed': 'green',
                'cancelled': 'red'
            }.get(task['status'], 'white')
            
            priority_style = {
                'low': 'green',
                'medium': 'yellow',
                'high': 'red'
            }.get(task['priority'], 'white')
            
            due_date = task['due_date'] or "-"
            if due_date != "-":
                # 只显示日期部分
                due_date = due_date.split('T')[0]
            
            table.add_row(
                task['id'],
                task['title'][:30] + "..." if len(task['title']) > 30 else task['title'],
                f"[{status_style}]{task['status']}[/{status_style}]",
                f"[{priority_style}]{task['priority']}[/{priority_style}]",
                due_date
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.option('--task-id', '-i', help='要分析的任务ID')
@click.argument('description', required=False)
def analyze(task_id, description):
    """分析任务"""
    try:
        if task_id:
            # 分析指定任务
            task = task_service.get_task(task_id)
            if not task['success']:
                console.print(f"[red]✗[/red] {task['message']}")
                return
            
            task_data = task['task']
            with console.status("[bold green]分析任务中..."):
                analysis = deepseek_client.analyze_task(task_data['description'])
            
            # 显示分析结果
            analysis_text = "\n".join([f"- {k}: {v}" for k, v in analysis.items()])
            console.print(Panel.fit(
                f"[bold]任务分析结果[/bold]\n\n{analysis_text}",
                title=f"任务: {task_data['title']}",
                border_style="blue"
            ))
        elif description:
            # 分析提供的描述
            with console.status("[bold green]分析任务中..."):
                analysis = deepseek_client.analyze_task(description)
            
            # 显示分析结果
            analysis_text = "\n".join([f"- {k}: {v}" for k, v in analysis.items()])
            console.print(Panel.fit(
                f"[bold]任务分析结果[/bold]\n\n{analysis_text}",
                title="任务分析",
                border_style="blue"
            ))
        else:
            console.print("[red]请提供任务ID或任务描述[/red]")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('project_description')
def suggest(project_description):
    """基于项目描述生成任务建议"""
    try:
        with console.status("[bold green]生成任务建议中..."):
            suggestions = deepseek_client.generate_task_suggestions(project_description)
        
        if not suggestions:
            console.print("[yellow]无法生成任务建议，请提供更详细的项目描述[/yellow]")
            return
        
        # 显示任务建议
        suggestion_text = "\n".join([
            f"{i+1}. {s.get('title', '')} - {s.get('description', '')} (优先级: {s.get('priority', '中')}, 预估工时: {s.get('estimated_hours', 1)}小时)"
            for i, s in enumerate(suggestions)
        ])
        
        console.print(Panel.fit(
            f"[bold]任务建议[/bold]\n\n{suggestion_text}",
            title="任务建议",
            border_style="green"
        ))
        
        # 询问是否要创建这些任务
        create = Prompt.ask("是否要创建这些任务? (y/n)", default="n")
        if create.lower() == 'y':
            for s in suggestions:
                result = task_service.create_task(
                    title=s.get('title', ''),
                    description=s.get('description', ''),
                    priority=s.get('priority', 'medium'),
                    estimated_hours=s.get('estimated_hours', 1)
                )
                
                if result['success']:
                    console.print(f"[green]✓[/green] 已创建任务: {result['task_id']}")
                else:
                    console.print(f"[red]✗[/red] 创建任务失败: {result['message']}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
def optimize():
    """优化任务执行顺序"""
    try:
        # 获取所有任务
        result = task_service.list_tasks()
        
        if not result['success']:
            console.print(f"[red]✗[/red] {result['message']}")
            return
        
        tasks = result['tasks']
        
        if not tasks:
            console.print("[yellow]当前没有任务可以优化[/yellow]")
            return
        
        with console.status("[bold green]优化任务顺序中..."):
            optimized_tasks = deepseek_client.optimize_task_order(tasks)
        
        # 显示优化后的任务顺序
        optimized_text = "\n".join([
            f"{i+1}. {task.get('title', '')} (ID: {task.get('id', '')}, 优先级: {task.get('priority', '中')})"
            for i, task in enumerate(optimized_tasks)
        ])
        
        console.print(Panel.fit(
            f"[bold]优化后的任务顺序[/bold]\n\n{optimized_text}",
            title="任务优化",
            border_style="cyan"
        ))
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
def check_api():
    """检查DeepSeek API是否可用"""
    try:
        with console.status("[bold green]检查API连接..."):
            is_available = deepseek_client.is_available()
        
        if is_available:
            console.print("[green]✓[/green] DeepSeek API连接正常")
        else:
            console.print("[red]✗[/red] DeepSeek API连接失败，请检查API密钥配置")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
def show(task_id):
    """显示任务详情"""
    try:
        result = task_service.get_task(task_id)
        
        if not result['success']:
            console.print(f"[red]✗[/red] {result['message']}")
            return
        
        task = result['task']
        
        # 创建任务详情面板
        details = []
        details.append(f"[bold]ID:[/bold] {task['id']}")
        details.append(f"[bold]标题:[/bold] {task['title']}")
        details.append(f"[bold]描述:[/bold] {task['description'] or '无'}")
        
        # 状态
        status_style = {
            'pending': 'white',
            'in_progress': 'blue',
            'completed': 'green',
            'cancelled': 'red'
        }.get(task['status'], 'white')
        details.append(f"[bold]状态:[/bold] [{status_style}]{task['status']}[/{status_style}]")
        
        # 优先级
        priority_style = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'red'
        }.get(task['priority'], 'white')
        details.append(f"[bold]优先级:[/bold] [{priority_style}]{task['priority']}[/{priority_style}]")
        
        # 日期
        details.append(f"[bold]创建时间:[/bold] {task['created_at']}")
        details.append(f"[bold]更新时间:[/bold] {task['updated_at']}")
        
        if task['due_date']:
            details.append(f"[bold]截止日期:[/bold] {task['due_date']}")
        
        if task['completed_at']:
            details.append(f"[bold]完成时间:[/bold] {task['completed_at']}")
        
        if task['tags']:
            details.append(f"[bold]标签:[/bold] {', '.join(task['tags'])}")
        
        if task['estimated_hours']:
            details.append(f"[bold]预估工时:[/bold] {task['estimated_hours']}小时")
        
        if task['actual_hours']:
            details.append(f"[bold]实际工时:[/bold] {task['actual_hours']}小时")
        
        if task['parent_task_id']:
            details.append(f"[bold]父任务:[/bold] {task['parent_task_id']}")
        
        if task['subtasks']:
            details.append(f"[bold]子任务:[/bold] {', '.join(task['subtasks'])}")
        
        # 笔记
        if task['notes']:
            details.append("\n[bold]笔记:[/bold]")
            for note in task['notes']:
                details.append(f"- {note['content']} ({note['created_at']})")
        
        # 显示面板
        panel_content = "\n".join(details)
        console.print(Panel(panel_content, title=f"任务详情: {task['title']}", border_style="blue"))
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.option('--title', help='新标题')
@click.option('--description', '-d', help='新描述')
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed', 'cancelled']), help='新状态')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), help='新优先级')
@click.option('--due-date', help='新截止日期 (YYYY-MM-DD)')
@click.option('--tags', help='新标签，用逗号分隔')
@click.option('--estimated-hours', type=float, help='新预估工时')
@click.option('--actual-hours', type=float, help='实际工时')
def update(task_id, title, description, status, priority, due_date, tags, estimated_hours, actual_hours):
    """更新任务"""
    try:
        # 处理标签
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
        
        # 更新任务
        result = task_service.update_task(
            task_id=task_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            tags=tag_list,
            estimated_hours=estimated_hours,
            actual_hours=actual_hours
        )
        
        if result['success']:
            console.print(f"[green]✓[/green] {result['message']}")
        else:
            console.print(f"[red]✗[/red] {result['message']}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.option('--confirm', is_flag=True, help='确认删除')
def delete(task_id, confirm):
    """删除任务"""
    try:
        if not confirm:
            # 获取任务信息
            task_result = task_service.get_task(task_id)
            if task_result['success']:
                task = task_result['task']
                console.print(f"将要删除任务: [bold]{task['title']}[/bold] (ID: {task['id']})")
                
                if not Prompt.ask("确认删除?", choices=["y", "n"], default="n") == "y":
                    console.print("[yellow]已取消删除[/yellow]")
                    return
        
        # 删除任务
        result = task_service.delete_task(task_id)
        
        if result['success']:
            console.print(f"[green]✓[/green] {result['message']}")
        else:
            console.print(f"[red]✗[/red] {result['message']}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.argument('content')
def note(task_id, content):
    """添加任务笔记"""
    try:
        result = task_service.add_task_note(task_id, content)
        
        if result['success']:
            console.print(f"[green]✓[/green] {result['message']}")
        else:
            console.print(f"[red]✗[/red] {result['message']}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
def stats():
    """显示任务统计信息"""
    try:
        result = task_service.get_task_statistics()
        
        if not result['success']:
            console.print(f"[red]✗[/red] {result['message']}")
            return
        
        # 创建统计表格
        table = Table(title="任务统计")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="magenta")
        
        table.add_row("总任务数", str(result['total_tasks']))
        table.add_row("完成率", f"{result['completion_rate']}%")
        table.add_row("逾期任务", str(result['overdue_tasks']))
        
        # 添加状态统计
        table.add_row("", "")  # 空行
        table.add_row("[bold]状态分布[/bold]", "")
        for status, count in result['status_counts'].items():
            table.add_row(f"- {status}", str(count))
        
        # 添加优先级统计
        table.add_row("", "")  # 空行
        table.add_row("[bold]优先级分布[/bold]", "")
        for priority, count in result['priority_counts'].items():
            table.add_row(f"- {priority}", str(count))
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.option('--timeout', type=int, help='执行超时时间（秒）')
def execute(task_id, timeout):
    """执行任务"""
    try:
        # 检查任务是否存在
        task_result = task_service.get_task(task_id)
        if not task_result['success']:
            console.print(f"[red]✗[/red] {task_result['message']}")
            return
        
        # 检查任务是否已在执行中
        if executor.is_task_running(task_id):
            console.print(f"[yellow]任务 {task_id} 已在执行中[/yellow]")
            return
        
        # 执行任务
        if executor.execute_task(task_id, timeout):
            console.print(f"[green]✓[/green] 任务 {task_id} 已开始执行")
        else:
            console.print(f"[red]✗[/red] 无法执行任务 {task_id}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
def cancel(task_id):
    """取消任务执行"""
    try:
        if executor.cancel_task(task_id):
            console.print(f"[green]✓[/green] 任务 {task_id} 已取消")
        else:
            console.print(f"[red]✗[/red] 无法取消任务 {task_id}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
@click.option('--priority', type=int, help='调度优先级覆盖值')
def schedule(task_id, priority):
    """调度任务"""
    try:
        if scheduler.schedule_task(task_id, priority):
            console.print(f"[green]✓[/green] 任务 {task_id} 已加入调度队列")
        else:
            console.print(f"[red]✗[/red] 无法调度任务 {task_id}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
def unschedule(task_id):
    """取消任务调度"""
    try:
        if scheduler.cancel_scheduled_task(task_id):
            console.print(f"[green]✓[/green] 任务 {task_id} 已从调度队列中移除")
        else:
            console.print(f"[red]✗[/red] 无法取消调度任务 {task_id}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
def queue():
    """显示任务调度队列状态"""
    try:
        queue_status = scheduler.get_queue_status()
        
        # 创建状态表格
        table = Table(title="调度队列状态")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="magenta")
        
        table.add_row("队列中的任务", str(queue_status['queued_tasks']))
        table.add_row("正在运行的任务", str(queue_status['running_tasks']))
        table.add_row("最大并发任务数", str(queue_status['max_concurrent_tasks']))
        table.add_row("调度策略", queue_status['scheduling_policy'])
        
        console.print(table)
        
        # 显示队列中的任务
        queued_tasks = scheduler.get_queued_tasks()
        if queued_tasks:
            console.print("\n[bold]队列中的任务:[/bold]")
            queue_table = Table()
            queue_table.add_column("ID", style="cyan")
            queue_table.add_column("标题", style="magenta")
            queue_table.add_column("优先级", style="yellow")
            
            for task in queued_tasks:
                queue_table.add_row(
                    task.id,
                    task.title[:30] + "..." if len(task.title) > 30 else task.title,
                    task.priority.value
                )
            
            console.print(queue_table)
        
        # 显示正在运行的任务
        running_tasks = scheduler.get_running_tasks()
        if running_tasks:
            console.print("\n[bold]正在运行的任务:[/bold]")
            running_table = Table()
            running_table.add_column("ID", style="cyan")
            running_table.add_column("标题", style="magenta")
            running_table.add_column("状态", style="green")
            
            for task in running_tasks:
                running_table.add_row(
                    task.id,
                    task.title[:30] + "..." if len(task.title) > 30 else task.title,
                    task.status.value
                )
            
            console.print(running_table)
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.option('--policy', type=click.Choice(['fifo', 'priority', 'deadline', 'fair_share']), 
              help='调度策略')
@click.option('--max-concurrent', type=int, help='最大并发任务数')
def configure_scheduler(policy, max_concurrent):
    """配置任务调度器"""
    try:
        if policy:
            policy_enum = SchedulingPolicy(policy)
            scheduler.set_scheduling_policy(policy_enum)
            console.print(f"[green]✓[/green] 调度策略已设置为: {policy}")
        
        if max_concurrent:
            scheduler.set_max_concurrent_tasks(max_concurrent)
            console.print(f"[green]✓[/green] 最大并发任务数已设置为: {max_concurrent}")
        
        if not policy and not max_concurrent:
            # 显示当前配置
            queue_status = scheduler.get_queue_status()
            console.print(f"当前调度策略: {queue_status['scheduling_policy']}")
            console.print(f"当前最大并发任务数: {queue_status['max_concurrent_tasks']}")
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.command()
@click.argument('task_id')
def execution_status(task_id):
    """查看任务执行状态"""
    try:
        result = executor.get_execution_result(task_id)
        
        if not result:
            # 检查任务是否在运行中
            if executor.is_task_running(task_id):
                console.print(f"[yellow]任务 {task_id} 正在执行中[/yellow]")
            else:
                console.print(f"[yellow]任务 {task_id} 没有执行记录[/yellow]")
            return
        
        # 显示执行结果
        status_style = {
            ExecutionStatus.PENDING: 'white',
            ExecutionStatus.RUNNING: 'blue',
            ExecutionStatus.SUCCESS: 'green',
            ExecutionStatus.FAILED: 'red',
            ExecutionStatus.TIMEOUT: 'yellow'
        }.get(result.status, 'white')
        
        details = []
        details.append(f"[bold]任务ID:[/bold] {result.task_id}")
        details.append(f"[bold]执行状态:[/bold] [{status_style}]{result.status.value}[/{status_style}]")
        details.append(f"[bold]执行时间:[/bold] {result.execution_time:.2f}秒")
        details.append(f"[bold]执行时间戳:[/bold] {result.timestamp}")
        
        if result.message:
            details.append(f"[bold]消息:[/bold] {result.message}")
        
        panel_content = "\n".join(details)
        console.print(Panel(panel_content, title="任务执行状态", border_style="blue"))
    
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


def main():
    """CLI入口点"""
    cli()


if __name__ == "__main__":
    main()