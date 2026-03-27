-- 迁移脚本：新增需求表(requirements)和任务表(work_tasks)
-- 适用范围：已有部署（docker-compose 升级时手动执行）
-- 执行方式：docker exec -i bug-server-mysql mysql -u root -pTest@123456 bug_management < migrate_add_requirements_and_work_tasks.sql

USE bug_management;

-- 需求表
CREATE TABLE IF NOT EXISTS requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '所属项目ID',
    sprint_id INT COMMENT '关联迭代ID',
    title VARCHAR(200) NOT NULL COMMENT '需求标题',
    content TEXT COMMENT '需求内容',
    priority ENUM('urgent', 'high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级：紧急/高/中/低',
    status ENUM('not_started', 'developing', 'testing', 'completed') DEFAULT 'not_started' COMMENT '状态：未开始/开发中/测试中/已完成',
    assignee_id INT COMMENT '处理人ID',
    created_by INT NOT NULL COMMENT '创建人ID',
    start_date DATE COMMENT '开始日期',
    due_date DATE COMMENT '截止日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,  -- NOT NULL，不能 SET NULL
    INDEX idx_project_id (project_id),
    INDEX idx_sprint_id (sprint_id),
    INDEX idx_assignee_id (assignee_id),
    INDEX idx_created_by (created_by),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='需求表';

-- 任务表
CREATE TABLE IF NOT EXISTS work_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '所属项目ID',
    sprint_id INT COMMENT '关联迭代ID',
    title VARCHAR(200) NOT NULL COMMENT '任务标题',
    content TEXT COMMENT '任务内容',
    priority ENUM('urgent', 'high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级：紧急/高/中/低',
    status ENUM('not_started', 'in_progress', 'completed') DEFAULT 'not_started' COMMENT '状态：未开始/处理中/已完成',
    assignee_id INT COMMENT '处理人ID',
    created_by INT NOT NULL COMMENT '创建人ID',
    start_date DATE COMMENT '开始日期',
    due_date DATE COMMENT '截止日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_project_id (project_id),
    INDEX idx_sprint_id (sprint_id),
    INDEX idx_assignee_id (assignee_id),
    INDEX idx_created_by (created_by),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务表';

SELECT 'Migration migrate_add_requirements_and_work_tasks completed.' AS result;
