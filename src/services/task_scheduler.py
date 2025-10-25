"""
任务调度器模块
负责任务的调度、优先级管理和资源分配
"""

import heapq
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable, Any
from enum import Enum

from ..models.task import Task, TaskStatus, TaskPriority, TaskManager
from ..utils.config import config
from .task_executor import TaskExecutor, TaskExecutionResult, ExecutionStatus


class SchedulingPolicy(Enum):
    """调度策略枚举"""
    FIFO = "fifo"  # 先进先出
    PRIORITY = "priority"  # 优先级调度
    DEADLINE = "deadline"  # 截止时间调度
    FAIR_SHARE = "fair_share"  # 公平共享调度


class ScheduledTask:
    """调度任务包装类"""
    def __init__(self, task: Task, priority_value: int = 0):
        self.task = task
        self.priority_value = priority_value
        self.scheduled_time = datetime.now()
        
    def __lt__(self, other):
        """用于优先队列排序"""
        return self.priority_value < other.priority_value


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, task_manager: TaskManager, executor: TaskExecutor):
        self.task_manager = task_manager
        self.executor = executor
        self.scheduling_policy = SchedulingPolicy.PRIORITY
        self.max_concurrent_tasks = config.task_max_concurrent_tasks
        self.task_queue: List[ScheduledTask] = []
        self.running_tasks: Dict[str, ScheduledTask] = {}
        self.scheduling_callbacks: List[Callable[[str, str], None]] = []
        self._stop_event = threading.Event()
        self._scheduler_thread = None
        self._lock = threading.Lock()
        
        # 添加执行器回调
        self.executor.add_execution_callback(self._on_task_execution_complete)
    
    def set_scheduling_policy(self, policy: SchedulingPolicy):
        """设置调度策略"""
        self.scheduling_policy = policy
    
    def set_max_concurrent_tasks(self, max_tasks: int):
        """设置最大并发任务数"""
        self.max_concurrent_tasks = max_tasks
    
    def add_scheduling_callback(self, callback: Callable[[str, str], None]):
        """添加调度回调函数
        Args:
            callback: 回调函数，参数为(task_id, event_type)
                      event_type可以是"scheduled", "started", "completed", "failed"
        """
        self.scheduling_callbacks.append(callback)
    
    def schedule_task(self, task_id: str, priority_override: Optional[int] = None) -> bool:
        """
        调度任务
        
        Args:
            task_id: 任务ID
            priority_override: 优先级覆盖值，如果不提供则使用任务的默认优先级
            
        Returns:
            bool: 是否成功加入调度队列
        """
        task = self.task_manager.get_task(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False
            
        # 检查任务是否已在队列中
        if self._is_task_in_queue(task_id):
            return False
            
        # 计算优先级值
        if priority_override is not None:
            priority_value = priority_override
        else:
            priority_value = self._calculate_priority_value(task)
            
        # 创建调度任务
        scheduled_task = ScheduledTask(task, priority_value)
        
        with self._lock:
            heapq.heappush(self.task_queue, scheduled_task)
            
        # 通知回调
        self._notify_callbacks(task_id, "scheduled")
        
        # 尝试启动调度
        self._try_schedule_next()
        
        return True
    
    def cancel_scheduled_task(self, task_id: str) -> bool:
        """
        取消调度任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否成功取消
        """
        # 检查是否在运行中
        if task_id in self.running_tasks:
            return self.executor.cancel_task(task_id)
            
        # 从队列中移除
        with self._lock:
            for i, scheduled_task in enumerate(self.task_queue):
                if scheduled_task.task.id == task_id:
                    self.task_queue.pop(i)
                    heapq.heapify(self.task_queue)
                    return True
                    
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取调度队列状态"""
        with self._lock:
            return {
                "queued_tasks": len(self.task_queue),
                "running_tasks": len(self.running_tasks),
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "scheduling_policy": self.scheduling_policy.value
            }
    
    def get_queued_tasks(self) -> List[Task]:
        """获取队列中的任务列表"""
        with self._lock:
            return [scheduled_task.task for scheduled_task in self.task_queue]
    
    def get_running_tasks(self) -> List[Task]:
        """获取正在运行的任务列表"""
        with self._lock:
            return [scheduled_task.task for scheduled_task in self.running_tasks.values()]
    
    def start_scheduler(self, interval: int = 10):
        """启动调度器"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
            
        self._scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            args=(interval,),
            daemon=True
        )
        self._scheduler_thread.start()
    
    def stop_scheduler(self):
        """停止调度器"""
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._stop_event.set()
            self._scheduler_thread.join(timeout=5)
            self._stop_event.clear()
    
    def _scheduler_loop(self, interval: int):
        """调度器主循环"""
        while not self._stop_event.is_set():
            try:
                self._try_schedule_next()
                
                # 等待下一次调度
                for _ in range(interval):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                # 调度异常不应影响主流程
                pass
    
    def _try_schedule_next(self):
        """尝试调度下一个任务"""
        with self._lock:
            # 检查是否达到最大并发数
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                return
                
            # 检查队列是否为空
            if not self.task_queue:
                return
                
            # 获取下一个任务
            scheduled_task = heapq.heappop(self.task_queue)
            task = scheduled_task.task
            
            # 检查任务状态是否仍然有效
            if task.status != TaskStatus.PENDING:
                return
                
            # 检查依赖是否满足
            if not self._check_dependencies(task):
                # 依赖不满足，重新放回队列
                heapq.heappush(self.task_queue, scheduled_task)
                return
                
            # 启动任务执行
            if self.executor.execute_task(task.id):
                self.running_tasks[task.id] = scheduled_task
                self._notify_callbacks(task.id, "started")
    
    def _on_task_execution_complete(self, result: TaskExecutionResult):
        """任务执行完成回调"""
        task_id = result.task_id
        
        with self._lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
                
        # 通知回调
        if result.status == ExecutionStatus.SUCCESS:
            self._notify_callbacks(task_id, "completed")
        else:
            self._notify_callbacks(task_id, "failed")
            
        # 尝试调度下一个任务
        self._try_schedule_next()
    
    def _calculate_priority_value(self, task: Task) -> int:
        """计算任务优先级值"""
        if self.scheduling_policy == SchedulingPolicy.FIFO:
            # 先进先出：使用创建时间戳
            return int(task.created_at.timestamp())
            
        elif self.scheduling_policy == SchedulingPolicy.PRIORITY:
            # 优先级调度：使用任务优先级（值越小优先级越高）
            priority_map = {
                TaskPriority.LOW: 3,
                TaskPriority.MEDIUM: 2,
                TaskPriority.HIGH: 1,
                TaskPriority.URGENT: 0
            }
            return priority_map.get(task.priority, 2)
            
        elif self.scheduling_policy == SchedulingPolicy.DEADLINE:
            # 截止时间调度：使用截止时间（值越小越早）
            if task.due_date:
                return int(task.due_date.timestamp())
            else:
                # 没有截止时间的任务排在最后
                return int(datetime.max.timestamp())
                
        elif self.scheduling_policy == SchedulingPolicy.FAIR_SHARE:
            # 公平共享调度：综合考虑优先级和等待时间
            priority_map = {
                TaskPriority.LOW: 3,
                TaskPriority.MEDIUM: 2,
                TaskPriority.HIGH: 1,
                TaskPriority.URGENT: 0
            }
            
            # 计算等待时间（小时）
            wait_time = (datetime.now() - task.created_at).total_seconds() / 3600
            
            # 基础优先级
            base_priority = priority_map.get(task.priority, 2)
            
            # 根据等待时间调整优先级（每等待24小时，优先级提高1）
            adjusted_priority = max(0, base_priority - int(wait_time / 24))
            
            return adjusted_priority
            
        # 默认使用中等优先级
        return 2
    
    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = self.task_manager.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _is_task_in_queue(self, task_id: str) -> bool:
        """检查任务是否已在队列中"""
        for scheduled_task in self.task_queue:
            if scheduled_task.task.id == task_id:
                return True
        return task_id in self.running_tasks
    
    def _notify_callbacks(self, task_id: str, event_type: str):
        """通知所有回调函数"""
        for callback in self.scheduling_callbacks:
            try:
                callback(task_id, event_type)
            except Exception:
                pass  # 回调函数异常不应影响主流程