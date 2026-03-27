-- 添加 code_scans 表的 error_message 字段
-- 用于存储扫描不通过的原因或错误信息

ALTER TABLE code_scans ADD COLUMN IF NOT EXISTS error_message TEXT AFTER result;
