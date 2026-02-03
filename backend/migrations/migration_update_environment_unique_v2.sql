-- 更新环境表唯一约束：从 base_url 全局唯一改为 project_id + base_url 组合唯一
-- 执行时间：2026-01-22
-- 说明：同一项目下不能有重复的环境信息，但不同项目可以有相同的环境信息

-- 1. 删除原有的 base_url 唯一索引（如果存在）
SET @exist := (SELECT COUNT(*) FROM information_schema.statistics 
               WHERE table_schema = DATABASE() 
               AND table_name = 'api_environments' 
               AND index_name = 'uk_base_url');
SET @sqlstmt := IF(@exist > 0, 'ALTER TABLE api_environments DROP INDEX uk_base_url', 'SELECT "Index uk_base_url does not exist"');
PREPARE stmt FROM @sqlstmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. 添加 project_id + base_url 组合唯一索引（如果不存在）
SET @exist2 := (SELECT COUNT(*) FROM information_schema.statistics 
                WHERE table_schema = DATABASE() 
                AND table_name = 'api_environments' 
                AND index_name = 'uk_project_base_url');
SET @sqlstmt2 := IF(@exist2 = 0, 'ALTER TABLE api_environments ADD UNIQUE KEY uk_project_base_url (project_id, base_url)', 'SELECT "Index uk_project_base_url already exists"');
PREPARE stmt2 FROM @sqlstmt2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;
