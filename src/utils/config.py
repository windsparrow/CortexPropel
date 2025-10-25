"""
配置管理模块
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """配置类"""
    
    def __init__(self, env_file: Optional[str] = None):
        # 加载环境变量
        if env_file:
            load_dotenv(env_file)
        else:
            # 尝试加载默认的.env文件
            load_dotenv()
        
        # LLM 配置
        self.llm_provider = os.getenv("LLM_PROVIDER", "deepseek")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        # 数据存储配置
        self.data_dir = os.getenv("DATA_DIR", "./data")
        self.tasks_file = os.getenv("TASKS_FILE", "./data/tasks.json")
        
        # 日志配置
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "./logs/cortexpropel.log")
        
        # CLI 配置
        self.cli_theme = os.getenv("CLI_THEME", "dark")
        
        # 任务执行和调度配置
        self.task_default_execution_time: int = int(os.getenv("TASK_DEFAULT_EXECUTION_TIME", "60"))  # 默认执行时间（秒）
        self.task_auto_execute: bool = os.getenv("TASK_AUTO_EXECUTE", "false").lower() == "true"
        self.task_max_concurrent_tasks: int = int(os.getenv("TASK_MAX_CONCURRENT_TASKS", "3"))  # 最大并发任务数
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        if self.llm_provider == "deepseek" and not self.deepseek_api_key:
            print("错误: 使用 DeepSeek 时必须提供 DEEPSEEK_API_KEY")
            return False
        
        return True
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)


# 全局配置实例
config = Config()