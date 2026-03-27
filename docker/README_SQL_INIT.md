# SQL 初始化文件说明

## 文件结构

Docker Compose 部署时，MySQL 容器会自动执行 `docker-entrypoint-initdb.d/` 目录中的 SQL 文件，按**文件名字母顺序**执行。

### 执行顺序

1. **01_init_db.sql** (`backend/init_db.sql`)
   - 创建所有表结构（含 `requirements.parent_id`、`work_tasks.parent_id` 等）
   - 不包含初始数据插入

2. **02_init_data.sql** (`docker/02_init_data.sql`)
   - 插入初始管理员用户（admin/admin123）

3. **03_migrate_worktask_parent.sql**（`backend/migrations/migrate_add_worktask_parent.sql`）
   - 为 `work_tasks` 表补充 `parent_id`（子任务）及外键；**幂等**，若列已由 01 建好则仅执行 `SELECT` 跳过
   - 与 `init_db.sql` 同步维护：新部署以 01 为准，本文件用于兼容旧版 01 或未含该列的库

### 注意事项

1. **数据库创建**：`bug_management` 数据库由 Docker 环境变量 `MYSQL_DATABASE` 自动创建，SQL 文件中的 `CREATE DATABASE IF NOT EXISTS` 语句仅用于兼容非 Docker 环境。

2. **执行时机**：SQL 文件只在 MySQL 容器**首次启动**时执行。如果数据卷已存在，不会重新执行。

3. **重新初始化**：如需重新初始化数据库，需要删除 Docker 数据卷：
   ```bash
   docker-compose down -v  # 删除所有容器和数据卷
   docker-compose up -d     # 重新启动，会重新执行 SQL 文件
   ```

4. **字段说明**：
   - `users.roles` 字段使用 JSON 格式，例如：`["admin"]`
   - 管理员密码哈希值使用 bcrypt 加密（rounds=12）

### 文件映射

在 `docker-compose.yml` 中：
```yaml
volumes:
  - ../backend/init_db.sql:/docker-entrypoint-initdb.d/01_init_db.sql:ro
  - ./02_init_data.sql:/docker-entrypoint-initdb.d/02_init_data.sql:ro
  - ../backend/migrations/migrate_add_worktask_parent.sql:/docker-entrypoint-initdb.d/03_migrate_worktask_parent.sql:ro
```

### 已有数据卷升级（未删 volume）

`docker-entrypoint-initdb.d` **只在 MySQL 数据目录首次初始化时执行**。若容器一直沿用旧 volume，拉新代码后需要**手动**对运行中的库执行迁移，例如：

```bash
docker exec -i bug-server-mysql mysql -u root -p'Test@123456' bug_management < backend/migrations/migrate_add_worktask_parent.sql
```

（密码与库名请按实际 `.env` / compose 调整。）

### 修改初始数据

如需修改初始数据（如管理员密码），编辑 `docker/02_init_data.sql` 文件，然后删除数据卷重新部署。

生成新的密码哈希值：
```bash
python3 docker/generate_password_hash.py <新密码>
```
