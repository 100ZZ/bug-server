-- 初始化数据脚本
-- 这个文件会在表结构创建后执行，用于插入初始数据
-- 执行顺序：01_init_db.sql (创建表) -> 02_init_data.sql (插入数据)

-- 设置字符集，确保中文正确存储
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

USE bug_management;

-- 创建 SonarQube 数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS sonarqube CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 初始化管理员用户
-- 用户名：admin
-- 密码：admin123
-- 密码哈希值：使用 bcrypt 加密（rounds=12）
-- 注意：bcrypt 每次生成的哈希值都不同（因为 salt 随机），但都能正确验证密码
-- roles 字段使用 JSON 格式存储角色列表：["admin"]
INSERT IGNORE INTO users (username, email, password, display_name, roles, status) VALUES 
('admin', 'admin@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '系统管理员', '["admin"]', 'active');
