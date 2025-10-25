"""
任务服务模块
提供任务操作的高级接口
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import Task, TaskManager, TaskStatus, TaskPriority
from ..utils.config import config


class TaskService:
    """任务服务类"""
    
    def __init__(self, data_file: Optional[str] = None):
        data_file = data_file or config.tasks_file
        self.task_manager = TaskManager(data_file)
    
    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        parent_task_id: Optional[str] = None,
        estimated_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建新任务"""
        try:
            # 处理优先级
            try:
                task_priority = TaskPriority(priority.lower())
            except ValueError:
                task_priority = TaskPriority.MEDIUM
            
            # 处理截止日期
            task_due_date = None
            if due_date:
                try:
                    task_due_date = datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    # 尝试其他日期格式
                    try:
                        task_due_date = datetime.strptime(due_date, "%Y/%m/%d")
                    except ValueError:
                        pass
            
            # 创建任务
            task = Task(
                title=title,
                description=description,
                priority=task_priority,
                due_date=task_due_date,
                parent_task_id=parent_task_id,
                tags=tags or [],
                estimated_hours=estimated_hours
            )
            
            # 添加到任务管理器
            task_id = self.task_manager.add_task(task)
            
            # 如果有父任务，将此任务添加为子任务
            if parent_task_id:
                parent_task = self.task_manager.get_task(parent_task_id)
                if parent_task:
                    parent_task.add_subtask(task_id)
                    self.task_manager.save_tasks()
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"任务 '{title}' 创建成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"创建任务失败: {str(e)}"
            }
    
    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        estimated_hours: Optional[float] = None,
        actual_hours: Optional[float] = None
    ) -> Dict[str, Any]:
        """更新任务"""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"未找到ID为 {task_id} 的任务"
                }
            
            # 更新任务属性
            if title is not None:
                task.title = title
            
            if description is not None:
                task.description = description
            
            if status is not None:
                try:
                    task.update_status(TaskStatus(status.lower()))
                except ValueError:
                    return {
                        "success": False,
                        "error": "Invalid status",
                        "message": f"无效的状态值: {status}"
                    }
            
            if priority is not None:
                try:
                    task.priority = TaskPriority(priority.lower())
                except ValueError:
                    return {
                        "success": False,
                        "error": "Invalid priority",
                        "message": f"无效的优先级值: {priority}"
                    }
            
            if due_date is not None:
                try:
                    task.due_date = datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    try:
                        task.due_date = datetime.strptime(due_date, "%Y/%m/%d")
                    except ValueError:
                        return {
                            "success": False,
                            "error": "Invalid date format",
                            "message": f"无效的日期格式: {due_date}，请使用 YYYY-MM-DD 或 YYYY/MM/DD 格式"
                        }
            
            if tags is not None:
                task.tags = tags
            
            if estimated_hours is not None:
                task.estimated_hours = estimated_hours
            
            if actual_hours is not None:
                task.actual_hours = actual_hours
            
            task.updated_at = datetime.now()
            self.task_manager.save_tasks()
            
            return {
                "success": True,
                "message": f"任务 '{task.title}' 更新成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"更新任务失败: {str(e)}"
            }
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """获取任务详情"""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"未找到ID为 {task_id} 的任务"
                }
            
            return {
                "success": True,
                "task": task.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"获取任务失败: {str(e)}"
            }
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        parent_task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """列出任务"""
        try:
            tasks = self.task_manager.get_all_tasks()
            
            # 过滤任务
            if status:
                try:
                    status_enum = TaskStatus(status.lower())
                    tasks = [task for task in tasks if task.status == status_enum]
                except ValueError:
                    pass
            
            if priority:
                try:
                    priority_enum = TaskPriority(priority.lower())
                    tasks = [task for task in tasks if task.priority == priority_enum]
                except ValueError:
                    pass
            
            if parent_task_id:
                tasks = [task for task in tasks if task.parent_task_id == parent_task_id]
            
            return {
                "success": True,
                "tasks": [task.to_dict() for task in tasks],
                "count": len(tasks)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"获取任务列表失败: {str(e)}"
            }
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """删除任务"""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"未找到ID为 {task_id} 的任务"
                }
            
            task_title = task.title
            success = self.task_manager.delete_task(task_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"任务 '{task_title}' 删除成功"
                }
            else:
                return {
                    "success": False,
                    "error": "Delete failed",
                    "message": f"删除任务失败"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"删除任务失败: {str(e)}"
            }
    
    def add_task_note(self, task_id: str, content: str) -> Dict[str, Any]:
        """添加任务笔记"""
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"未找到ID为 {task_id} 的任务"
                }
            
            task.add_note(content)
            self.task_manager.save_tasks()
            
            return {
                "success": True,
                "message": f"笔记添加成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"添加笔记失败: {str(e)}"
            }
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        try:
            all_tasks = self.task_manager.get_all_tasks()
            
            # 按状态统计
            status_counts = {}
            for status in TaskStatus:
                status_counts[status.value] = len([task for task in all_tasks if task.status == status])
            
            # 按优先级统计
            priority_counts = {}
            for priority in TaskPriority:
                priority_counts[priority.value] = len([task for task in all_tasks if task.priority == priority])
            
            # 计算完成率
            total_tasks = len(all_tasks)
            completed_tasks = status_counts.get("completed", 0)
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # 计算逾期任务数
            now = datetime.now()
            overdue_tasks = len([
                task for task in all_tasks 
                if task.due_date and task.due_date < now and task.status != TaskStatus.COMPLETED
            ])
            
            return {
                "success": True,
                "total_tasks": total_tasks,
                "status_counts": status_counts,
                "priority_counts": priority_counts,
                "completion_rate": round(completion_rate, 2),
                "overdue_tasks": overdue_tasks
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"获取统计信息失败: {str(e)}"
            }