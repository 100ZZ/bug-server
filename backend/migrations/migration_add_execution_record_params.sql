-- 为 api_execution_records 表添加 request_query_params 和 request_path_params 字段
-- 执行方式：mysql -u root -p bug_management < migration_add_execution_record_params.sql

USE bug_management;

-- 添加 request_query_params 字段
ALTER TABLE api_execution_records 
ADD COLUMN request_query_params JSON COMMENT '请求查询参数' AFTER request_headers;

-- 添加 request_path_params 字段
ALTER TABLE api_execution_records 
ADD COLUMN request_path_params JSON COMMENT '请求路径参数' AFTER request_query_params;

