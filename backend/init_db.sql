-- 缺陷管理系统数据库初始化脚本
-- 注意：数据库由 Docker 环境变量 MYSQL_DATABASE 自动创建，这里不需要再创建
-- 但为了兼容非 Docker 环境，保留 CREATE DATABASE 语句（使用 IF NOT EXISTS）

-- 设置字符集，确保中文正确存储
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

CREATE DATABASE IF NOT EXISTS bug_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE bug_management;

-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '项目名称',
    `key` TEXT COMMENT '描述',
    description TEXT COMMENT '项目描述',
    `lead` VARCHAR(50) COMMENT '项目负责人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目表';

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    display_name VARCHAR(50) COMMENT '显示名称',
    avatar_url VARCHAR(255) COMMENT '头像URL',
    roles JSON COMMENT '用户角色列表',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    current_project_id INT COMMENT '当前选中的项目ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (current_project_id) REFERENCES projects(id) ON DELETE SET NULL,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_users_current_project_id (current_project_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 项目成员关联表（多对多关系）
CREATE TABLE IF NOT EXISTS project_members (
    project_id INT NOT NULL COMMENT '项目ID',
    user_id INT NOT NULL COMMENT '用户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目成员关联表';

-- 缺陷表
CREATE TABLE IF NOT EXISTS bugs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bug_key VARCHAR(30) NOT NULL UNIQUE COMMENT '缺陷唯一标识，如BUG-001',
    project_id INT NOT NULL COMMENT '所属项目ID',
    title VARCHAR(200) NOT NULL COMMENT '缺陷标题',
    page_url VARCHAR(500) COMMENT '访问页面URL',
    description TEXT COMMENT '缺陷详细描述',
    type ENUM('bug', 'defect', 'improvement', 'task') DEFAULT 'bug' COMMENT '类型',
    priority ENUM('blocker', 'critical', 'major', 'minor', 'trivial') DEFAULT 'major' COMMENT '优先级',
    severity ENUM('fatal', 'serious', 'general', 'slight', 'suggestion') DEFAULT 'general' COMMENT '严重程度',
    status ENUM('open', 'in_progress', 'resolved', 'closed', 'reopened', 'pending') DEFAULT 'open' COMMENT '状态',
    resolution ENUM('fixed', 'wontfix', 'duplicate', 'cannot_reproduce', 'deferred', '') DEFAULT '' COMMENT '解决方案',
    assignee_id INT COMMENT '指派人ID',
    reporter_id INT NOT NULL COMMENT '报告人ID',
    verifier_id INT COMMENT '验证人ID',
    environment TEXT COMMENT '环境信息',
    version VARCHAR(50) COMMENT '发现版本',
    fix_version VARCHAR(50) COMMENT '修复版本',
    module VARCHAR(100) COMMENT '所属模块',
    steps_to_reproduce TEXT COMMENT '重现步骤',
    expected_result TEXT COMMENT '期望结果',
    actual_result TEXT COMMENT '实际结果',
    attachments JSON COMMENT '附件列表',
    tags JSON COMMENT '标签列表',
    due_date DATE COMMENT '截止日期',
    estimated_hours DECIMAL(5,2) COMMENT '预估工时',
    actual_hours DECIMAL(5,2) COMMENT '实际工时',
    resolved_at TIMESTAMP NULL COMMENT '解决时间',
    closed_at TIMESTAMP NULL COMMENT '关闭时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (verifier_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_bug_key (bug_key),
    INDEX idx_project (project_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_assignee (assignee_id),
    INDEX idx_reporter (reporter_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='缺陷表';

-- 评论表
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bug_id INT NOT NULL COMMENT '缺陷ID',
    user_id INT NOT NULL COMMENT '评论人ID',
    content TEXT NOT NULL COMMENT '评论内容',
    attachments JSON COMMENT '附件列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_bug (bug_id),
    INDEX idx_user (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评论表';

-- 操作历史表
CREATE TABLE IF NOT EXISTS bug_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bug_id INT NOT NULL COMMENT '缺陷ID',
    user_id INT NOT NULL COMMENT '操作人ID',
    field VARCHAR(50) NOT NULL COMMENT '变更字段',
    old_value TEXT COMMENT '旧值',
    new_value TEXT COMMENT '新值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bug_id) REFERENCES bugs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_bug (bug_id),
    INDEX idx_user (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作历史表';

-- 迭代表
CREATE TABLE IF NOT EXISTS sprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '项目ID',
    name VARCHAR(100) NOT NULL COMMENT '迭代名称',
    goal TEXT COMMENT '迭代目标',
    owner VARCHAR(50) COMMENT '负责人',
    start_date DATE NOT NULL COMMENT '起始时间',
    end_date DATE NOT NULL COMMENT '截止时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_start_date (start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='迭代表';

-- 测试用例表
CREATE TABLE IF NOT EXISTS testcases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_key VARCHAR(30) NOT NULL UNIQUE COMMENT '用例唯一标识，如TC-001',
    project_id INT NOT NULL COMMENT '所属项目ID',
    title VARCHAR(200) NOT NULL COMMENT '用例标题',
    module VARCHAR(100) COMMENT '所属模块',
    precondition TEXT COMMENT '前置条件',
    steps JSON COMMENT '测试步骤',
    expected_result TEXT COMMENT '预期结果',
    priority ENUM('P0', 'P1', 'P2', 'P3', 'P4') DEFAULT 'P2' COMMENT '优先级',
    type ENUM('functional', 'non-functional') DEFAULT 'functional' COMMENT '用例类型',
    status ENUM('draft', 'active', 'deprecated') DEFAULT 'draft' COMMENT '状态',
    tags JSON COMMENT '标签列表',
    created_by INT NOT NULL COMMENT '创建人ID',
    updated_by INT COMMENT '更新人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_case_key (case_key),
    INDEX idx_project (project_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试用例表';

-- 用例评审表
CREATE TABLE IF NOT EXISTS testcase_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '所属项目ID',
    sprint_id INT COMMENT '关联迭代ID',
    name VARCHAR(200) NOT NULL COMMENT '评审名称',
    initiator_id INT NOT NULL COMMENT '发起人ID',
    start_date DATE NOT NULL COMMENT '发起时间',
    end_date DATE NOT NULL COMMENT '截止时间',
    status ENUM('not_started', 'in_progress', 'ended') DEFAULT 'not_started' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL,
    FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_project_id (project_id),
    INDEX idx_sprint_id (sprint_id),
    INDEX idx_initiator_id (initiator_id),
    INDEX idx_status (status),
    INDEX idx_start_date (start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用例评审表';

-- 用例评审项表（评审与用例的关联表，包含评审结果）
CREATE TABLE IF NOT EXISTS testcase_review_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL COMMENT '评审ID',
    testcase_id INT NOT NULL COMMENT '用例ID',
    reviewer_id INT COMMENT '评审人ID',
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '评审状态：待评审、通过、不通过',
    comments TEXT COMMENT '评审意见',
    reviewed_at TIMESTAMP NULL COMMENT '评审时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES testcase_reviews(id) ON DELETE CASCADE,
    FOREIGN KEY (testcase_id) REFERENCES testcases(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_review_id (review_id),
    INDEX idx_testcase_id (testcase_id),
    INDEX idx_reviewer_id (reviewer_id),
    INDEX idx_status (status),
    UNIQUE KEY uk_review_testcase (review_id, testcase_id) COMMENT '同一评审中同一用例只能添加一次'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用例评审项表';

-- 接口测试环境表
CREATE TABLE IF NOT EXISTS api_environments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '关联项目ID',
    name VARCHAR(100) NOT NULL COMMENT '环境名称',
    base_url VARCHAR(255) NOT NULL COMMENT '环境信息（基础URL）',
    description TEXT COMMENT '环境说明',
    headers JSON COMMENT '默认请求头',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_name (name),
    UNIQUE KEY uk_project_base_url (project_id, base_url)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='接口测试环境表';

-- 接口端点表
CREATE TABLE IF NOT EXISTS api_endpoints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '关联项目ID',
    name VARCHAR(200) NOT NULL COMMENT '接口名称',
    path VARCHAR(500) NOT NULL COMMENT '接口路径',
    method VARCHAR(10) NOT NULL COMMENT 'HTTP方法',
    description TEXT COMMENT '接口描述',
    tags JSON COMMENT '标签列表',
    parameters JSON COMMENT 'Swagger参数列表(path/query/header参数)',
    request_body JSON COMMENT 'Swagger请求体定义',
    is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_method (method),
    INDEX idx_path (path(255)),
    INDEX idx_favorite (is_favorite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='接口端点表';

-- 接口测试数据表
CREATE TABLE IF NOT EXISTS api_test_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint_id INT NOT NULL COMMENT '接口端点ID',
    name VARCHAR(100) NOT NULL COMMENT '测试数据名称',
    path_params JSON COMMENT '路径参数',
    query_params JSON COMMENT '查询参数',
    headers JSON COMMENT '请求头',
    body JSON COMMENT '请求体',
    expected_status INT DEFAULT 200 COMMENT '期望状态码',
    assertions JSON COMMENT '断言列表',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id) ON DELETE CASCADE,
    INDEX idx_endpoint (endpoint_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='接口测试数据表';

-- 接口执行记录表
CREATE TABLE IF NOT EXISTS api_execution_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint_id INT NOT NULL COMMENT '接口端点ID',
    test_data_id INT COMMENT '测试数据ID',
    environment_id INT NOT NULL COMMENT '环境ID',
    request_url TEXT COMMENT '完整请求URL',
    request_method VARCHAR(10) COMMENT '请求方法',
    request_headers JSON COMMENT '请求头',
    request_query_params JSON COMMENT '请求查询参数',
    request_path_params JSON COMMENT '请求路径参数',
    request_body JSON COMMENT '请求体',
    response_status INT COMMENT '响应状态码',
    response_headers JSON COMMENT '响应头',
    response_body TEXT COMMENT '响应体',
    response_time INT COMMENT '响应时间（毫秒）',
    success BOOLEAN DEFAULT FALSE COMMENT '是否成功',
    error_message TEXT COMMENT '错误信息',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (endpoint_id) REFERENCES api_endpoints(id) ON DELETE CASCADE,
    FOREIGN KEY (test_data_id) REFERENCES api_test_data(id) ON DELETE SET NULL,
    FOREIGN KEY (environment_id) REFERENCES api_environments(id) ON DELETE CASCADE,
    INDEX idx_endpoint (endpoint_id),
    INDEX idx_environment (environment_id),
    INDEX idx_executed_at (executed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='接口执行记录表';

-- 接口流程表
CREATE TABLE IF NOT EXISTS api_test_flows (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '关联项目ID',
    name VARCHAR(200) NOT NULL COMMENT '流程名称',
    description TEXT COMMENT '描述',
    environment_id INT COMMENT '默认环境',
    global_variables JSON COMMENT '全局变量',
    steps JSON COMMENT '步骤定义',
    is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (environment_id) REFERENCES api_environments(id) ON DELETE SET NULL,
    INDEX idx_project (project_id),
    INDEX idx_flow_favorite (is_favorite)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='接口流程测试表';

-- 流程变量表
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

-- 流程导出记录表
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

-- 测试文件管理表
CREATE TABLE IF NOT EXISTS test_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '文件名称',
    description TEXT COMMENT '描述',
    file_type VARCHAR(50) NOT NULL DEFAULT 'local' COMMENT '类型：flow（流程导出）、local（本地上传）',
    file_name VARCHAR(255) NOT NULL COMMENT '实际文件名',
    file_path VARCHAR(500) COMMENT '文件存储路径（本地上传时使用）',
    file_content JSON COMMENT '文件内容（流程导出时使用JSON存储）',
    file_size INT COMMENT '文件大小（字节）',
    mime_type VARCHAR(100) COMMENT 'MIME类型',
    flow_id INT COMMENT '关联的流程ID（如果是流程导出）',
    created_by INT COMMENT '创建人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (flow_id) REFERENCES api_test_flows(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_file_type (file_type),
    INDEX idx_flow_id (flow_id),
    INDEX idx_created_by (created_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试文件管理表';

-- 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    token_hash VARCHAR(255) NOT NULL COMMENT 'Token哈希值（用于验证）',
    ip_address VARCHAR(45) COMMENT '登录IP地址',
    user_agent TEXT COMMENT '用户代理信息',
    expires_at TIMESTAMP NOT NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后活动时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户会话表';

-- 代码扫描任务表
CREATE TABLE IF NOT EXISTS code_scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL COMMENT '关联项目ID',
    project_name VARCHAR(200) NOT NULL COMMENT '工程名称',
    branch VARCHAR(100) NOT NULL COMMENT '分支',
    scan_path VARCHAR(500) NOT NULL COMMENT '扫描路径',
    language VARCHAR(50) COMMENT '编程语言：Java, Python, Go, PHP等',
    sonar_project_key VARCHAR(200) COMMENT 'Sonar的projectKey',
    sonar_host VARCHAR(500) COMMENT 'Sonar的服务host URL',
    sonar_login VARCHAR(200) COMMENT 'Sonar的login token',
    scan_time TIMESTAMP NULL COMMENT '扫描时间',
    result VARCHAR(20) COMMENT '扫描结果：passed/failed',
    error_message TEXT COMMENT '扫描不通过的原因或错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    INDEX idx_project (project_id),
    INDEX idx_result (result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码扫描任务表';

-- 代码扫描结果表（简化版，仅记录扫描状态，详细结果请查看Sonar页面）
CREATE TABLE IF NOT EXISTS code_scan_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scan_id INT NOT NULL COMMENT '关联扫描任务ID',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending/completed/failed',
    error_message TEXT COMMENT '错误信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (scan_id) REFERENCES code_scans(id) ON DELETE CASCADE,
    INDEX idx_scan (scan_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='代码扫描结果表';

-- AI模型配置表
CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '模型名称',
    provider ENUM('openai', 'deepseek', 'qwen', 'doubao', 'local') NOT NULL COMMENT '提供商',
    type ENUM('api', 'local') NOT NULL COMMENT '类型',
    api_key TEXT COMMENT 'API密钥（加密存储）',
    api_base VARCHAR(500) COMMENT 'API基础URL',
    model_path VARCHAR(500) COMMENT '本地模型路径',
    model_name VARCHAR(200) COMMENT '模型标识/名称',
    is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认模型',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    description TEXT COMMENT '描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_is_default (is_default),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI模型配置表';

-- 测试任务表
CREATE TABLE IF NOT EXISTS test_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '任务名称',
    project_id INT NOT NULL COMMENT '关联项目ID',
    description TEXT COMMENT '任务描述',
    status ENUM('idle', 'running', 'success', 'failed') DEFAULT 'idle' COMMENT '状态：空闲|运行中|成功|失败',
    is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
    cron_expression VARCHAR(100) COMMENT 'Cron表达式，用于定时执行',
    environment_id INT COMMENT '定时执行时使用的环境ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (environment_id) REFERENCES api_environments(id) ON DELETE SET NULL,
    INDEX idx_project (project_id),
    INDEX idx_status (status),
    INDEX idx_is_favorite (is_favorite),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试任务表';

-- 测试任务项表（接口或流程）
CREATE TABLE IF NOT EXISTS test_task_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL COMMENT '关联任务ID',
    item_type ENUM('api', 'flow') NOT NULL COMMENT '类型：接口或流程',
    item_id INT NOT NULL COMMENT '接口ID或流程ID',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
    INDEX idx_task (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试任务项表';

-- 测试任务执行记录表
CREATE TABLE IF NOT EXISTS test_task_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL COMMENT '关联任务ID',
    environment_id INT COMMENT '环境ID',
    status ENUM('running', 'success', 'failed') DEFAULT 'running' COMMENT '执行状态',
    total_count INT DEFAULT 0 COMMENT '总数量',
    success_count INT DEFAULT 0 COMMENT '成功数量',
    failed_count INT DEFAULT 0 COMMENT '失败数量',
    execution_results JSON COMMENT '执行结果详情（每个接口/流程的执行结果）',
    error_message TEXT COMMENT '错误信息',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (environment_id) REFERENCES api_environments(id) ON DELETE SET NULL,
    INDEX idx_task (task_id),
    INDEX idx_status (status),
    INDEX idx_started_at (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='测试任务执行记录表';
