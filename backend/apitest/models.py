from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Environment(Base):
    __tablename__ = "environments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    base_url = Column(String(255), nullable=False)
    description = Column(Text)
    headers = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class API(Base):
    __tablename__ = "apis"
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    summary = Column(String(255))
    operation_id = Column(String(100))
    tags = Column(JSON)
    parameters = Column(JSON)
    request_body = Column(JSON)
    responses = Column(JSON)
    swagger_file = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class TestData(Base):
    __tablename__ = "test_data"
    
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    path_params = Column(JSON)
    query_params = Column(JSON)
    headers = Column(JSON)
    form_data = Column(JSON)
    body = Column(JSON)
    expected_status = Column(Integer)
    expected_response = Column(JSON)
    assertions = Column(JSON)  # 断言配置列表
    # 前置接口配置
    pre_request_api_id = Column(Integer, ForeignKey("apis.id", ondelete="SET NULL"))  # 前置接口 API ID
    pre_request_test_data_id = Column(Integer, ForeignKey("test_data.id", ondelete="SET NULL"))  # 前置接口测试数据 ID
    variable_extractions = Column(JSON)  # 变量提取规则，格式: {"varName": "$.data.accessToken"}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ExecutionRecord(Base):
    __tablename__ = "execution_records"
    
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, ForeignKey("apis.id", ondelete="CASCADE"), nullable=False)
    test_data_id = Column(Integer, ForeignKey("test_data.id", ondelete="SET NULL"))
    environment_id = Column(Integer, ForeignKey("environments.id", ondelete="CASCADE"), nullable=False)
    request_url = Column(Text)
    request_method = Column(String(10))
    request_headers = Column(JSON)
    request_body = Column(JSON)
    response_status = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(JSON)
    response_time = Column(Integer)
    success = Column(Boolean)
    error_message = Column(Text)
    assertion_results = Column(JSON)  # 断言执行结果列表
    executed_at = Column(DateTime(timezone=True), server_default=func.now())

class ChainPlan(Base):
    __tablename__ = "chain_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    api_ids = Column(JSON, nullable=False)  # 存储 API ID 的顺序列表
    api_params = Column(JSON)  # 存储每个接口的参数配置 {api_index: {query, body, headers}}
    api_assertions = Column(JSON)  # 存储每个接口的断言配置 {api_index: [{type, operator, target, expected}]}
    global_variables = Column(JSON)  # 全局变量配置 {key: value}
    replace_key = Column(String(200))  # 替换变量键名
    replace_value = Column(Text)  # 替换变量值
    environment_id = Column(Integer, ForeignKey("environments.id", ondelete="SET NULL"))
    stop_on_error = Column(Boolean, default=True)
    delay_ms = Column(Integer, default=500)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ExportRecord(Base):
    """导出记录表"""
    __tablename__ = "export_records"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("chain_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # 导出名称
    export_data = Column(JSON, nullable=False)  # 导出的完整数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

