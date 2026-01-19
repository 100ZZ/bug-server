# Docker 部署说明

本目录包含使用 Docker Compose 一键部署 bug-server 项目的配置文件。

## 快速开始

### 方式一：使用启动脚本（推荐）

在 `docker` 目录下执行：

```bash
./start.sh
```

脚本会自动：
- 检查 Docker 环境
- 创建 `.env` 文件（如果不存在）
- 构建并启动所有服务

### 方式二：手动启动

#### 1. 准备环境变量

复制环境变量示例文件并修改：

```bash
cp env.example .env
```

根据需要修改 `.env` 文件中的配置，特别是数据库密码等敏感信息。

#### 2. 启动服务

在 `docker` 目录下执行：

```bash
docker-compose up -d
```

### 3. 查看服务状态

```bash
docker-compose ps
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

### 5. 停止服务

使用脚本停止：

```bash
./stop.sh
```

或手动停止：

```bash
docker-compose down
```

### 6. 停止并删除数据卷（注意：会删除数据库数据）

```bash
docker-compose down -v
```

## 多架构支持

本项目支持 x86 和 ARM 架构，启动脚本会自动检测系统架构并选择对应的镜像：

**x86/amd64 架构：**
- **MySQL**: `100zz/test-mysql:8.0.20`
- **Python**: `100zz/test-python:3.12-slim`
- **Node.js**: `100zz/test-node:22-alpine`

**ARM64/aarch64 架构：**
- **MySQL**: `100zz/test-mysql:8.0.39-arm64v8`
- **Python**: `python:3.12-slim`（使用官方镜像）
- **Node.js**: `node:22-alpine`（使用官方镜像）

启动脚本会自动检测架构并设置正确的镜像，也可在 `.env` 文件中手动指定 `MYSQL_IMAGE`。

## 服务说明

### MySQL 8.x
- **容器名**: `bug-server-mysql`
- **镜像**: 根据系统架构自动选择（x86 或 ARM）
- **端口**: 33306（可通过 `.env` 中的 `MYSQL_PORT` 修改，映射到容器内的 3306）
- **数据卷**: `mysql_data`（持久化存储）
- **初始化脚本**: `init.sql`（首次启动时自动执行）

### 后端服务
- **容器名**: `bug-server-backend-YYYYMMDD-HHMMSS`（自动添加时间戳后缀）
- **镜像名**: `bug-backend:${IMAGE_TAG}`（标签在 `.env` 中手动指定，默认为 `latest`）
- **基础镜像**: 
  - x86: `100zz/test-python:3.12-slim`
  - ARM: `python:3.12-slim`
- **端口**: 43211（可通过 `.env` 中的 `BACKEND_PORT` 修改）
- **技术栈**: FastAPI + Python 3.12
- **热重载**: 已启用（代码修改自动重启）

### 前端服务
- **容器名**: `bug-server-frontend-YYYYMMDD-HHMMSS`（自动添加时间戳后缀）
- **镜像名**: `bug-frontend:${IMAGE_TAG}`（标签在 `.env` 中手动指定，默认为 `latest`）
- **基础镜像**: 
  - x86: `100zz/test-node:22-alpine`
  - ARM: `node:22-alpine`
- **端口**: 11234（可通过 `.env` 中的 `FRONTEND_PORT` 修改）
- **技术栈**: Vue 3 + Vite
- **热重载**: 已启用（代码修改自动刷新）

### 镜像标签和容器名称

- **镜像标签**：在 `.env` 文件中手动指定 `IMAGE_TAG`（默认为 `latest`），例如：
  - `IMAGE_TAG=1.0.0`
  - `IMAGE_TAG=v1.2.3`
  - `IMAGE_TAG=latest`

- **容器名称**：每次运行 `./start.sh` 时，会自动在容器名称后添加时间戳后缀（格式：`-YYYYMMDD-HHMMSS`），例如：
  - `bug-server-backend-20260106-140231`
  - `bug-server-frontend-20260106-140231`
  - `bug-server-mysql-20260106-140231`

这样可以方便地追踪不同时间启动的容器实例，同时镜像版本由你手动控制。

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_IMAGE | MySQL 镜像（自动检测架构） | 100zz/test-mysql:8.0.20 |
| MYSQL_ROOT_PASSWORD | MySQL root 密码 | Test@123456 |
| MYSQL_DATABASE | 数据库名 | bug_management |
| MYSQL_USER | 数据库用户 | buguser |
| MYSQL_PASSWORD | 数据库用户密码 | Test@123456 |
| MYSQL_PORT | MySQL 端口映射 | 33306 |
| IMAGE_TAG | 镜像标签（手动指定，如：1.0.0、v1.2.3） | latest |
| NPM_REGISTRY | npm 镜像源（如果无法访问外网） | 空（使用官方源） |
| YARN_REGISTRY | yarn 镜像源（如果无法访问外网） | 空（使用官方源） |
| BACKEND_PORT | 后端服务端口映射 | 43211 |
| FRONTEND_PORT | 前端服务端口映射 | 11234 |

## 数据持久化

MySQL 数据存储在 Docker 数据卷 `mysql_data` 中，即使删除容器，数据也不会丢失。

如需备份数据：

```bash
# 备份
docker exec bug-server-mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} bug_management > backup.sql

# 恢复
docker exec -i bug-server-mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} bug_management < backup.sql
```

## 开发模式

当前配置支持开发模式，代码修改会自动生效：

- **后端**: 使用 `--reload` 参数，代码修改后自动重启
- **前端**: Vite 热重载，代码修改后自动刷新浏览器

## 生产环境建议

如果用于生产环境，建议：

1. 修改所有默认密码
2. 使用 `.env` 文件管理敏感信息，不要提交到版本控制
3. 考虑使用 Nginx 作为反向代理
4. 前端构建为静态文件，使用 Nginx 提供服务
5. 配置 SSL/TLS 证书
6. 设置适当的资源限制（CPU、内存）

## 故障排查

### 数据库连接失败

1. 检查 MySQL 容器是否正常运行：
   ```bash
   docker-compose ps mysql
   ```

2. 检查数据库健康状态：
   ```bash
   docker-compose logs mysql
   ```

3. 确认环境变量配置正确

### 后端服务无法启动

1. 查看后端日志：
   ```bash
   docker-compose logs backend
   ```

2. 检查数据库连接配置

3. 确认依赖已正确安装

### 前端服务无法访问

1. 查看前端日志：
   ```bash
   docker-compose logs frontend
   ```

2. 检查端口是否被占用

3. 确认前端构建成功

### npm/yarn 网络连接问题

如果构建时出现网络超时错误（ETIMEDOUT），说明容器内无法访问外网的 npm/yarn registry。

**解决方案：**

1. **配置内网 registry**（推荐）：
   在 `.env` 文件中添加：
   ```bash
   NPM_REGISTRY=https://your-internal-registry.com
   YARN_REGISTRY=https://your-internal-registry.com
   ```

2. **使用国内镜像源**（如果允许）：
   ```bash
   NPM_REGISTRY=https://registry.npmmirror.com
   YARN_REGISTRY=https://registry.npmmirror.com
   ```

3. **配置 Docker 代理**：
   在 `docker-compose.yml` 的 frontend 服务中添加：
   ```yaml
   build:
     args:
       HTTP_PROXY: ${HTTP_PROXY}
       HTTPS_PROXY: ${HTTPS_PROXY}
   ```

配置完成后，重新构建：
```bash
docker-compose build frontend
```

## 常用命令

```bash
# 重新构建镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec mysql bash

# 查看资源使用情况
docker stats

# 清理未使用的资源
docker system prune
```

