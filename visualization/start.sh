#!/bin/bash
# Quick start script for visualization server

echo "🌳 启动任务可视化调试工具..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# Install requirements if needed
if [ ! -f "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "📦 安装依赖..."
pip install -r requirements.txt

# Start the server
echo "🚀 启动服务器..."
echo "📍 访问地址: http://localhost:8000"
echo "🔄 按 Ctrl+C 停止服务器"

python server.py