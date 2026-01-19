# SQL 初始化文件说明

## 文件结构

Docker Compose 部署时，MySQL 容器会自动执行 `docker-entrypoint-initdb.d/` 目录中的 SQL 文件，按**文件名字母顺序**执行。

### 执行顺序

1. **01_init_db.sql** (`backend/init_db.sql`)
   - 创建所有表结构
   - 不包含初始数据插入

2. **02_init_data.sql** (`docker/02_init_data.sql`)
   - 创建 SonarQube 数据库
   - 插入初始管理员用户（admin/admin123）

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
```

### 修改初始数据

如需修改初始数据（如管理员密码），编辑 `docker/02_init_data.sql` 文件，然后删除数据卷重新部署。

生成新的密码哈希值：
```bash
python3 docker/generate_password_hash.py <新密码>
```
