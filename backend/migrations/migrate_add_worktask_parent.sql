-- 任务表新增 parent_id（子任务关联）
-- 可重复执行：列已存在则跳过（适合 Docker 首次初始化与已有库升级）
-- 新环境完整建表仍以 backend/init_db.sql 为准（已含 parent_id）

USE bug_management;

SET @db := DATABASE();
SET @has_col := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = @db AND TABLE_NAME = 'work_tasks' AND COLUMN_NAME = 'parent_id'
);

SET @sql := IF(
  @has_col > 0,
  'SELECT ''work_tasks.parent_id already exists'' AS migrate_result',
  'ALTER TABLE work_tasks ADD COLUMN parent_id INT NULL COMMENT ''父任务ID（NULL表示顶级任务）'' AFTER created_by, ADD INDEX idx_parent_id (parent_id), ADD CONSTRAINT fk_worktask_parent FOREIGN KEY (parent_id) REFERENCES work_tasks(id) ON DELETE SET NULL'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT 'migrate_add_worktask_parent completed.' AS result;
