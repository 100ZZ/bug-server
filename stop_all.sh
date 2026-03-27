#!/bin/bash

echo "======================================"
echo "停止缺陷管理系统"
echo "======================================"

# 停止后端
echo "停止后端服务..."
pkill -f "uvicorn app:app --host 0.0.0.0 --port 43211" 2>/dev/null
pkill -f "run_server.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端服务已停止"
else
    echo "⚠️  未找到运行中的后端服务"
fi

# 停止前端
echo "停止前端服务..."
pkill -f "vite --port 11234" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 前端服务已停止"
else
    echo "⚠️  未找到运行中的前端服务"
fi

echo ""
echo "======================================"
echo "✅ 服务停止完成"
echo "======================================"

