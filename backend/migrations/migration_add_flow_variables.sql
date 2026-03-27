USE bug_management;

-- 创建流程变量表
CREATE TABLE IF NOT EXISTS flow_variables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flow_id INT NOT NULL COMMENT '关联流程ID',
    `key` VARCHAR(100) NOT NULL COMMENT '变量名',
    `value` TEXT NOT NULL COMMENT '变量值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES api_test_flows(id) ON DELETE CASCADE,
    INDEX idx_flow_id (flow_id),
    UNIQUE KEY uk_flow_key (flow_id, `key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='流程局部变量表';

