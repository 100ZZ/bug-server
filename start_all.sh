#!/bin/bash

# 清理函数
cleanup() {
    echo ""
    echo "======================================"
    echo "正在停止所有服务..."
    echo "======================================"
    
    # 停止后端 - 先尝试优雅关闭，然后强制关闭
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill -TERM $BACKEND_PID 2>/dev/null
        sleep 1
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
        echo "✅ 后端服务已停止"
    fi
    
    # 停止前端 - 先尝试优雅关闭，然后强制关闭
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        kill -TERM $FRONTEND_PID 2>/dev/null
        sleep 1
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill -9 $FRONTEND_PID 2>/dev/null
        fi
        echo "✅ 前端服务已停止"
    fi
    
    # 清理可能残留的进程（包括子进程）
    pkill -f "uvicorn app:app --host 0.0.0.0 --port 43211" 2>/dev/null
    pkill -f "vite --port 11234" 2>/dev/null
    
    echo ""
    echo "======================================"
    echo "✅ 所有服务已停止"
    echo "======================================"
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup SIGINT SIGTERM EXIT

echo "======================================"
echo "启动缺陷管理系统"
echo "======================================"

# 检查 MySQL 是否运行
if ! pgrep -x "mysqld" > /dev/null; then
    echo "❌ MySQL 未运行，请先启动 MySQL"
    exit 1
fi

echo "✅ MySQL 运行中"

# 启动后端
echo ""
echo "启动后端服务..."
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

python3 run_server.py &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "   访问: http://localhost:43211"
echo "   API 文档: http://localhost:43211/docs"

cd ..

# 等待后端启动
sleep 2

# 启动前端
echo ""
echo "启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "   访问: http://localhost:11234"

cd ..

echo ""
echo "======================================"
echo "🎉 所有服务启动成功！"
echo "======================================"
echo "前端: http://localhost:11234"
echo "后端: http://localhost:43211"
echo "API 文档: http://localhost:43211/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "======================================"
echo ""

# 等待所有后台进程
wait

