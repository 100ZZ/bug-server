### 本地执行：
- ✅ sh start_all.sh
- ✅ ps：前后端的npm install和venv可以前置操作
### 容器部署：
- ✅ cd docker
- ✅ sh start.sh
<img width="3828" height="1848" alt="image" src="https://github.com/user-attachments/assets/f4d5b6e0-6a56-4b4a-bf3e-ec7f6d5b52b9" />


# 质量管理系统

基于 Vue3 + Element Plus + FastAPI + MySQL 8 的现代化缺陷管理平台，参考 Jira 设计。

## 功能特性

- ✅ **用户认证**：登录/登出、密码管理、JWT 认证
- ✅ **权限管理**：5 种角色（管理员、产品、开发、测试、游客）
- ✅ **项目管理**：支持多项目管理，项目归档
- ✅ **缺陷管理**：创建、编辑、删除、查询缺陷，支持高级筛选
- ✅ **用户管理**：完整的用户 CRUD，角色分配
- ✅ **统计分析**：按状态、优先级、严重程度、类型统计
- ✅ **评论功能**：支持缺陷讨论
- ✅ **操作历史**：记录所有变更

### 权限说明

| 角色 | 项目管理 | 用户管理 | 缺陷管理 | 说明 |
|------|---------|---------|---------|------|
| 管理员 (admin) | ✓✓✓✓ | ✓✓✓✓ | ✓✓✓✓ | 所有权限 |
| 产品 (product) | ✓✓✓✓ | 只读 | ✓✓✓✓ | 除用户管理外的所有权限 |
| 开发 (developer) | ✓✓✓✓ | 只读 | ✓✓✓✓ | 除用户管理外的所有权限 |
| 测试 (tester) | ✓✓✓✓ | 只读 | ✓✓✓✓ | 除用户管理外的所有权限 |
| 游客 (guest) | 只读 | 只读 | 只读 | 所有模块只读 |

## 技术栈

### 后端
- FastAPI: 现代化的 Python Web 框架
- MySQL 8: 数据库
- SQLAlchemy: ORM 框架
- Pydantic: 数据验证
- Passlib + Bcrypt: 密码加密
- Python-JOSE: JWT 认证

### 前端
- Vue 3: 渐进式 JavaScript 框架
- TypeScript: 类型安全
- Element Plus: UI 组件库
- Vue Router: 路由管理
- Axios: HTTP 客户端

## 快速开始

### 1. 初始化数据库

```bash
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source backend/init_db.sql
```

### 2. 启动服务

**方式1：分别启动（推荐）**

在两个不同的终端窗口中：

```bash
# 终端 1 - 启动后端
./start_backend.sh

# 终端 2 - 启动前端
./start_frontend.sh
```

**方式2：手动启动**

后端：
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

前端：
```bash
cd frontend
npm install
npm run dev
```

### 3. 停止服务

```bash
# 停止所有服务
./stop_all.sh

# 或在各终端窗口按 Ctrl+C
```

后端运行在 `http://localhost:43211`  
前端运行在 `http://localhost:11234`

## 数据库配置

默认配置（可在 `backend/config.py` 修改）：

- 主机：localhost
- 端口：3306
- 用户：root
- 密码：Test@123456
- 数据库：bug_management

## 默认账号

系统初始化后会创建一个管理员账号：

| 用户名 | 密码 | 邮箱 | 角色 | 权限 |
|--------|------|------|------|------|
| admin | admin | admin@example.com | 管理员 | 所有权限 |

**首次登录**：
```
用户名：admin
密码：admin
```

**重要提示**：
- 未登录时，系统默认为**游客（guest）**身份，只能查看数据
- 首次登录后**请立即修改密码**
- 管理员可以在"用户管理"页面创建新用户
- 创建新用户时，如果不指定密码，默认密码为**用户名**
- 用户登录后可以在右上角个人中心修改密码

## 缺陷字段说明

| 字段 | 说明 | 可选值 |
|------|------|--------|
| 类型 | 缺陷类型 | 缺陷、故障、改进、任务 |
| 优先级 | 处理优先级 | 阻塞、严重、主要、次要、轻微 |
| 严重程度 | 影响程度 | 致命、严重、一般、轻微、建议 |
| 状态 | 当前状态 | 待处理、进行中、已解决、已关闭、重新打开 |
| 解决方案 | 解决方式 | 已修复、不予修复、重复、无法重现、延期 |

## 项目结构

```
bug-server/
├── backend/                    # 后端服务
│   ├── app.py                 # FastAPI 主应用
│   ├── models.py              # 数据库模型
│   ├── schemas.py             # Pydantic schemas
│   ├── config.py              # 配置文件
│   ├── auth.py                # 认证工具（密码加密、JWT）
│   ├── permissions.py         # 权限管理
│   ├── init_db.sql            # 数据库初始化脚本
│   ├── migrations/            # 数据库迁移脚本目录（中途优化问题的 SQL 和脚本）
│   ├── requirements.txt       # Python 依赖
│   └── venv/                  # Python 虚拟环境
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── api/              # API 接口
│   │   ├── composables/      # 组合式函数（权限管理）
│   │   ├── router/           # 路由配置
│   │   ├── App.vue           # 根组件
│   │   └── main.ts           # 入口文件
│   ├── index.html
│   └── package.json
├── README.md                  # 项目说明
├── 权限系统说明.md            # 权限系统详细文档
├── 认证系统说明.md            # 认证系统详细文档
├── start_all.sh              # 启动所有服务
├── start_backend.sh          # 启动后端
├── start_frontend.sh         # 启动前端
└── stop_all.sh               # 停止所有服务
```

## API 文档

启动后端服务后，访问：

- Swagger UI: `http://localhost:43211/docs`
- ReDoc: `http://localhost:43211/redoc`

## 使用指南

### 1. 未登录访问
- 访问 http://localhost:11234
- 默认为**游客身份**，只能查看数据
- 点击右上角"登录"按钮进行登录

### 2. 用户登录
```
用户名：admin
密码：admin@example.com
```

### 3. 修改密码
- 登录后点击右上角用户名
- 选择"修改密码"
- 输入旧密码和新密码
- 修改成功后需要重新登录

### 4. 管理员创建用户
- 进入"用户管理"页面
- 点击"新建用户"
- 填写基本信息（无需填写密码）
- 新用户使用邮箱作为默认密码登录

## 详细文档

- [权限系统说明.md](./权限系统说明.md) - 权限规则、角色定义
- [认证系统说明.md](./认证系统说明.md) - 登录认证、密码管理

## 开发说明

### 后端开发

1. 修改数据库模型后，需要重新初始化数据库
2. 所有 API 接口都在 `app.py` 中定义
3. 数据验证使用 Pydantic schemas
4. 权限控制在 `permissions.py` 中定义
5. 认证相关功能在 `auth.py` 中实现

### 前端开发

1. 组件使用 Vue 3 Composition API
2. 类型定义在 `src/api/types.ts`
3. API 调用统一封装在 `src/api/` 目录
4. 权限管理使用 `usePermissions` Composable

## 许可证

MIT License

