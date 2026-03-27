-- 迁移脚本：需求表新增 parent_id（子需求关联）
-- 执行方式：docker exec -i bug-server-mysql mysql -u root -pTest@123456 bug_management < migrate_add_requirement_parent.sql

USE bug_management;

ALTER TABLE requirements
    ADD COLUMN parent_id INT NULL COMMENT '父需求ID（NULL表示顶级需求）' AFTER created_by,
    ADD INDEX idx_parent_id (parent_id),
    ADD FOREIGN KEY fk_req_parent (parent_id) REFERENCES requirements(id) ON DELETE SET NULL;

SELECT 'Migration migrate_add_requirement_parent completed.' AS result;
