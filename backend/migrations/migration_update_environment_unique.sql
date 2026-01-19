-- 更新环境表结构：环境名称可以重复，但环境信息（base_url）必须唯一
-- 执行时间：2026-01-06

-- 1. 删除可能存在的name唯一索引（如果有）
-- 注意：如果表中有name的唯一约束，需要先删除
-- ALTER TABLE api_environments DROP INDEX IF EXISTS uk_name;

-- 2. 添加base_url的唯一索引
-- 如果已存在重复的base_url，需要先处理重复数据
-- 检查是否有重复的base_url
-- SELECT base_url, COUNT(*) as count FROM api_environments GROUP BY base_url HAVING count > 1;

-- 添加唯一索引
ALTER TABLE api_environments 
ADD UNIQUE KEY uk_base_url (base_url);

-- 3. 保留name的普通索引（非唯一）
-- name索引已存在，无需修改

