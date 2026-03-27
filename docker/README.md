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
- **Python**: `100zz/test-python:3.12-slim`
- **Node.js**: `100zz/test-node:22-alpine`

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
- **基础镜像**: `100zz/test-python:3.12-slim`
- **端口**: 43211（可通过 `.env` 中的 `BACKEND_PORT` 修改）
- **技术栈**: FastAPI + Python 3.12
- **热重载**: 已启用（代码修改自动重启）

### 前端服务
- **容器名**: `bug-server-frontend-YYYYMMDD-HHMMSS`（自动添加时间戳后缀）
- **镜像名**: `bug-frontend:${IMAGE_TAG}`（标签在 `.env` 中手动指定，默认为 `latest`）
- **基础镜像**: `100zz/test-node:22-alpine`
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
| UPLOAD_HOST_DIR | 文件上传目录（宿主机路径） | /opt/bug-uploads |
| BUG_IMAGE_DIR | 缺陷图片目录（宿主机路径） | /opt/bug-images |
| CODE_SCAN_DIR | 代码扫描目录（宿主机路径） | /opt/code |
| SONAR_URL | 外部 SonarQube 服务地址（扫描页面调用） | 按实际填写 |
| SONAR_TOKEN | 外部 SonarQube 认证 Token（可选） | 按实际填写 |

## 数据持久化

### 数据库

MySQL 数据存储在 Docker 数据卷 `bug_mysql_data` 中，即使删除容器，数据也不会丢失。

如需备份数据：

```bash
# 备份
docker exec bug-server-mysql mysqldump -u root -p${MYSQL_ROOT_PASSWORD} bug_management > backup.sql

# 恢复
docker exec -i bug-server-mysql mysql -u root -p${MYSQL_ROOT_PASSWORD} bug_management < backup.sql
```

### 上传文件

文件管理功能（本地上传、流程导出）的文件**直接映射到宿主机目录**，方便随时查看和备份。

**默认存储路径：** `/opt/bug-uploads/`（可通过 `.env` 中的 `UPLOAD_HOST_DIR` 修改）

**目录结构（按文件类型和名称组织）：**
```
/opt/bug-uploads/
├── local/                        # 本地上传的文件
│   ├── 测试数据1/                # 文件管理中设置的"名称"
│   │   └── a1b2c3d4e5f6.json    # 实际文件（UUID命名）
│   ├── 用户信息/
│   │   └── x9y8z7w6v5u4.csv
│   └── ...
└── flow/                         # 流程导出的文件
    ├── 登录流程/
    │   └── f1e2d3c4b5a6.json
    ├── 订单流程/
    │   └── b5a6c7d8e9f0.json
    └── ...
```

| 存储类型 | 宿主机路径 | 容器内路径 | 说明 |
|----------|-----------|-----------|------|
| MySQL 数据 | Docker 卷 | `/var/lib/mysql` | 使用 Docker 数据卷 |
| 上传文件 | `/opt/bug-uploads/` | `/data/uploads/` | 直接映射到宿主机目录 |
| 缺陷图片 | `/opt/bug-images/` | `/data/images/` | 直接映射到宿主机目录 |

**首次部署前，请确保宿主机目录存在并有正确权限：**

```bash
# 创建目录
sudo mkdir -p /opt/bug-uploads/local /opt/bug-uploads/flow
sudo mkdir -p /opt/bug-images

# 设置权限（确保容器内进程可以读写）
sudo chmod -R 777 /opt/bug-uploads
sudo chmod -R 777 /opt/bug-images
```

**查看上传的文件：**

```bash
# 查看所有上传的文件
ls -la /opt/bug-uploads/

# 查看本地上传的文件（按名称分文件夹）
ls -la /opt/bug-uploads/local/

# 查看流程导出的文件（按名称分文件夹）
ls -la /opt/bug-uploads/flow/

# 查看某个文件夹下的文件
ls -la /opt/bug-uploads/flow/登录流程/

# 查看某个 JSON 文件内容（格式化输出）
cat /opt/bug-uploads/flow/登录流程/xxxxx.json | python -m json.tool
```

**备份上传文件：**

```bash
# 直接打包宿主机目录
tar czf bug-uploads-backup.tar.gz -C /opt bug-uploads

# 恢复
tar xzf bug-uploads-backup.tar.gz -C /opt
```

### 缺陷图片

缺陷截图**直接映射到宿主机目录**，不再存储在数据库中，避免数据库过大导致性能问题。

**默认存储路径：** `/opt/bug-images/`（可通过 `.env` 中的 `BUG_IMAGE_DIR` 修改）

**目录结构：**
```
/opt/bug-images/
├── BUG-001/                  # 以缺陷编号为文件夹名称
│   ├── a1b2c3d4.png
│   └── x9y8z7w6.jpg
├── BUG-002/
│   └── ...
└── ...
```

**查看缺陷图片：**

```bash
# 查看所有缺陷图片
ls -la /opt/bug-images/

# 查看某个缺陷的图片
ls -la /opt/bug-images/BUG-001/
```

**备份缺陷图片：**

```bash
# 直接打包宿主机目录
tar czf bug-images-backup.tar.gz -C /opt bug-images

# 恢复
tar xzf bug-images-backup.tar.gz -C /opt
```

### 代码扫描目录与外部 SonarQube

扫描功能**不部署 SonarQube 容器**，通过配置的**外部 SonarQube 服务**执行扫描。请在 `.env` 中设置 `SONAR_URL`、`SONAR_TOKEN`（或在后端/前端配置中指定），扫描页面会调用该地址。

代码目录需映射到宿主机，默认 `/opt/code` 映射到容器内（若扫描任务在容器内执行则需此映射；若仅由外部 Sonar 扫描则按实际需求配置）。

**配置方式：**

1. 将待扫描的代码放到 `/opt/code` 目录下（如需在宿主机上被扫描）：
```bash
# 例如
/opt/code/
├── arcana-saas/          # 项目1
├── my-java-project/      # 项目2
└── ...
```

2. 新增扫描任务时，路径填写容器内路径（与宿主机路径相同）：
```
扫描路径: /opt/code/arcana-saas
```

**自定义扫描目录：**

如需修改映射目录，编辑 `.env` 文件：
```bash
CODE_SCAN_DIR=/your/custom/path
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

