-- 为 api_test_flows 表添加 is_favorite 字段
-- 执行此 SQL 来添加 is_favorite 字段

-- 添加 is_favorite 字段
ALTER TABLE api_test_flows
ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏' 
AFTER steps;

-- 添加索引以优化查询性能
ALTER TABLE api_test_flows
ADD INDEX idx_flow_favorite (is_favorite);

