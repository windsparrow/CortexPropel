"""
任务执行检查模块
提供任务状态检查、进度跟踪等功能
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import Task, TaskStatus, TaskPriority, TaskManager


class TaskChecker:
    """任务执行检查器"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.logger = logging.getLogger(__name__)
    
    def check_overdue_tasks(self) -> List[Task]:
        """检查逾期任务"""
        now = datetime.now()
        overdue_tasks = []
        
        for task in self.task_manager.get_all_tasks():
            if (task.due_date and 
                task.due_date < now and 
                task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
                overdue_tasks.append(task)
        
        return overdue_tasks
    
    def check_tasks_due_soon(self, days: int = 3) -> List[Task]:
        """检查即将到期的任务"""
        now = datetime.now()
        soon_date = now + timedelta(days=days)
        due_soon_tasks = []
        
        for task in self.task_manager.get_all_tasks():
            if (task.due_date and 
                now <= task.due_date <= soon_date and 
                task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
                due_soon_tasks.append(task)
        
        return due_soon_tasks
    
    def check_blocked_tasks(self) -> List[Task]:
        """检查被阻塞的任务"""
        return self.task_manager.get_tasks_by_status(TaskStatus.BLOCKED)
    
    def check_long_running_tasks(self, days: int = 7) -> List[Task]:
        """检查长时间运行的任务"""
        now = datetime.now()
        long_running_tasks = []
        
        for task in self.task_manager.get_all_tasks():
            if (task.status == TaskStatus.IN_PROGRESS and 
                task.updated_at and 
                (now - task.updated_at).days >= days):
                long_running_tasks.append(task)
        
        return long_running_tasks
    
    def check_stale_tasks(self, days: int = 14) -> List[Task]:
        """检查长时间未更新的任务"""
        now = datetime.now()
        stale_date = now - timedelta(days=days)
        stale_tasks = []
        
        for task in self.task_manager.get_all_tasks():
            if (task.updated_at < stale_date and 
                task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]):
                stale_tasks.append(task)
        
        return stale_tasks
    
    def get_task_progress_report(self, task_id: str) -> Dict[str, Any]:
        """获取任务进度报告"""
        task = self.task_manager.get_task(task_id)
        if not task:
            return {"error": "任务不存在"}
        
        now = datetime.now()
        report = {
            "task": task.model_dump(mode='json'),
            "status_analysis": self._analyze_task_status(task),
            "time_analysis": self._analyze_task_time(task, now),
            "risk_assessment": self._assess_task_risk(task, now)
        }
        
        return report
    
    def _analyze_task_status(self, task: Task) -> Dict[str, Any]:
        """分析任务状态"""
        analysis = {
            "current_status": task.status.value,
            "status_description": self._get_status_description(task.status),
            "is_active": task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS],
            "is_completed": task.status == TaskStatus.COMPLETED,
            "is_problematic": task.status in [TaskStatus.BLOCKED, TaskStatus.CANCELLED]
        }
        
        return analysis
    
    def _analyze_task_time(self, task: Task, now: datetime) -> Dict[str, Any]:
        """分析任务时间"""
        analysis = {
            "created_days_ago": (now - task.created_at).days if task.created_at else None,
            "updated_days_ago": (now - task.updated_at).days if task.updated_at else None,
            "has_due_date": bool(task.due_date),
            "is_overdue": False,
            "days_until_due": None
        }
        
        if task.due_date:
            if task.due_date < now:
                analysis["is_overdue"] = True
                analysis["overdue_days"] = (now - task.due_date).days
            else:
                analysis["days_until_due"] = (task.due_date - now).days
        
        return analysis
    
    def _assess_task_risk(self, task: Task, now: datetime) -> Dict[str, Any]:
        """评估任务风险"""
        risk_level = "low"
        risk_factors = []
        
        # 检查逾期
        if task.due_date and task.due_date < now and task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            risk_level = "high"
            risk_factors.append("任务已逾期")
        
        # 检查即将到期
        elif task.due_date and (task.due_date - now).days <= 3 and task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
            risk_level = "medium"
            risk_factors.append("任务即将到期")
        
        # 检查阻塞状态
        if task.status == TaskStatus.BLOCKED:
            risk_level = "high"
            risk_factors.append("任务被阻塞")
        
        # 检查长时间未更新
        if task.updated_at and (now - task.updated_at).days >= 14:
            risk_level = "medium"
            risk_factors.append("任务长时间未更新")
        
        # 检查长时间运行
        if task.status == TaskStatus.IN_PROGRESS and task.updated_at and (now - task.updated_at).days >= 7:
            risk_level = "medium"
            risk_factors.append("任务长时间运行中")
        
        # 高优先级任务
        if task.priority == TaskPriority.URGENT:
            risk_level = "high"
            risk_factors.append("任务优先级为紧急")
        elif task.priority == TaskPriority.HIGH:
            if risk_level == "low":
                risk_level = "medium"
            risk_factors.append("任务优先级为高")
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "needs_attention": risk_level in ["medium", "high"]
        }
    
    def _get_status_description(self, status: TaskStatus) -> str:
        """获取状态描述"""
        descriptions = {
            TaskStatus.PENDING: "待开始",
            TaskStatus.IN_PROGRESS: "进行中",
            TaskStatus.COMPLETED: "已完成",
            TaskStatus.CANCELLED: "已取消",
            TaskStatus.BLOCKED: "被阻塞"
        }
        return descriptions.get(status, "未知状态")
    
    def generate_health_report(self) -> Dict[str, Any]:
        """生成项目健康报告"""
        all_tasks = self.task_manager.get_all_tasks()
        now = datetime.now()
        
        # 基本统计
        total_tasks = len(all_tasks)
        completed_tasks = len(self.task_manager.get_tasks_by_status(TaskStatus.COMPLETED))
        in_progress_tasks = len(self.task_manager.get_tasks_by_status(TaskStatus.IN_PROGRESS))
        pending_tasks = len(self.task_manager.get_tasks_by_status(TaskStatus.PENDING))
        blocked_tasks_count = len(self.task_manager.get_tasks_by_status(TaskStatus.BLOCKED))
        
        # 问题任务
        overdue_tasks = self.check_overdue_tasks()
        due_soon_tasks = self.check_tasks_due_soon()
        stale_tasks = self.check_stale_tasks()
        long_running_tasks = self.check_long_running_tasks()
        
        # 计算健康指标
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        problem_rate = (len(overdue_tasks) + blocked_tasks_count) / total_tasks if total_tasks > 0 else 0
        
        # 评估整体健康状态
        if problem_rate > 0.3:
            health_status = "poor"
        elif problem_rate > 0.1:
            health_status = "fair"
        else:
            health_status = "good"
        
        report = {
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "pending_tasks": pending_tasks,
                "blocked_tasks": blocked_tasks_count,
                "completion_rate": completion_rate,
                "problem_rate": problem_rate,
                "health_status": health_status
            },
            "issues": {
                "overdue_tasks": len(overdue_tasks),
                "due_soon_tasks": len(due_soon_tasks),
                "stale_tasks": len(stale_tasks),
                "long_running_tasks": len(long_running_tasks)
            },
            "recommendations": self._generate_recommendations(
                overdue_tasks, due_soon_tasks, stale_tasks, long_running_tasks
            )
        }
        
        return report
    
    def _generate_recommendations(self, overdue_tasks: List[Task], 
                                 due_soon_tasks: List[Task],
                                 stale_tasks: List[Task], 
                                 long_running_tasks: List[Task]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if overdue_tasks:
            recommendations.append(f"有 {len(overdue_tasks)} 个任务已逾期，请优先处理")
        
        if due_soon_tasks:
            recommendations.append(f"有 {len(due_soon_tasks)} 个任务即将到期，请注意时间安排")
        
        if stale_tasks:
            recommendations.append(f"有 {len(stale_tasks)} 个任务长时间未更新，请检查状态")
        
        if long_running_tasks:
            recommendations.append(f"有 {len(long_running_tasks)} 个任务运行时间过长，请评估是否需要调整")
        
        if not recommendations:
            recommendations.append("项目状态良好，继续保持")
        
        return recommendations