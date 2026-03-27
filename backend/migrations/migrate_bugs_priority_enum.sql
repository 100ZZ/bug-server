-- 将 bugs.priority 从旧枚举 (blocker/critical/major/minor/trivial) 改为新枚举 (urgent/high/medium/low)
-- 与 backend/models.py 及 Excel 导入使用的优先级一致

-- 1. 扩展枚举，使新旧值同时存在
ALTER TABLE bugs
MODIFY COLUMN priority ENUM(
    'blocker', 'critical', 'major', 'minor', 'trivial',
    'urgent', 'high', 'medium', 'low'
) DEFAULT 'major' COMMENT '优先级';

-- 2. 将旧值映射到新值
UPDATE bugs SET priority = CASE priority
    WHEN 'blocker' THEN 'urgent'
    WHEN 'critical' THEN 'high'
    WHEN 'major' THEN 'medium'
    WHEN 'minor' THEN 'low'
    WHEN 'trivial' THEN 'low'
    ELSE 'medium'
END;

-- 3. 收缩为仅新枚举
ALTER TABLE bugs
MODIFY COLUMN priority ENUM('urgent', 'high', 'medium', 'low') DEFAULT 'medium' COMMENT '优先级';
