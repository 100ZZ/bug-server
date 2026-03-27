#!/bin/bash

# Docker Compose 停止脚本

set -e

echo "=========================================="
echo "  停止 Bug Server Docker 服务"
echo "=========================================="
echo ""

# 停止服务
echo "🛑 停止服务..."
docker-compose down

echo ""
echo "✅ 服务已停止"
echo ""

