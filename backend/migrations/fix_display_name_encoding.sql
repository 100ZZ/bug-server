-- 修复用户显示名称乱码问题
-- 执行前请确保数据库连接使用 utf8mb4 字符集

USE bug_management;

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

-- 修复 admin 用户的显示名称
UPDATE users 
SET display_name = '系统管理员' 
WHERE username = 'admin' AND display_name != '系统管理员';
