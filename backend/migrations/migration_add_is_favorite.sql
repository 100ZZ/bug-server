-- 添加收藏字段到api_endpoints表
-- 执行此SQL来添加is_favorite字段
-- 如果字段已存在，执行会报错，可以忽略

USE bug_management;

-- 添加is_favorite字段
ALTER TABLE api_endpoints 
ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏' 
AFTER request_body;

-- 添加索引
ALTER TABLE api_endpoints 
ADD INDEX idx_favorite (is_favorite);
