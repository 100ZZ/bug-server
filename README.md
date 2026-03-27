# 质量管理系统

基于 Vue3 + Element Plus + FastAPI + MySQL 8 的质量与缺陷管理平台（界面品牌为「质量管理系统」），涵盖项目管理、缺陷跟踪、API 测试、测试用例与模型配置等能力。

## 功能特性

- ✅ **用户认证**：登录/登出、密码管理、JWT 认证
- ✅ **角色权限**：5 种角色（管理员、产品、开发、测试、游客），细粒度控制各模块操作
- ✅ **项目管理**：多项目、项目归档；需先在侧栏选择项目后使用项目相关菜单
- ✅ **项目协同**：迭代（Sprint）、需求、工作任务
- ✅ **用例管理**：测试用例维护、用例评审
- ✅ **缺陷管理**：创建、编辑、删除、查询缺陷，支持高级筛选
- ✅ **测试管理**：接口测试、流程测试、测试任务、代码扫描、测试文件管理
- ✅ **配置管理**：API 环境等配置（`/api-environments`）
- ✅ **模型管理**：模型列表与默认模型设置（对接 AI 等场景）
- ✅ **用户管理**：用户 CRUD、角色分配
- ✅ **统计分析**：按状态、优先级、严重程度、类型等维度统计（ECharts）
- ✅ **评论与历史**：缺陷讨论、操作历史记录
- ✅ **项目上下文**：侧栏项目选择器；各业务页可按当前项目过滤数据（扩展方式见 [项目过滤功能使用说明.md](./项目过滤功能使用说明.md)）

### 角色权限说明

| 角色 | 项目管理 | 用户管理 | 缺陷管理 | 说明 |
|------|---------|---------|---------|------|
| 管理员 (admin) | ✓✓✓✓ | ✓✓✓✓ | ✓✓✓✓ | 所有权限 |
| 产品 (product) | ✓✓✓✓ | 只读 | ✓✓✓✓ | 除用户管理外的主要写权限 |
| 开发 (developer) | ✓✓✓✓ | 只读 | ✓✓✓✓ | 除用户管理外的主要写权限 |
| 测试 (tester) | ✓✓✓✓ | 只读 | ✓✓✓✓ | 除用户管理外的主要写权限 |
| 游客 (guest) | 只读 | 只读 | 只读 | 各模块以只读为主 |

## 技术栈

### 后端
- FastAPI: 现代化的 Python Web 框架
- MySQL 8: 数据库
- SQLAlchemy: ORM 框架
- Pydantic: 数据验证
- Passlib + Bcrypt: 密码加密
- Python-JOSE: JWT 认证

### 前端
- Vue 3: 渐进式 JavaScript 框架（Composition API）
- TypeScript: 类型安全
- Element Plus: UI 组件库
- Vue Router: 路由管理（Hash 模式）
- Axios: HTTP 客户端
- ECharts: 统计图表

## 快速开始

### 1. 初始化数据库

```bash
# 示例：用客户端执行 SQL 文件（密码与账号以本机为准）
mysql -u root -pTest@123456 < backend/init_db.sql
```

或在 `mysql` 交互环境中执行 `source /绝对路径/backend/init_db.sql`。

### 2. 启动服务

**方式 0：一键启动（推荐本地开发）**

```bash
sh start_all.sh
```

说明见 [启动脚本说明.md](./启动脚本说明.md)（Ctrl+C 可同时停止前后端）。

**方式 1：前后端分终端启动**

```bash
# 终端 1 - 后端
./start_backend.sh

# 终端 2 - 前端
./start_frontend.sh
```

**方式 2：手动启动**

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

**方式 3：Docker Compose（适合生产或容器化环境）**

```bash
cd docker
./start.sh
```

详细说明见 [docker/README.md](./docker/README.md)；数据库初始化补充说明见 [docker/README_SQL_INIT.md](./docker/README_SQL_INIT.md)。

### 3. 停止服务

**脚本 / 手动进程：**
```bash
./stop_all.sh
# 或使用 start_all.sh 时在各终端按 Ctrl+C
```

**Docker Compose：**
```bash
cd docker
docker-compose down
```

- 后端：`http://localhost:43211`
- 前端：`http://localhost:11234`（路由为 Hash，例如 `http://localhost:11234/#/projects/list`）

## 数据库配置

默认配置（可在 `backend/config.py` 修改）：

- 主机：localhost
- 端口：3306
- 用户：root
- 密码：Test@123456
- 数据库：bug_management

## 默认账号

应用启动时会确保存在管理员账号（逻辑见 `backend/app.py` 中 `init_default_admin`）：

| 用户名 | 密码 | 邮箱 | 角色 |
|--------|------|------|------|
| admin | **admin123** | admin@example.com | 管理员 |

**重要提示**：
- 主要业务页面需要**登录**后才能访问；未登录时会弹出登录框。
- **游客 (guest)** 指登录后的只读角色，并非「免登录浏览全站」。
- 首次部署后请尽快修改管理员密码。
- 管理员在「用户管理」中新建用户时，若不填写密码，默认密码为**用户名**（与后端创建用户逻辑一致）。

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
├── backend/
│   ├── app.py                 # FastAPI 主应用与 API
│   ├── models.py              # 数据库模型
│   ├── schemas.py             # Pydantic schemas
│   ├── config.py              # 配置
│   ├── auth.py                # 认证（密码、JWT）
│   ├── permissions.py         # 权限校验
│   ├── init_db.sql            # 数据库初始化
│   ├── migrations/            # 手工迁移 SQL / 说明
│   ├── requirements.txt
│   └── venv/
├── docker/                    # Docker Compose、启动脚本与说明
├── frontend/
│   ├── src/
│   │   ├── views/             # 页面（项目、缺陷、用例、API 测试等）
│   │   ├── components/        # 公共组件（如侧栏项目选择器）
│   │   ├── api/               # 接口封装
│   │   ├── composables/       # usePermissions、项目上下文等
│   │   ├── router/            # 路由（Hash）
│   │   ├── App.vue
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts         # 开发代理 /api → 后端
│   └── package.json
├── README.md
├── QUICKSTART.md              # 更短的上手步骤
├── 权限系统说明.md
├── 认证系统说明.md
├── 启动脚本说明.md
├── 项目过滤功能使用说明.md
├── start_all.sh
├── start_backend.sh
├── start_frontend.sh
└── stop_all.sh
```

## 主要前端路由（需登录）

| 路径 | 说明 |
|------|------|
| `/#/projects/list` | 项目列表（入口） |
| `/#/projects/sprints` | 迭代 |
| `/#/projects/requirements` | 需求 |
| `/#/projects/worktasks` | 工作任务 |
| `/#/testcases/detail` | 测试用例 |
| `/#/testcases/review` | 用例评审 |
| `/#/bugs` | 缺陷 |
| `/#/apitest/api` 等 | 测试管理子模块 |
| `/#/api-environments` | 环境配置 |
| `/#/statistics` | 统计 |
| `/#/models` | 模型管理 |
| `/#/users` | 用户管理 |

## API 文档

启动后端后访问：

- Swagger UI: `http://localhost:43211/docs`
- ReDoc: `http://localhost:43211/redoc`

## 使用指南

### 1. 登录与导航

- 浏览器打开 `http://localhost:11234`，在登录框使用管理员或业务账号登录。
- 先在侧栏选择**当前项目**，再使用「项目协同」「用例管理」「缺陷管理」「测试管理」等菜单。

### 2. 管理员首次登录示例

```
用户名：admin
密码：admin123
```

### 3. 修改密码

- 登录后点击右上角用户区域，选择「修改密码」，成功后需重新登录。

### 4. 管理员创建用户

- 进入「用户管理」→「新建用户」；不填密码时，默认密码为**用户名**。

## 详细文档

- [权限系统说明.md](./权限系统说明.md) — 角色与各模块权限
- [认证系统说明.md](./认证系统说明.md) — 登录与密码
- [启动脚本说明.md](./启动脚本说明.md) — `start_all.sh` 等行为说明
- [项目过滤功能使用说明.md](./项目过滤功能使用说明.md) — 项目上下文与列表过滤扩展
- [QUICKSTART.md](./QUICKSTART.md) — 精简快速开始

## 开发说明

### 后端

1. 模型变更需同步数据库（初始化脚本或 `migrations/` 内说明）
2. 业务 API 集中在 `app.py`（可按模块再拆分）
3. 请求体验证使用 Pydantic schemas
4. 接口权限在 `permissions.py` 中维护

### 前端

1. 使用 Vue 3 Composition API
2. 类型与接口定义见 `src/api/`（含 `types.ts` 等）
3. 权限与当前用户见 `usePermissions` composable
4. 项目维度数据见 `useProjectContext` / `useProjectFilter` 与侧栏 `SidebarProjectSelector`

## 许可证

MIT License
