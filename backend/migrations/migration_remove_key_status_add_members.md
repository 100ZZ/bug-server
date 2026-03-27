# 项目表迁移说明

## 变更内容

1. **删除字段**
   - `key` (项目Key)
   - `status` (项目状态)

2. **新增表**
   - `project_members` - 项目成员关联表（多对多关系）

## 迁移SQL

```sql
-- 1. 创建项目成员关联表
CREATE TABLE IF NOT EXISTS project_members (
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目成员关联表';

-- 2. 删除 status 字段（如果存在）
ALTER TABLE projects DROP COLUMN IF EXISTS status;

-- 3. 删除 key 字段（如果存在，注意：如果数据库不支持 DROP COLUMN IF EXISTS，需要先检查）
-- 对于MySQL 8.0+，可以使用：
ALTER TABLE projects DROP COLUMN IF EXISTS `key`;

-- 对于MySQL 5.7，需要先检查是否存在，然后删除：
-- 手动执行：ALTER TABLE projects DROP COLUMN `key`;
```

## 注意事项

1. 删除 `key` 和 `status` 字段前，请确保没有其他代码依赖这些字段
2. 迁移前建议备份数据库
3. 如果项目中已有数据，迁移前需要考虑数据迁移策略

