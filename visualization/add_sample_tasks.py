#!/usr/bin/env python3
"""
Quick test script to populate some sample tasks for visualization testing.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.task_manager import TaskManager

def add_sample_tasks():
    """Add some sample tasks for testing visualization."""
    task_manager = TaskManager()
    
    print("🧪 添加示例任务用于可视化测试...")
    
    # Add some sample tasks
    sample_inputs = [
        "准备项目文档",
        "设计系统架构", 
        "实现用户认证功能",
        "编写单元测试",
        "部署到测试环境"
    ]
    
    for user_input in sample_inputs:
        print(f"📝 处理任务: {user_input}")
        result = task_manager.process_user_input(user_input)
        if result.get("success"):
            print(f"✅ 已添加任务: {result.get('message', '成功')}")
        else:
            print(f"❌ 添加失败: {result.get('message', '未知错误')}")
    
    print("\n🎉 示例任务添加完成！")
    print("🌐 请访问 http://localhost:8000 查看可视化结果")

if __name__ == "__main__":
    add_sample_tasks()