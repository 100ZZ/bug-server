"""Pydantic schemas for API"""
from __future__ import annotations
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime, date
from decimal import Decimal

# ===== Project Schemas =====
class ProjectBase(BaseModel):
    name: str
    key: Optional[str] = None  # 描述
    description: Optional[str] = None
    lead: Optional[str] = None
    member_ids: Optional[List[int]] = None  # 项目成员ID列表

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None  # 描述
    description: Optional[str] = None
    lead: Optional[str] = None
    member_ids: Optional[List[int]] = None  # 项目成员ID列表

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    members: Optional[List['User']] = None  # 项目成员列表

    class Config:
        from_attributes = True

# ===== User Schemas =====
class UserBase(BaseModel):
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    roles: List[str] = Field(default_factory=list)  # 用户角色列表
    status: str = "active"

class UserCreate(UserBase):
    password: Optional[str] = None  # 如果不提供，默认使用邮箱作为密码

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    roles: Optional[List[str]] = None
    status: Optional[str] = None
    current_project_id: Optional[int] = None

class User(UserBase):
    id: int
    current_project_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ===== Auth Schemas =====
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ===== Bug Schemas =====
class BugBase(BaseModel):
    project_id: int
    title: str
    page_url: Optional[str] = None
    description: Optional[str] = None
    type: str = "bug"
    priority: str = "major"
    severity: str = "general"
    status: str = "open"
    resolution: str = ""
    assignee_id: Optional[int] = None
    verifier_id: Optional[int] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    fix_version: Optional[str] = None
    module: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    attachments: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None

class BugCreate(BugBase):
    reporter_id: int

class BugUpdate(BaseModel):
    title: Optional[str] = None
    page_url: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    priority: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    resolution: Optional[str] = None
    assignee_id: Optional[int] = None
    verifier_id: Optional[int] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    fix_version: Optional[str] = None
    module: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    attachments: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None

class Bug(BugBase):
    id: int
    bug_key: str
    reporter_id: int
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # 关联对象
    project: Optional[Project] = None
    reporter: Optional[User] = None
    assignee: Optional[User] = None
    verifier: Optional[User] = None

    class Config:
        from_attributes = True

# ===== Comment Schemas =====
class CommentBase(BaseModel):
    content: str
    attachments: Optional[List[str]] = None

class CommentCreate(CommentBase):
    bug_id: int
    user_id: int

class Comment(CommentBase):
    id: int
    bug_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True

# ===== Statistics Schemas =====
class BugStatistics(BaseModel):
    total: int
    open: int
    in_progress: int
    resolved: int
    closed: int
    by_priority: dict
    by_severity: dict
    by_type: dict

# ===== TestCase Schemas =====
class TestCaseBase(BaseModel):
    project_id: int
    title: str
    module: Optional[str] = None
    precondition: Optional[str] = None
    steps: Optional[List[dict]] = None
    expected_result: Optional[str] = None
    priority: str = "P2"
    type: str = "functional"
    status: str = "draft"
    tags: Optional[List[str]] = None

class TestCaseCreate(TestCaseBase):
    created_by: int

class TestCaseUpdate(BaseModel):
    title: Optional[str] = None
    module: Optional[str] = None
    precondition: Optional[str] = None
    steps: Optional[List[dict]] = None
    expected_result: Optional[str] = None
    priority: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    updated_by: Optional[int] = None

class TestCase(TestCaseBase):
    id: int
    case_key: str
    created_by: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    # 关联对象
    project: Optional[Project] = None
    creator: Optional[User] = None
    updater: Optional[User] = None

    class Config:
        from_attributes = True


# ===== API Test Schemas =====
class Assertion(BaseModel):
    type: Literal['status_code', 'response_body', 'response_header', 'response_time', 'json_path', 'contains']
    operator: Literal['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'contains', 'not_contains', 'exists', 'not_exists', 'is_empty', 'is_not_empty', 'regex']
    target: Optional[str] = None
    expected: Optional[Any] = None

# ===== API Test Schemas =====
class ApiEnvironmentBase(BaseModel):
    project_id: int
    name: str
    base_url: str
    description: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None

class ApiEnvironmentCreate(ApiEnvironmentBase):
    pass

class ApiEnvironmentUpdate(BaseModel):
    project_id: Optional[int] = None
    name: Optional[str] = None
    base_url: Optional[str] = None
    description: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None

class ApiEnvironment(ApiEnvironmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None
    
    class Config:
        from_attributes = True

class ApiEndpointBase(BaseModel):
    project_id: int
    name: str
    path: str
    method: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    parameters: Optional[List[Dict[str, Any]]] = None  # Swagger参数列表
    request_body: Optional[Dict[str, Any]] = None  # Swagger请求体定义
    is_favorite: Optional[bool] = False

class ApiEndpointCreate(ApiEndpointBase):
    pass

class ApiEndpointUpdate(BaseModel):
    project_id: Optional[int] = None
    name: Optional[str] = None
    path: Optional[str] = None
    method: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

class ApiEndpoint(ApiEndpointBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None
    
    class Config:
        from_attributes = True

class ApiTestDataBase(BaseModel):
    endpoint_id: int
    name: str
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    assertions: Optional[List[Dict[str, Any]]] = None  # 断言列表

class ApiTestDataCreate(ApiTestDataBase):
    pass

class ApiTestDataUpdate(BaseModel):
    name: Optional[str] = None
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: Optional[int] = None
    assertions: Optional[List[Dict[str, Any]]] = None  # 断言列表

class ApiTestData(ApiTestDataBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ApiExecuteRequest(BaseModel):
    environment_id: int
    test_data_id: Optional[int] = None
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    assertions: Optional[List[Dict[str, Any]]] = None  # 断言列表（可选，如果不提供则使用测试数据中的断言）
    global_variables: Optional[Dict[str, Any]] = None  # 全局变量，用于模板替换

class ApiExecutionRecord(BaseModel):
    id: int
    endpoint_id: int
    test_data_id: Optional[int] = None
    environment_id: int
    request_url: Optional[str] = None
    request_method: Optional[str] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_query_params: Optional[Dict[str, Any]] = None
    request_path_params: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, Any]] = None
    response_body: Optional[str] = None
    response_time: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    executed_at: datetime
    
    class Config:
        from_attributes = True


# ===== API Flow Schemas =====
class FlowExtractRule(BaseModel):
    name: str
    path: str  # 简单的点路径，如 "data.token"
    step_index: Optional[int] = None  # 从第几个接口提取（1-based），如果为None或0，则从当前接口提取


class FlowStep(BaseModel):
    endpoint_id: int
    environment_id: Optional[int] = None
    test_data_id: Optional[int] = None
    alias: Optional[str] = None  # 用于变量引用的别名
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    assertions: Optional[List[Assertion]] = None
    extracts: Optional[List[FlowExtractRule]] = None


class ApiTestFlowBase(BaseModel):
    project_id: int
    name: str
    description: Optional[str] = None
    environment_id: Optional[int] = None
    global_variables: Optional[Dict[str, Any]] = None
    steps: List[FlowStep] = []
    is_favorite: Optional[bool] = False


class ApiTestFlowCreate(ApiTestFlowBase):
    pass


class ApiTestFlowUpdate(BaseModel):
    project_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    environment_id: Optional[int] = None
    global_variables: Optional[Dict[str, Any]] = None
    steps: Optional[List[FlowStep]] = None
    is_favorite: Optional[bool] = None


class ApiTestFlow(ApiTestFlowBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None

    class Config:
        from_attributes = True


class ModelBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    provider: str  # 'openai', 'deepseek', 'qwen', 'doubao', 'local'
    type: str  # 'api' or 'local'
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_path: Optional[str] = None
    model_name: Optional[str] = None
    is_default: bool = False
    status: str = 'active'  # 'active' or 'inactive'
    description: Optional[str] = None


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = None
    provider: Optional[str] = None
    type: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model_path: Optional[str] = None
    model_name: Optional[str] = None
    is_default: Optional[bool] = None
    status: Optional[str] = None
    description: Optional[str] = None


class Model(ModelBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelTestRequest(BaseModel):
    prompt: str


class ModelTestResponse(BaseModel):
    response: str


# ===== Test Task Schemas =====
class TestTaskItemBase(BaseModel):
    item_type: str  # 'api' or 'flow'
    item_id: int
    sort_order: int = 0


class TestTaskItemCreate(TestTaskItemBase):
    pass


class TestTaskItem(TestTaskItemBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TestTaskBase(BaseModel):
    name: str
    project_id: int
    description: Optional[str] = None
    items: Optional[List[TestTaskItemCreate]] = None  # 任务项列表
    cron_expression: Optional[str] = None  # Cron表达式
    environment_id: Optional[int] = None  # 定时执行时使用的环境ID


class TestTaskCreate(TestTaskBase):
    pass


class TestTaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    items: Optional[List[TestTaskItemCreate]] = None
    is_favorite: Optional[bool] = None
    cron_expression: Optional[str] = None  # Cron表达式
    environment_id: Optional[int] = None  # 定时执行时使用的环境ID


class TestTask(TestTaskBase):
    id: int
    status: str  # 'idle', 'running', 'success', 'failed'
    is_favorite: bool
    cron_expression: Optional[str] = None
    environment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    items: Optional[List[TestTaskItem]] = None
    project: Optional[Project] = None

    class Config:
        from_attributes = True


class HeaderReplacement(BaseModel):
    """Header 替换配置"""
    key: str
    value: str


class AssertionReplacement(BaseModel):
    """断言替换配置"""
    type: str  # status_code, json_path, response_time, contains
    target: Optional[str] = None  # json_path 时需要
    operator: str  # eq, ne, gt, gte, lt, lte, contains, not_contains
    expected: Any


class TestTaskExecutionRequest(BaseModel):
    environment_id: int
    header_replacements: Optional[List[HeaderReplacement]] = None  # Header 替换列表
    assertion_replacements: Optional[List[AssertionReplacement]] = None  # 断言替换列表


class TestTaskExecutionResult(BaseModel):
    item_type: str  # 'api' or 'flow'
    item_id: int
    item_name: str
    success: bool
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    execution_time: Optional[int] = None  # 毫秒
    details: Optional[Dict[str, Any]] = None


class TestTaskExecutionSummary(BaseModel):
    """执行记录摘要（不包含详细结果，用于列表查询）"""
    id: int
    task_id: int
    environment_id: Optional[int] = None
    status: str  # 'running', 'success', 'failed'
    total_count: int
    success_count: int
    failed_count: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TestTaskExecution(BaseModel):
    """执行记录详情（包含完整结果）"""
    id: int
    task_id: int
    environment_id: Optional[int] = None
    status: str  # 'running', 'success', 'failed'
    total_count: int
    success_count: int
    failed_count: int
    execution_results: Optional[List[TestTaskExecutionResult]] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FlowVariableBase(BaseModel):
    key: str
    value: str


class FlowVariableCreate(FlowVariableBase):
    pass


class FlowVariableUpdate(FlowVariableBase):
    pass


class FlowVariable(FlowVariableBase):
    id: int
    flow_id: int
    # 注意：FlowVariable 模型中没有 created_at 和 updated_at 字段

    class Config:
        from_attributes = True


class FlowVariableBatchRequest(BaseModel):
    variables: List[FlowVariableBase]


class FlowExecuteRequest(BaseModel):
    environment_id: Optional[int] = None
    global_variables: Optional[Dict[str, Any]] = None
    failAction: Optional[str] = "stop"  # 执行失败时的行为：stop 或 continue
    delay: Optional[int] = 0  # 步骤间延迟（毫秒），0表示不延迟


# ===== Record API Request Schema =====
class RecordApiRequest(BaseModel):
    project_id: int
    environment_id: int
    start_url: str
    max_depth: int = 2
    login_url: Optional[str] = None  # 登录URL（可选）
    login_username: Optional[str] = None  # 登录用户名（可选）
    login_password: Optional[str] = None  # 登录密码（可选）
    login_data: Optional[Dict[str, Any]] = None  # 自定义登录数据（可选，JSON格式）


# ===== Flow Export Record Schemas =====
class FlowExportRecordBase(BaseModel):
    name: str
    export_data: Dict[str, Any]


class FlowExportRecordCreate(FlowExportRecordBase):
    flow_id: int


class FlowExportRecord(FlowExportRecordBase):
    id: int
    flow_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ===== Code Scan Schemas =====
class CodeScanBase(BaseModel):
    project_id: int
    project_name: str
    branch: str
    scan_path: str
    language: Optional[str] = None  # 编程语言
    sonar_project_key: Optional[str] = None  # Sonar的projectKey
    sonar_host: Optional[str] = None  # Sonar的服务host
    sonar_login: Optional[str] = None  # Sonar的login token

class CodeScanCreate(CodeScanBase):
    pass

class CodeScanUpdate(BaseModel):
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    branch: Optional[str] = None
    scan_path: Optional[str] = None
    language: Optional[str] = None
    sonar_project_key: Optional[str] = None
    sonar_host: Optional[str] = None
    sonar_login: Optional[str] = None

class CodeScan(CodeScanBase):
    id: int
    scan_time: Optional[datetime] = None
    result: Optional[str] = None
    error_message: Optional[str] = None  # 扫描不通过的原因或错误信息
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None
    
    class Config:
        from_attributes = True

class CodeScanResultBase(BaseModel):
    scan_id: int
    status: str = 'pending'
    error_message: Optional[str] = None

class CodeScanResultCreate(CodeScanResultBase):
    pass

class CodeScanResult(CodeScanResultBase):
    id: int
    created_at: datetime
    updated_at: datetime
    scan: Optional[CodeScan] = None
    
    class Config:
        from_attributes = True

# ===== Sprint Schemas =====
class SprintBase(BaseModel):
    project_id: int
    name: str
    goal: Optional[str] = None
    owner: Optional[str] = None
    start_date: date
    end_date: date

class SprintCreate(SprintBase):
    pass

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    owner: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class Sprint(SprintBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None
    
    class Config:
        from_attributes = True

# ===== TestCaseReview Schemas =====
class TestCaseReviewBase(BaseModel):
    project_id: int
    sprint_id: Optional[int] = None
    name: str
    initiator_id: int
    start_date: date
    end_date: date

class TestCaseReviewCreate(TestCaseReviewBase):
    pass

class TestCaseReviewUpdate(BaseModel):
    project_id: Optional[int] = None
    sprint_id: Optional[int] = None
    name: Optional[str] = None
    initiator_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class TestCaseReviewItemBase(BaseModel):
    review_id: int
    testcase_id: int
    reviewer_id: Optional[int] = None
    status: str = "pending"  # pending, approved, rejected
    comments: Optional[str] = None

class TestCaseReviewItemCreate(TestCaseReviewItemBase):
    pass

class TestCaseReviewItemUpdate(BaseModel):
    reviewer_id: Optional[int] = None
    status: Optional[str] = None
    comments: Optional[str] = None

class TestCaseReviewItem(TestCaseReviewItemBase):
    id: int
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    review: Optional['TestCaseReview'] = None
    testcase: Optional['TestCase'] = None
    reviewer: Optional[User] = None

    class Config:
        from_attributes = True

class TestCaseReview(TestCaseReviewBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    project: Optional[Project] = None
    sprint: Optional[Sprint] = None
    initiator: Optional[User] = None
    review_items: Optional[List[TestCaseReviewItem]] = None

    class Config:
        from_attributes = True


# ==================== 测试文件管理 ====================

class TestFileBase(BaseModel):
    """测试文件基础模型"""
    name: str
    description: Optional[str] = None
    file_type: str = 'local'  # flow 或 local

class TestFileCreate(TestFileBase):
    """创建测试文件"""
    file_name: Optional[str] = None
    file_content: Optional[Any] = None  # 流程导出时使用
    flow_id: Optional[int] = None

class TestFileUpdate(BaseModel):
    """更新测试文件"""
    name: Optional[str] = None
    description: Optional[str] = None

class TestFile(TestFileBase):
    """测试文件响应模型"""
    id: int
    file_name: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    flow_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    creator: Optional[User] = None

    class Config:
        from_attributes = True

class TestFileList(BaseModel):
    """测试文件列表响应"""
    items: List[TestFile]
    total: int
