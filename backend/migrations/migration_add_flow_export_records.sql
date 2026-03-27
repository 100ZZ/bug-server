USE bug_management;

-- 创建流程导出记录表
CREATE TABLE IF NOT EXISTS flow_export_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flow_id INT NOT NULL COMMENT '关联流程ID',
    name VARCHAR(200) NOT NULL COMMENT '导出名称',
    export_data JSON NOT NULL COMMENT '导出的完整数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (flow_id) REFERENCES api_test_flows(id) ON DELETE CASCADE,
    INDEX idx_flow_id (flow_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='流程导出记录表';

