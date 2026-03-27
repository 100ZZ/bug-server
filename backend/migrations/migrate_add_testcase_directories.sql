-- 迁移：新增用例目录表
-- 适用范围：已有部署（本地或 Docker Compose），用于替代旧的 [目录占位] 用例方案
-- 执行方式：mysql -u <user> -p <db_name> < migrate_add_testcase_directories.sql

CREATE TABLE IF NOT EXISTS testcase_directories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '所属项目ID',
    path VARCHAR(500) NOT NULL COMMENT '完整路径，如"模块A/子模块B"',
    name VARCHAR(200) NOT NULL COMMENT '目录名（最后一段）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_project_path (project_id, path),
    INDEX idx_project_id (project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用例目录表';
