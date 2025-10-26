"""
CortexPropel核心引擎
整合任务管理和AI意图理解功能
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.task import TaskManager, TaskStatus, TaskPriority
from ai.intent_analyzer import TaskAgent
from ai.llm_client import get_llm_client


class CortexPropelEngine:
    """CortexPropel核心引擎"""
    
    def __init__(self, config_file: str = "config.ini", tasks_file: str = "tasks.json"):
        """初始化引擎"""
        self.config_file = config_file
        self.tasks_file = tasks_file
        self.setup_logging()
        self.task_manager = TaskManager(tasks_file)
        
        # 尝试初始化AI组件，如果失败则只启用基础功能
        try:
            self.llm_client = get_llm_client(config_file)
            self.task_agent = TaskAgent(self.task_manager, self.llm_client)
            self.ai_enabled = True
            self.logger.info("CortexPropel引擎初始化完成（AI功能已启用）")
        except Exception as e:
            self.llm_client = None
            self.task_agent = None
            self.ai_enabled = False
            self.logger.warning(f"AI功能初始化失败: {str(e)}，将只启用基础功能")
            self.logger.info("CortexPropel引擎初始化完成（基础功能已启用）")
    
    def setup_logging(self):
        """设置日志"""
        import configparser
        
        # 读取日志配置
        config = configparser.ConfigParser()
        config.read(self.config_file, encoding='utf-8')
        
        log_level = config.get('logging', 'level', fallback='INFO')
        log_file = config.get('logging', 'file', fallback='cortexpropel.log')
        
        # 配置日志
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def process_natural_language_input(self, user_input: str) -> Dict[str, Any]:
        """处理自然语言输入"""
        try:
            # 检查AI功能是否可用
            if not self.ai_enabled or not self.task_agent:
                return {
                    "error": "AI功能当前不可用",
                    "suggestion": "请配置API密钥以启用AI功能，或使用直接命令操作任务"
                }
            
            self.logger.info(f"收到用户输入: {user_input}")
            
            # 使用AI智能体处理输入
            result = self.task_agent.process_input(user_input)
            
            if "error" in result:
                self.logger.error(f"处理失败: {result['error']}")
            else:
                self.logger.info(f"处理成功: {result.get('action', 'unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"处理用户输入时发生错误: {str(e)}")
            return {
                "error": f"处理失败: {str(e)}",
                "suggestion": "请检查配置和网络连接，或稍后重试"
            }
    
    def create_task_directly(self, title: str, description: str = "",
                           priority: TaskPriority = TaskPriority.MEDIUM,
                           due_date: Optional[datetime] = None) -> Dict[str, Any]:
        """直接创建任务（绕过AI理解）"""
        try:
            task = self.task_manager.create_task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date
            )
            
            self.logger.info(f"直接创建任务: {task.title}")
            
            return {
                "action": "create_task",
                "task": task.model_dump(mode='json'),
                "message": f"成功创建任务: {task.title}"
            }
            
        except Exception as e:
            self.logger.error(f"直接创建任务失败: {str(e)}")
            return {
                "error": f"创建任务失败: {str(e)}"
            }
    
    def update_task_directly(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """直接更新任务（绕过AI理解）"""
        try:
            updated_task = self.task_manager.update_task(task_id, **kwargs)
            
            if updated_task:
                self.logger.info(f"直接更新任务: {updated_task.title}")
                return {
                    "action": "update_task",
                    "task": updated_task.model_dump(mode='json'),
                    "message": f"成功更新任务: {updated_task.title}"
                }
            else:
                return {
                    "error": "任务不存在"
                }
                
        except Exception as e:
            self.logger.error(f"直接更新任务失败: {str(e)}")
            return {
                "error": f"更新任务失败: {str(e)}"
            }
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        try:
            all_tasks = self.task_manager.get_all_tasks()
            
            # 按状态统计
            status_stats = {}
            for status in TaskStatus:
                count = len(self.task_manager.get_tasks_by_status(status))
                status_stats[status.value] = count
            
            # 按优先级统计
            priority_stats = {}
            for priority in TaskPriority:
                count = len(self.task_manager.get_tasks_by_priority(priority))
                priority_stats[priority.value] = count
            
            # 计算完成率和问题率
            total_tasks = len(all_tasks)
            completed_tasks = status_stats.get(TaskStatus.COMPLETED.value, 0)
            blocked_tasks = status_stats.get(TaskStatus.BLOCKED.value, 0)
            cancelled_tasks = status_stats.get(TaskStatus.CANCELLED.value, 0)
            
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
            problem_rate = (blocked_tasks + cancelled_tasks) / total_tasks if total_tasks > 0 else 0
            
            return {
                "total_tasks": total_tasks,
                "status_distribution": status_stats,
                "priority_distribution": priority_stats,
                "completion_rate": completion_rate,
                "problem_rate": problem_rate
            }
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {str(e)}")
            return {
                "error": f"获取统计信息失败: {str(e)}"
            }
    
    def get_all_tasks(self) -> list:
        """获取所有任务"""
        try:
            tasks = self.task_manager.get_all_tasks()
            return [task.model_dump(mode='json') for task in tasks]
        except Exception as e:
            self.logger.error(f"获取任务列表失败: {str(e)}")
            return []
    
    def search_tasks(self, keyword: str) -> list:
        """搜索任务"""
        try:
            tasks = self.task_manager.search_tasks(keyword)
            return [task.model_dump(mode='json') for task in tasks]
        except Exception as e:
            self.logger.error(f"搜索任务失败: {str(e)}")
            return []
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取任务"""
        try:
            task = self.task_manager.get_task(task_id)
            return task.model_dump(mode='json') if task else None
        except Exception as e:
            self.logger.error(f"获取任务失败: {str(e)}")
            return None
    
    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        try:
            result = self.task_manager.delete_task(task_id)
            if result:
                self.logger.info(f"删除任务: {task_id}")
            return result
        except Exception as e:
            self.logger.error(f"删除任务失败: {str(e)}")
            return False