#!/usr/bin/env python3
"""
CortexPropel 入口脚本
"""

import sys
import os

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入CLI模块
from cli.main import cli

if __name__ == '__main__':
    cli()