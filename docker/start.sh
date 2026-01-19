#!/bin/bash

# Docker Compose 一键启动脚本

set -e

echo "=========================================="
echo "  Bug Server Docker 部署脚本"
echo "=========================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未检测到 Docker，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: 未检测到 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

# 检测系统架构
ARCH=$(uname -m)
echo "🔍 检测系统架构: $ARCH"

# 根据架构设置 MySQL 镜像
if [ "$ARCH" = "x86_64" ] || [ "$ARCH" = "amd64" ]; then
    MYSQL_IMAGE="100zz/test-mysql:8.0.20"
    echo "✅ 使用 x86 架构 MySQL 镜像: $MYSQL_IMAGE"
elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    MYSQL_IMAGE="100zz/test-mysql:8.0.39-arm64v8"
    echo "✅ 使用 ARM 架构 MySQL 镜像: $MYSQL_IMAGE"
else
    echo "⚠️  未知架构 $ARCH，使用默认 x86 镜像"
    MYSQL_IMAGE="100zz/test-mysql:8.0.20"
fi
echo ""

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp env.example .env
    echo "✅ 已创建 .env 文件"
fi

# 更新 .env 文件中的配置
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    # 更新 MySQL 镜像
    if grep -q "MYSQL_IMAGE=" .env 2>/dev/null; then
        sed -i '' "s|MYSQL_IMAGE=.*|MYSQL_IMAGE=$MYSQL_IMAGE|" .env
    else
        echo "MYSQL_IMAGE=$MYSQL_IMAGE" >> .env
    fi
    # 确保 MySQL 端口为 33306
    if grep -q "MYSQL_PORT=" .env 2>/dev/null; then
        sed -i '' "s|MYSQL_PORT=.*|MYSQL_PORT=33306|" .env
    else
        echo "MYSQL_PORT=33306" >> .env
    fi
    # 确保 NPM_REGISTRY 存在
    if ! grep -q "NPM_REGISTRY=" .env 2>/dev/null; then
        echo "NPM_REGISTRY=https://registry.npmmirror.com" >> .env
    fi
    # 确保 YARN_REGISTRY 存在
    if ! grep -q "YARN_REGISTRY=" .env 2>/dev/null; then
        echo "YARN_REGISTRY=https://registry.npmmirror.com" >> .env
    fi
else
    # Linux
    # 更新 MySQL 镜像
    if grep -q "MYSQL_IMAGE=" .env 2>/dev/null; then
        sed -i "s|MYSQL_IMAGE=.*|MYSQL_IMAGE=$MYSQL_IMAGE|" .env
    else
        echo "MYSQL_IMAGE=$MYSQL_IMAGE" >> .env
    fi
    # 确保 MySQL 端口为 33306
    if grep -q "MYSQL_PORT=" .env 2>/dev/null; then
        sed -i "s|MYSQL_PORT=.*|MYSQL_PORT=33306|" .env
    else
        echo "MYSQL_PORT=33306" >> .env
    fi
    # 确保 NPM_REGISTRY 存在
    if ! grep -q "NPM_REGISTRY=" .env 2>/dev/null; then
        echo "NPM_REGISTRY=https://registry.npmmirror.com" >> .env
    fi
    # 确保 YARN_REGISTRY 存在
    if ! grep -q "YARN_REGISTRY=" .env 2>/dev/null; then
        echo "YARN_REGISTRY=https://registry.npmmirror.com" >> .env
    fi
fi
echo "✅ 已设置 MySQL 镜像: $MYSQL_IMAGE"
echo "✅ 已设置 MySQL 端口: 33306"
echo "✅ 已确保 NPM/YARN registry 配置存在"
echo ""

# 生成容器名称后缀（时间戳格式：年月日-时分秒）
CONTAINER_SUFFIX=$(date +"-%Y%m%d-%H%M%S")
echo "🏷️  生成容器名称后缀: $CONTAINER_SUFFIX"
export CONTAINER_SUFFIX

# 更新 .env 文件中的容器后缀（如果不存在 IMAGE_TAG，则使用 latest）
if [ -z "$IMAGE_TAG" ]; then
    if ! grep -q "IMAGE_TAG=" .env 2>/dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "IMAGE_TAG=latest" >> .env
        else
            echo "IMAGE_TAG=latest" >> .env
        fi
    fi
fi
echo "✅ 镜像标签: ${IMAGE_TAG:-latest}（可在 .env 中手动修改 IMAGE_TAG）"
echo "✅ 容器名称后缀: $CONTAINER_SUFFIX"
echo ""

# 停止现有容器（如果存在）
echo "🛑 停止现有容器..."
docker-compose down 2>/dev/null || true

# 构建并启动服务
echo "🔨 构建并启动服务（镜像标签: ${IMAGE_TAG:-latest}，容器后缀: $CONTAINER_SUFFIX）..."
# 使用 .env 文件中的 IMAGE_TAG，docker-compose 会自动读取
# CONTAINER_SUFFIX 通过环境变量传递
CONTAINER_SUFFIX=$CONTAINER_SUFFIX docker-compose build
CONTAINER_SUFFIX=$CONTAINER_SUFFIX docker-compose up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "🌐 访问地址:"
echo "   - 前端: http://localhost:11234"
echo "   - 后端 API: http://localhost:43211"
echo "   - API 文档: http://localhost:43211/docs"
echo ""
echo "📝 查看日志:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 停止服务:"
echo "   docker-compose down"
echo ""

