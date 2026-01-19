-- 为 test_tasks 表添加定时执行相关字段

-- 添加 Cron 表达式字段
ALTER TABLE test_tasks ADD COLUMN cron_expression VARCHAR(100) COMMENT 'Cron表达式，用于定时执行';

-- 添加环境ID字段（用于定时执行时指定环境）
ALTER TABLE test_tasks ADD COLUMN environment_id INT COMMENT '定时执行时使用的环境ID';

-- 添加外键约束
ALTER TABLE test_tasks 
ADD CONSTRAINT fk_test_task_environment 
FOREIGN KEY (environment_id) 
REFERENCES api_environments(id) 
ON DELETE SET NULL;

-- 添加索引以提高查询性能
CREATE INDEX idx_test_tasks_cron_expression ON test_tasks(cron_expression);
CREATE INDEX idx_test_tasks_environment_id ON test_tasks(environment_id);

