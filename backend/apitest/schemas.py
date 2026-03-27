from pydantic import BaseModel
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime

# Assertion schemas
class Assertion(BaseModel):
    """单个断言配置"""
    type: Literal['status_code', 'response_body', 'response_header', 'response_time']  # 断言类型
    operator: Literal['eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'contains', 'not_contains', 'exists', 'not_exists', 'is_empty', 'is_not_empty', 'regex']  # 操作符
    target: Optional[str] = None  # 目标字段，如 $.data.id 或 header名称
    expected: Optional[Any] = None  # 期望值

class AssertionResult(BaseModel):
    """断言执行结果"""
    assertion: Assertion
    passed: bool  # 是否通过
    actual_value: Optional[Any] = None  # 实际值
    message: str  # 结果消息

# Environment schemas
class EnvironmentBase(BaseModel):
    name: str
    base_url: str
    description: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(EnvironmentBase):
    name: Optional[str] = None
    base_url: Optional[str] = None

class Environment(EnvironmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# API schemas
class APIBase(BaseModel):
    path: str
    method: str
    summary: Optional[str] = None
    operation_id: Optional[str] = None
    tags: Optional[List[str]] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None

class APICreate(APIBase):
    swagger_file: Optional[str] = None

class API(APIBase):
    id: int
    swagger_file: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# TestData schemas
class TestDataBase(BaseModel):
    api_id: int
    name: str
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: Optional[int] = None
    expected_response: Optional[Dict[str, Any]] = None
    assertions: Optional[List[Dict[str, Any]]] = None  # 断言配置列表
    # 前置接口配置
    pre_request_api_id: Optional[int] = None  # 前置接口 API ID
    pre_request_test_data_id: Optional[int] = None  # 前置接口测试数据 ID
    variable_extractions: Optional[Dict[str, str]] = None  # 变量提取规则，格式: {"varName": "$.data.accessToken"}

class TestDataCreate(TestDataBase):
    pass

class TestDataUpdate(BaseModel):
    name: Optional[str] = None
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    expected_status: Optional[int] = None
    expected_response: Optional[Dict[str, Any]] = None
    assertions: Optional[List[Dict[str, Any]]] = None  # 断言配置列表
    # 前置接口配置
    pre_request_api_id: Optional[int] = None
    pre_request_test_data_id: Optional[int] = None
    variable_extractions: Optional[Dict[str, str]] = None

class TestData(TestDataBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ExecutionRecord schemas
class ExecutionRecordBase(BaseModel):
    api_id: int
    test_data_id: Optional[int] = None
    environment_id: int
    request_url: Optional[str] = None
    request_method: Optional[str] = None
    request_headers: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, Any]] = None
    response_body: Optional[Any] = None
    response_time: Optional[int] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    assertion_results: Optional[List[Dict[str, Any]]] = None  # 断言执行结果列表

class ExecutionRecord(ExecutionRecordBase):
    id: int
    executed_at: datetime
    
    class Config:
        from_attributes = True

# Execution request schemas
class ExecuteRequest(BaseModel):
    environment_id: int
    test_data_id: Optional[int] = None
    path_params: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    assertions: Optional[List[Dict[str, Any]]] = None  # 实时断言配置

class BatchExecuteRequest(BaseModel):
    environment_id: int
    api_ids: Optional[List[int]] = None  # 如果为空，则执行所有接口

# ChainPlan schemas
class ChainPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    api_ids: List[int]
    api_params: Optional[Dict[str, Any]] = None  # 每个接口的参数配置
    api_assertions: Optional[Dict[str, Any]] = None  # 每个接口的断言配置
    global_variables: Optional[Dict[str, Any]] = None  # 全局变量配置
    environment_id: Optional[int] = None
    stop_on_error: bool = True
    delay_ms: int = 500

class ChainPlanCreate(ChainPlanBase):
    pass

class ChainPlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_ids: Optional[List[int]] = None
    api_params: Optional[Dict[str, Any]] = None
    api_assertions: Optional[Dict[str, Any]] = None
    global_variables: Optional[Dict[str, Any]] = None
    environment_id: Optional[int] = None
    stop_on_error: Optional[bool] = None
    delay_ms: Optional[int] = None

class ChainPlan(ChainPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ExportRecord schemas
class ExportRecordBase(BaseModel):
    plan_id: int
    name: str
    export_data: Dict[str, Any]

class ExportRecordCreate(ExportRecordBase):
    pass

class ExportRecord(ExportRecordBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

