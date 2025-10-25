"""
任务执行器模块
负责检查任务执行状态，自动更新任务状态，并处理任务依赖关系
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from ..models.task import Task, TaskStatus, TaskPriority, TaskManager
from ..utils.config import config


class ExecutionStatus(Enum):
    """任务执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskExecutionResult:
    """任务执行结果"""
    def __init__(self, task_id: str, status: ExecutionStatus, 
                 message: str = "", execution_time: float = 0.0):
        self.task_id = task_id
        self.status = status
        self.message = message
        self.execution_time = execution_time
        self.timestamp = datetime.now()


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.running_tasks: Dict[str, threading.Thread] = {}
        self.execution_results: Dict[str, TaskExecutionResult] = {}
        self.execution_callbacks: List[Callable[[TaskExecutionResult], None]] = []
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._lock = threading.Lock()
        
    def add_execution_callback(self, callback: Callable[[TaskExecutionResult], None]):
        """添加执行结果回调函数"""
        self.execution_callbacks.append(callback)
    
    def execute_task(self, task_id: str, timeout: Optional[int] = None) -> bool:
        """
        执行任务
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒），None表示不限制
            
        Returns:
            bool: 是否成功启动执行
        """
        task = self.task_manager.get_task(task_id)
        if not task:
            return False
            
        if task_id in self.running_tasks:
            return False  # 任务已在执行中
            
        # 检查依赖任务是否完成
        if not self._check_dependencies(task):
            return False
            
        # 创建执行线程
        thread = threading.Thread(
            target=self._execute_task_thread,
            args=(task_id, timeout),
            daemon=True
        )
        
        with self._lock:
            self.running_tasks[task_id] = thread
            
        thread.start()
        return True
    
    def _execute_task_thread(self, task_id: str, timeout: Optional[int] = None):
        """任务执行线程"""
        start_time = time.time()
        task = self.task_manager.get_task(task_id)
        
        if not task:
            return
            
        # 更新任务状态为进行中
        self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)
        
        try:
            # 模拟任务执行（实际应用中这里应该是真正的任务执行逻辑）
            # 这里只是简单地等待一段时间
            execution_time = timeout or config.task_default_execution_time
            
            # 检查是否被停止
            if self._stop_event.is_set():
                self._create_execution_result(
                    task_id, ExecutionStatus.FAILED, 
                    "Task execution was cancelled", 
                    time.time() - start_time
                )
                return
                
            # 等待执行完成或超时
            for _ in range(int(execution_time)):
                if self._stop_event.is_set():
                    self._create_execution_result(
                        task_id, ExecutionStatus.FAILED, 
                        "Task execution was cancelled", 
                        time.time() - start_time
                    )
                    return
                time.sleep(1)
            
            # 任务执行完成
            self.task_manager.update_task_status(task_id, TaskStatus.COMPLETED)
            self._create_execution_result(
                task_id, ExecutionStatus.SUCCESS, 
                "Task completed successfully", 
                time.time() - start_time
            )
            
        except Exception as e:
            # 任务执行失败
            self.task_manager.update_task_status(task_id, TaskStatus.FAILED)
            self._create_execution_result(
                task_id, ExecutionStatus.FAILED, 
                f"Task execution failed: {str(e)}", 
                time.time() - start_time
            )
        finally:
            # 从运行任务列表中移除
            with self._lock:
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
    
    def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = self.task_manager.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _create_execution_result(self, task_id: str, status: ExecutionStatus, 
                                message: str, execution_time: float):
        """创建执行结果并调用回调"""
        result = TaskExecutionResult(task_id, status, message, execution_time)
        
        with self._lock:
            self.execution_results[task_id] = result
            
        # 调用所有回调函数
        for callback in self.execution_callbacks:
            try:
                callback(result)
            except Exception:
                pass  # 回调函数异常不应影响主流程
    
    def get_execution_result(self, task_id: str) -> Optional[TaskExecutionResult]:
        """获取任务执行结果"""
        with self._lock:
            return self.execution_results.get(task_id)
    
    def is_task_running(self, task_id: str) -> bool:
        """检查任务是否正在运行"""
        with self._lock:
            return task_id in self.running_tasks
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务执行"""
        with self._lock:
            if task_id not in self.running_tasks:
                return False
                
            # 注意：Python的线程无法强制终止，这里只是设置停止标志
            # 实际任务执行逻辑需要检查_stop_event来决定是否继续
            self._stop_event.set()
            
            # 重置停止事件，以便其他任务可以继续执行
            self._stop_event.clear()
            
            return True
    
    def start_monitor(self, interval: int = 60):
        """启动监控线程，定期检查任务状态"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
            
        self._monitor_thread = threading.Thread(
            target=self._monitor_tasks,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitor(self):
        """停止监控线程"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_event.set()
            self._monitor_thread.join(timeout=5)
            self._stop_event.clear()
    
    def _monitor_tasks(self, interval: int):
        """监控任务状态"""
        while not self._stop_event.is_set():
            try:
                # 检查逾期任务
                self._check_overdue_tasks()
                
                # 检查可以自动执行的任务
                self._check_auto_executable_tasks()
                
                # 等待下一次检查
                for _ in range(interval):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
                    
            except Exception as e:
                # 监控异常不应影响主流程
                pass
    
    def _check_overdue_tasks(self):
        """检查逾期任务"""
        now = datetime.now()
        all_tasks = self.task_manager.list_tasks()
        
        for task in all_tasks:
            if (task.due_date and 
                task.due_date < now and 
                task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
                
                # 更新任务状态为逾期
                if task.status != TaskStatus.OVERDUE:
                    self.task_manager.update_task_status(task.id, TaskStatus.OVERDUE)
    
    def _check_auto_executable_tasks(self):
        """检查可以自动执行的任务"""
        if not config.task_auto_execute:
            return
            
        pending_tasks = self.task_manager.list_tasks(status=TaskStatus.PENDING)
        
        for task in pending_tasks:
            # 检查是否设置了自动执行
            if not task.metadata.get("auto_execute", False):
                continue
                
            # 检查依赖是否满足
            if not self._check_dependencies(task):
                continue
                
            # 检查是否在指定时间窗口内
            now = datetime.now()
            start_time = task.metadata.get("auto_start_time")
            end_time = task.metadata.get("auto_end_time")
            
            if start_time and now < start_time:
                continue
                
            if end_time and now > end_time:
                continue
                
            # 启动任务执行
            self.execute_task(task.id)
    
    def get_running_tasks_count(self) -> int:
        """获取正在运行的任务数量"""
        with self._lock:
            return len(self.running_tasks)
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务执行统计信息"""
        all_tasks = self.task_manager.list_tasks()
        
        stats = {
            "total": len(all_tasks),
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "overdue": 0,
            "running": self.get_running_tasks_count()
        }
        
        for task in all_tasks:
            if task.status == TaskStatus.PENDING:
                stats["pending"] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                stats["in_progress"] += 1
            elif task.status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif task.status == TaskStatus.FAILED:
                stats["failed"] += 1
            elif task.status == TaskStatus.CANCELLED:
                stats["cancelled"] += 1
            elif task.status == TaskStatus.OVERDUE:
                stats["overdue"] += 1
                
        return stats