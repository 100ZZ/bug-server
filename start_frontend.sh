#!/bin/bash

echo "======================================"
echo "启动前端服务"
echo "======================================"

cd frontend

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

echo ""
echo "✅ 启动前端服务..."
echo "   访问: http://localhost:11234"
echo ""
echo "按 Ctrl+C 停止服务"
echo "======================================"
echo ""

# 前台运行
npm run dev

