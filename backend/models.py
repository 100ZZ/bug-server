"""数据库模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Date, DECIMAL, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from config import Base

# 项目成员关联表（多对多关系）
project_members = Table(
    'project_members',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.now)
)

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    key = Column(Text, nullable=True)  # 描述
    description = Column(Text)
    lead = Column("lead", String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    bugs = relationship("Bug", back_populates="project")
    members = relationship("User", secondary=project_members, backref="projects")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    display_name = Column(String(50))
    avatar_url = Column(String(255))
    roles = Column(JSON, default=list)  # 用户角色列表，例如：['admin', 'product']
    status = Column(Enum('active', 'inactive'), default='active')
    current_project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)  # 当前选中的项目
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    reported_bugs = relationship("Bug", foreign_keys="Bug.reporter_id", back_populates="reporter")
    assigned_bugs = relationship("Bug", foreign_keys="Bug.assignee_id", back_populates="assignee")
    verified_bugs = relationship("Bug", foreign_keys="Bug.verifier_id", back_populates="verifier")

class Bug(Base):
    __tablename__ = "bugs"
    
    id = Column(Integer, primary_key=True, index=True)
    bug_key = Column(String(30), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    page_url = Column(String(500))
    description = Column(Text)
    type = Column(Enum('bug', 'defect', 'improvement', 'task'), default='bug')
    priority = Column(Enum('blocker', 'critical', 'major', 'minor', 'trivial'), default='major', index=True)
    severity = Column(Enum('fatal', 'serious', 'general', 'slight', 'suggestion'), default='general')
    status = Column(Enum('open', 'in_progress', 'resolved', 'closed', 'reopened', 'pending'), default='open', index=True)
    resolution = Column(Enum('fixed', 'wontfix', 'duplicate', 'cannot_reproduce', 'deferred', ''), default='')
    assignee_id = Column(Integer, ForeignKey("users.id"), index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    verifier_id = Column(Integer, ForeignKey("users.id"))
    environment = Column(Text)
    version = Column(String(50))
    fix_version = Column(String(50))
    module = Column(String(100))
    steps_to_reproduce = Column(Text)
    expected_result = Column(Text)
    actual_result = Column(Text)
    attachments = Column(JSON)
    tags = Column(JSON)
    due_date = Column(Date)
    estimated_hours = Column(DECIMAL(5, 2))
    actual_hours = Column(DECIMAL(5, 2))
    resolved_at = Column(DateTime)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", back_populates="bugs")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_bugs")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_bugs")
    verifier = relationship("User", foreign_keys=[verifier_id], back_populates="verified_bugs")
    comments = relationship("Comment", back_populates="bug", cascade="all, delete-orphan")
    history = relationship("BugHistory", back_populates="bug", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey("bugs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    attachments = Column(JSON)
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    bug = relationship("Bug", back_populates="comments")
    user = relationship("User")

class BugHistory(Base):
    __tablename__ = "bug_history"
    
    id = Column(Integer, primary_key=True, index=True)
    bug_id = Column(Integer, ForeignKey("bugs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    field = Column(String(50), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    bug = relationship("Bug", back_populates="history")
    user = relationship("User")

class TestCase(Base):
    __tablename__ = "testcases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_key = Column(String(30), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    module = Column(String(100))
    precondition = Column(Text)
    steps = Column(JSON)
    expected_result = Column(Text)
    priority = Column(Enum('P0', 'P1', 'P2', 'P3', 'P4'), default='P2', index=True)
    type = Column(Enum('functional', 'non-functional'), default='functional')
    status = Column(Enum('draft', 'active', 'deprecated'), default='draft', index=True)
    tags = Column(JSON)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

class TestCaseReview(Base):
    """用例评审表"""
    __tablename__ = "testcase_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    sprint_id = Column(Integer, ForeignKey("sprints.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(200), nullable=False)  # 评审名称
    initiator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # 发起人ID
    start_date = Column(Date, nullable=False)  # 发起时间
    end_date = Column(Date, nullable=False)  # 截止时间
    status = Column(Enum('not_started', 'in_progress', 'ended'), default='not_started', index=True)  # 状态
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project")
    sprint = relationship("Sprint")
    initiator = relationship("User", foreign_keys=[initiator_id])
    review_items = relationship("TestCaseReviewItem", back_populates="review", cascade="all, delete-orphan")

class TestCaseReviewItem(Base):
    """用例评审项表（评审与用例的关联表，包含评审结果）"""
    __tablename__ = "testcase_review_items"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("testcase_reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    testcase_id = Column(Integer, ForeignKey("testcases.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # 评审人ID
    status = Column(Enum('pending', 'approved', 'rejected'), default='pending', index=True)  # 评审状态：待评审、通过、不通过
    comments = Column(Text)  # 评审意见
    reviewed_at = Column(DateTime)  # 评审时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    review = relationship("TestCaseReview", back_populates="review_items")
    testcase = relationship("TestCase")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

# ===== API Test Models =====
class ApiEnvironment(Base):
    """接口测试环境"""
    __tablename__ = "api_environments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)  # 关联项目
    name = Column(String(100), nullable=False)
    base_url = Column(String(255), nullable=False)
    description = Column(Text)
    headers = Column(JSON)  # 默认请求头
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", backref="api_environments")

class CodeScan(Base):
    """代码扫描任务"""
    __tablename__ = "code_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name = Column(String(200), nullable=False)  # 工程名称
    branch = Column(String(100), nullable=False)  # 分支
    scan_path = Column(String(500), nullable=False)  # 扫描路径
    language = Column(String(50))  # 编程语言：Java, Python, Go, PHP等
    sonar_project_key = Column(String(200))  # Sonar的projectKey
    sonar_host = Column(String(500))  # Sonar的服务host URL
    sonar_login = Column(String(200))  # Sonar的login token
    scan_time = Column(DateTime)  # 扫描时间
    result = Column(String(20))  # 扫描结果：passed/failed
    error_message = Column(Text)  # 扫描不通过的原因或错误信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", backref="code_scans")

class CodeScanResult(Base):
    """代码扫描结果（简化版，仅记录扫描状态）"""
    __tablename__ = "code_scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("code_scans.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default='pending')  # 状态：pending/completed/failed
    error_message = Column(Text)  # 错误信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    scan = relationship("CodeScan", backref="results")

class ApiEndpoint(Base):
    """接口端点"""
    __tablename__ = "api_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)  # 关联项目
    name = Column(String(200), nullable=False)  # 接口名称
    path = Column(String(500), nullable=False)  # 接口路径
    method = Column(String(10), nullable=False)  # HTTP方法
    description = Column(Text)  # 接口描述
    tags = Column(JSON)  # 标签列表
    parameters = Column(JSON)  # Swagger参数列表(path/query/header参数)
    request_body = Column(JSON)  # Swagger请求体定义
    is_favorite = Column(Boolean, default=False, index=True)  # 是否收藏
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", backref="api_endpoints")

class ApiTestData(Base):
    """接口测试数据"""
    __tablename__ = "api_test_data"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # 测试数据名称
    path_params = Column(JSON)  # 路径参数
    query_params = Column(JSON)  # 查询参数
    headers = Column(JSON)  # 请求头
    body = Column(JSON)  # 请求体
    expected_status = Column(Integer, default=200)  # 期望状态码
    assertions = Column(JSON)  # 断言列表
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    endpoint = relationship("ApiEndpoint", backref="test_data")

class ApiExecutionRecord(Base):
    """接口执行记录"""
    __tablename__ = "api_execution_records"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("api_endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    test_data_id = Column(Integer, ForeignKey("api_test_data.id", ondelete="SET NULL"))
    environment_id = Column(Integer, ForeignKey("api_environments.id", ondelete="CASCADE"), nullable=False, index=True)
    request_url = Column(Text)  # 完整请求URL
    request_method = Column(String(10))  # 请求方法
    request_headers = Column(JSON)  # 请求头
    request_query_params = Column(JSON)  # 请求查询参数
    request_path_params = Column(JSON)  # 请求路径参数
    request_body = Column(JSON)  # 请求体
    response_status = Column(Integer)  # 响应状态码
    response_headers = Column(JSON)  # 响应头
    response_body = Column(Text)  # 响应体（可能是大文本）
    response_time = Column(Integer)  # 响应时间（毫秒）
    success = Column(Boolean, default=False)  # 是否成功
    error_message = Column(Text)  # 错误信息
    executed_at = Column(DateTime, default=datetime.now, index=True)


class ApiTestFlow(Base):
    """接口流程测试配置"""
    __tablename__ = "api_test_flows"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    environment_id = Column(Integer, ForeignKey("api_environments.id", ondelete="SET NULL"))
    global_variables = Column(JSON)  # 流程级全局变量
    steps = Column(JSON)  # 流程步骤定义列表
    is_favorite = Column(Boolean, default=False, index=True)  # 是否收藏
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    project = relationship("Project", backref="api_test_flows")
    environment = relationship("ApiEnvironment", foreign_keys=[environment_id])
    variables = relationship("FlowVariable", back_populates="flow", cascade="all, delete-orphan")


class FlowVariable(Base):
    """流程局部变量"""
    __tablename__ = "flow_variables"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("api_test_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    
    flow = relationship("ApiTestFlow", back_populates="variables")


class Model(Base):
    """AI模型配置"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    provider = Column(Enum('openai', 'deepseek', 'qwen', 'doubao', 'local'), nullable=False)
    type = Column(Enum('api', 'local'), nullable=False)
    api_key = Column(Text)  # API密钥（加密存储）
    api_base = Column(String(500))  # API基础URL
    model_path = Column(String(500))  # 本地模型路径
    model_name = Column(String(200))  # 模型标识/名称
    is_default = Column(Boolean, default=False, index=True)  # 是否默认模型
    status = Column(Enum('active', 'inactive'), default='active', index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class TestTask(Base):
    """测试任务"""
    __tablename__ = "test_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 任务名称
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text)  # 任务描述
    status = Column(Enum('idle', 'running', 'success', 'failed'), default='idle', index=True)  # 状态：空闲|运行中|成功|失败
    is_favorite = Column(Boolean, default=False, index=True)  # 是否收藏
    cron_expression = Column(String(100))  # Cron表达式，用于定时执行
    environment_id = Column(Integer, ForeignKey("api_environments.id", ondelete="SET NULL"))  # 定时执行时使用的环境ID
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", backref="test_tasks")
    items = relationship("TestTaskItem", back_populates="task", cascade="all, delete-orphan", order_by="TestTaskItem.sort_order")
    executions = relationship("TestTaskExecution", back_populates="task", cascade="all, delete-orphan")


class TestTaskItem(Base):
    """测试任务项（接口或流程）"""
    __tablename__ = "test_task_items"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(Enum('api', 'flow'), nullable=False)  # 类型：接口或流程
    item_id = Column(Integer, nullable=False)  # 接口ID或流程ID
    sort_order = Column(Integer, default=0)  # 排序顺序
    created_at = Column(DateTime, default=datetime.now)
    
    task = relationship("TestTask", back_populates="items")


class TestTaskExecution(Base):
    """测试任务执行记录"""
    __tablename__ = "test_task_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    environment_id = Column(Integer, ForeignKey("api_environments.id", ondelete="SET NULL"))
    status = Column(Enum('running', 'success', 'failed'), default='running', index=True)  # 执行状态
    total_count = Column(Integer, default=0)  # 总数量
    success_count = Column(Integer, default=0)  # 成功数量
    failed_count = Column(Integer, default=0)  # 失败数量
    execution_results = Column(JSON)  # 执行结果详情（每个接口/流程的执行结果）
    error_message = Column(Text)  # 错误信息
    started_at = Column(DateTime, default=datetime.now, index=True)
    completed_at = Column(DateTime)  # 完成时间
    
    task = relationship("TestTask", back_populates="executions")
    environment = relationship("ApiEnvironment", foreign_keys=[environment_id])


class FlowExportRecord(Base):
    """流程导出记录"""
    __tablename__ = "flow_export_records"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("api_test_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # 导出名称
    export_data = Column(JSON, nullable=False)  # 导出的完整数据
    created_at = Column(DateTime, default=datetime.now, index=True)

    flow = relationship("ApiTestFlow", backref="export_records")


class TestFile(Base):
    """测试文件管理"""
    __tablename__ = "test_files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 文件名称
    description = Column(Text)  # 描述
    file_type = Column(String(50), nullable=False, default='local')  # 类型：flow（流程导出）、local（本地上传）
    file_name = Column(String(255), nullable=False)  # 实际文件名
    file_path = Column(String(500))  # 文件存储路径（本地上传时使用）
    file_content = Column(JSON)  # 文件内容（流程导出时使用JSON存储）
    file_size = Column(Integer)  # 文件大小（字节）
    mime_type = Column(String(100))  # MIME类型
    flow_id = Column(Integer, ForeignKey("api_test_flows.id", ondelete="SET NULL"), nullable=True, index=True)  # 关联的流程ID（如果是流程导出）
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)  # 创建人
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    flow = relationship("ApiTestFlow", backref="test_files")
    creator = relationship("User", backref="test_files")


class UserSession(Base):
    """用户会话表"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, index=True)  # Token的哈希值
    ip_address = Column(String(45))  # 支持IPv6
    user_agent = Column(Text)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    last_activity_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)
    is_active = Column(Boolean, default=True, index=True)

    user = relationship("User", backref="sessions")

class Sprint(Base):
    """迭代表"""
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    goal = Column(Text)  # 目标
    owner = Column(String(50))  # 负责人
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    project = relationship("Project", backref="sprints")
