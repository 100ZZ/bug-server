-- 为用户表添加当前项目ID字段
-- 用于存储用户当前选中的项目，实现全局项目过滤功能

ALTER TABLE users ADD COLUMN current_project_id INT COMMENT '当前选中的项目ID';

-- 添加外键约束
ALTER TABLE users 
ADD CONSTRAINT fk_user_current_project 
FOREIGN KEY (current_project_id) REFERENCES projects(id) ON DELETE SET NULL;

-- 添加索引
CREATE INDEX idx_users_current_project_id ON users(current_project_id);

