#!/bin/bash

echo "======================================"
echo "启动后端服务"
echo "======================================"

cd backend

# 创建或激活虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 检查并安装依赖
if ! python -c "import fastapi" &>/dev/null; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

echo ""
echo "✅ 启动后端服务..."
echo "   访问: http://localhost:43211"
echo "   API 文档: http://localhost:43211/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "======================================"
echo ""

# 前台运行（使用自定义启动脚本，过滤 401 日志）
python3 run_server.py

