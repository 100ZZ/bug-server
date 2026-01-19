from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from database import engine, get_db
from swagger_parser import parse_swagger_file, OpenAPIParser
from executor import APIExecutor
from data_generator import TestDataGenerator
import os
import json
from datetime import datetime
from pathlib import Path

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="测试平台API", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 环境管理 ====================

@app.get("/api/environments", response_model=List[schemas.Environment])
def get_environments(db: Session = Depends(get_db)):
    """获取所有环境"""
    return db.query(models.Environment).all()

@app.get("/api/environments/{environment_id}", response_model=schemas.Environment)
def get_environment(environment_id: int, db: Session = Depends(get_db)):
    """获取单个环境"""
    environment = db.query(models.Environment).filter(models.Environment.id == environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    return environment

@app.post("/api/environments", response_model=schemas.Environment)
def create_environment(environment: schemas.EnvironmentCreate, db: Session = Depends(get_db)):
    """创建环境"""
    db_environment = models.Environment(**environment.dict())
    db.add(db_environment)
    db.commit()
    db.refresh(db_environment)
    return db_environment

@app.put("/api/environments/{environment_id}", response_model=schemas.Environment)
def update_environment(environment_id: int, environment: schemas.EnvironmentUpdate, db: Session = Depends(get_db)):
    """更新环境"""
    db_environment = db.query(models.Environment).filter(models.Environment.id == environment_id).first()
    if not db_environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    for key, value in environment.dict(exclude_unset=True).items():
        setattr(db_environment, key, value)
    
    db.commit()
    db.refresh(db_environment)
    return db_environment

@app.delete("/api/environments/{environment_id}")
def delete_environment(environment_id: int, db: Session = Depends(get_db)):
    """删除环境"""
    db_environment = db.query(models.Environment).filter(models.Environment.id == environment_id).first()
    if not db_environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    db.delete(db_environment)
    db.commit()
    return {"message": "删除成功"}

# ==================== Swagger解析 ====================

@app.post("/api/swagger/upload")
async def upload_swagger(
    file: UploadFile = File(...), 
    auto_generate_data: bool = True,
    base_url: str = "http://192.168.60.219:48080",
    db: Session = Depends(get_db)
):
    """上传并解析Swagger文件"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="只支持JSON格式的Swagger文件")
    
    # 先登录获取真实 token
    import requests
    access_token = None
    try:
        login_url = f"{base_url}/admin-api/system/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123",
            "captchaVerification": ""
        }
        login_response = requests.post(login_url, json=login_data, headers={"tenant-id": "1"}, timeout=10)
        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get('code') == 0 and login_result.get('data'):
                access_token = login_result['data'].get('accessToken')
    except Exception:
        pass
    
    if not access_token:
        access_token = "test1"
    
    # 读取文件内容
    content = await file.read()
    
    # 解析Swagger
    try:
        apis = parse_swagger_file(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 保存到数据库并生成测试数据
    created_apis = []
    generated_test_data_count = 0
    
    for api_data in apis:
        db_api = models.API(**api_data)
        db.add(db_api)
        db.flush()  # 获取API的ID
        created_apis.append(api_data)
        
        # 自动生成测试数据 - 为所有接口生成
        if auto_generate_data:
            test_data = TestDataGenerator.generate_test_data(db_api)
            
            # 使用统一的默认数据名称
            test_data_name = "测试数据#默认"
            
            # 使用真实的 token 替换默认值
            headers = test_data.get('headers') or {}
            if isinstance(headers, dict):
                headers['Authorization'] = f"Bearer {access_token}"
                headers['tenant-id'] = '1'
            
            # 为每个接口都创建测试数据，即使没有参数
            db_test_data = models.TestData(
                api_id=db_api.id,
                name=test_data_name,
                path_params=test_data.get('path_params'),
                query_params=test_data.get('query_params'),
                headers=headers,
                form_data=test_data.get('form_data'),
                body=test_data.get('body'),
                expected_status=200
            )
            db.add(db_test_data)
            generated_test_data_count += 1
    
    db.commit()
    
    return {
        "message": f"成功解析并保存 {len(created_apis)} 个接口，自动生成 {generated_test_data_count} 条测试数据",
        "count": len(created_apis),
        "test_data_count": generated_test_data_count,
        "filename": file.filename
    }

# ==================== 接口管理 ====================

@app.get("/api/apis", response_model=List[schemas.API])
def get_apis(
    skip: int = 0,
    limit: int = 100,
    method: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取接口列表"""
    query = db.query(models.API)
    
    if method:
        query = query.filter(models.API.method == method.upper())
    
    if tag:
        query = query.filter(models.API.tags.contains([tag]))
    
    return query.offset(skip).limit(limit).all()

@app.get("/api/apis/{api_id}", response_model=schemas.API)
def get_api(api_id: int, db: Session = Depends(get_db)):
    """获取单个接口"""
    api = db.query(models.API).filter(models.API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="接口不存在")
    return api

@app.delete("/api/apis/{api_id}")
def delete_api(api_id: int, db: Session = Depends(get_db)):
    """删除接口"""
    api = db.query(models.API).filter(models.API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    db.delete(api)
    db.commit()
    return {"message": "删除成功"}

@app.delete("/api/apis")
def delete_all_apis(db: Session = Depends(get_db)):
    """删除所有接口"""
    db.query(models.API).delete()
    db.commit()
    return {"message": "已删除所有接口"}

@app.post("/api/swagger/sync")
def sync_swagger_from_url(
    swagger_url: str = "http://192.168.60.219:48080/v3/api-docs",
    auto_generate_data: bool = True,
    db: Session = Depends(get_db)
):
    """从远程URL同步Swagger文档"""
    try:
        import requests
        
        # 1. 先登录获取真实 token
        access_token = None
        try:
            login_url = swagger_url.replace('/v3/api-docs', '/admin-api/system/auth/login')
            login_data = {
                "username": "admin",
                "password": "admin123",
                "captchaVerification": ""
            }
            login_response = requests.post(login_url, json=login_data, headers={"tenant-id": "1"}, timeout=10)
            if login_response.status_code == 200:
                login_result = login_response.json()
                if login_result.get('code') == 0 and login_result.get('data'):
                    access_token = login_result['data'].get('accessToken')
                    print(f"✅ 登录成功，获取到 token: {access_token[:30]}...")
        except Exception as login_error:
            print(f"⚠️ 登录失败，将使用默认 token: {login_error}")
        
        # 如果没有获取到token，使用默认值
        if not access_token:
            access_token = "test1"
        
        # 2. 下载远程Swagger文档
        response = requests.get(swagger_url, timeout=30)
        response.raise_for_status()
        spec = response.json()
        
        # 3. 删除所有旧接口（级联删除测试数据）
        deleted_count = db.query(models.API).count()
        db.query(models.API).delete()
        db.commit()
        
        # 4. 解析新接口
        parser = OpenAPIParser(spec)
        apis = parser.parse()
        
        # 5. 保存新接口到数据库
        saved_count = 0
        for api_data in apis:
            api = models.API(**api_data, swagger_file="sync_from_url")
            db.add(api)
            saved_count += 1
        
        db.commit()
        
        # 6. 自动生成测试数据 - 为所有接口生成，使用真实token
        test_data_count = 0
        if auto_generate_data:
            for api in db.query(models.API).all():
                test_data = TestDataGenerator.generate_test_data(api)
                
                # 使用统一的默认数据名称
                test_data_name = "测试数据#默认"
                
                # 使用真实的 token 替换默认值
                headers = test_data.get('headers') or {}
                if isinstance(headers, dict):
                    headers['Authorization'] = f"Bearer {access_token}"
                    headers['tenant-id'] = '1'  # 修正为字符串 "1"
                
                # 为所有接口生成测试数据，不论是什么方法
                test_data_obj = models.TestData(
                    api_id=api.id,
                    name=test_data_name,
                    path_params=test_data.get('path_params'),
                    query_params=test_data.get('query_params'),
                    headers=headers,
                    form_data=test_data.get('form_data'),
                    body=test_data.get('body'),
                    expected_status=200
                )
                db.add(test_data_obj)
                test_data_count += 1
            
            db.commit()
        
        return {
            "message": f"同步成功：删除 {deleted_count} 个旧接口，导入 {saved_count} 个新接口，生成 {test_data_count} 条测试数据",
            "deleted_count": deleted_count,
            "imported_count": saved_count,
            "test_data_count": test_data_count,
            "source_url": swagger_url
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"无法访问远程文档: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")

# ==================== 测试数据管理 ====================

@app.get("/api/test-data", response_model=List[schemas.TestData])
def get_test_data_list(api_id: Optional[int] = None, db: Session = Depends(get_db)):
    """获取测试数据列表"""
    query = db.query(models.TestData)
    if api_id:
        query = query.filter(models.TestData.api_id == api_id)
    return query.all()

@app.get("/api/test-data/{test_data_id}", response_model=schemas.TestData)
def get_test_data(test_data_id: int, db: Session = Depends(get_db)):
    """获取单个测试数据"""
    test_data = db.query(models.TestData).filter(models.TestData.id == test_data_id).first()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    return test_data

@app.post("/api/test-data", response_model=schemas.TestData)
def create_test_data(test_data: schemas.TestDataCreate, db: Session = Depends(get_db)):
    """创建测试数据"""
    db_test_data = models.TestData(**test_data.dict())
    db.add(db_test_data)
    db.commit()
    db.refresh(db_test_data)
    return db_test_data

@app.put("/api/test-data/{test_data_id}", response_model=schemas.TestData)
def update_test_data(test_data_id: int, test_data: schemas.TestDataUpdate, db: Session = Depends(get_db)):
    """更新测试数据"""
    db_test_data = db.query(models.TestData).filter(models.TestData.id == test_data_id).first()
    if not db_test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    for key, value in test_data.dict(exclude_unset=True).items():
        setattr(db_test_data, key, value)
    
    db.commit()
    db.refresh(db_test_data)
    return db_test_data

@app.delete("/api/test-data/{test_data_id}")
def delete_test_data(test_data_id: int, db: Session = Depends(get_db)):
    """删除测试数据"""
    test_data = db.query(models.TestData).filter(models.TestData.id == test_data_id).first()
    if not test_data:
        raise HTTPException(status_code=404, detail="测试数据不存在")
    
    db.delete(test_data)
    db.commit()
    return {"message": "删除成功"}

@app.post("/api/test-data/generate/{api_id}", response_model=schemas.TestData)
def generate_test_data(api_id: int, db: Session = Depends(get_db)):
    """为指定接口生成测试数据"""
    # 获取接口
    api = db.query(models.API).filter(models.API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    # 生成测试数据
    test_data = TestDataGenerator.generate_test_data(api)
    
    # 查找已有的测试数据总数（包括默认数据）
    existing_count = db.query(models.TestData).filter(
        models.TestData.api_id == api_id
    ).count()
    
    # 如果已经有3个测试数据，不允许再生成
    if existing_count >= 3:
        raise HTTPException(status_code=400, detail="最多只能生成3个测试数据（1个默认 + 2个生成）")
    
    # 保存到数据库
    db_test_data = models.TestData(
        api_id=api_id,
        name=f"测试数据#{existing_count}",
        path_params=test_data.get('path_params'),
        query_params=test_data.get('query_params'),
        headers=test_data.get('headers'),
        form_data=test_data.get('form_data'),
        body=test_data.get('body')
    )
    db.add(db_test_data)
    db.commit()
    db.refresh(db_test_data)
    
    return db_test_data

# ==================== 接口执行 ====================

@app.post("/api/execute/{api_id}", response_model=schemas.ExecutionRecord)
def execute_api(api_id: int, request: schemas.ExecuteRequest, db: Session = Depends(get_db)):
    """执行单个接口"""
    # 获取接口
    api = db.query(models.API).filter(models.API.id == api_id).first()
    if not api:
        raise HTTPException(status_code=404, detail="接口不存在")
    
    # 获取环境
    environment = db.query(models.Environment).filter(models.Environment.id == request.environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    # 获取测试数据（如果提供）
    test_data = None
    if request.test_data_id:
        test_data = db.query(models.TestData).filter(models.TestData.id == request.test_data_id).first()
    else:
        # 如果没有指定 test_data_id，尝试查找该接口的默认测试数据
        # 通常第一个测试数据可以作为默认数据
        default_test_data = db.query(models.TestData).filter(
            models.TestData.api_id == api_id
        ).first()
        if default_test_data:
            test_data = default_test_data
            print(f"  📋 未指定 test_data_id，使用默认测试数据: {test_data.name} (ID: {test_data.id})")
    
    # 执行接口
    executor = APIExecutor(api, environment, db)
    
    print(f"  🔍 执行接口: {api.method} {api.path}")
    print(f"  📋 test_data: {test_data.name if test_data else 'None'}")
    print(f"  📋 request.headers: {request.headers}")
    print(f"  📋 test_data.headers: {test_data.headers if test_data else 'None'}")
    
    # 如果有测试数据，使用 execute_with_test_data（支持前置接口和变量引用）
    # 注意：即使没有配置前置接口，如果有 test_data_id，也应该使用测试数据（可能包含变量引用）
    if test_data:
        # 合并请求参数到测试数据（请求参数优先，但如果请求参数为 None 则使用测试数据）
        if request.path_params is not None:
            test_data.path_params = request.path_params
        if request.query_params is not None:
            test_data.query_params = request.query_params
        if request.headers is not None:
            # 如果 request.headers 不为 None，合并到 test_data.headers
            if test_data.headers:
                # 合并：test_data.headers 作为基础，request.headers 覆盖
                merged_headers = test_data.headers.copy() if isinstance(test_data.headers, dict) else {}
                if isinstance(request.headers, dict):
                    merged_headers.update(request.headers)
                test_data.headers = merged_headers
            else:
                test_data.headers = request.headers
        # 如果 request.headers 为 None，保持使用 test_data.headers
        if request.body is not None:
            test_data.body = request.body
        
        result = executor.execute_with_test_data(test_data)
    else:
        # 普通执行（没有测试数据）
        result = executor.execute(
            path_params=request.path_params,
            query_params=request.query_params,
            headers=request.headers,
            body=request.body
        )
    
    # 保存执行记录
    record = models.ExecutionRecord(
        api_id=api_id,
        test_data_id=request.test_data_id,
        environment_id=request.environment_id,
        **result
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record

@app.post("/api/execute/batch")
def batch_execute(request: schemas.BatchExecuteRequest, db: Session = Depends(get_db)):
    """批量执行接口"""
    # 获取环境
    environment = db.query(models.Environment).filter(models.Environment.id == request.environment_id).first()
    if not environment:
        raise HTTPException(status_code=404, detail="环境不存在")
    
    # 获取要执行的接口
    query = db.query(models.API)
    if request.api_ids:
        query = query.filter(models.API.id.in_(request.api_ids))
    apis = query.all()
    
    if not apis:
        raise HTTPException(status_code=404, detail="没有找到要执行的接口")
    
    # 批量执行
    results = []
    for api in apis:
        executor = APIExecutor(api, environment, db)
        
        # 查找该接口的测试数据
        test_data_list = db.query(models.TestData).filter(models.TestData.api_id == api.id).all()
        
        if test_data_list:
            # 如果有测试数据，使用测试数据执行
            for test_data in test_data_list:
                result = executor.execute_with_test_data(test_data)
                record = models.ExecutionRecord(
                    api_id=api.id,
                    test_data_id=test_data.id,
                    environment_id=request.environment_id,
                    **result
                )
                db.add(record)
                results.append({
                    "api_id": api.id,
                    "api_path": api.path,
                    "api_method": api.method,
                    "test_data_name": test_data.name,
                    "success": result['success'],
                    "response_status": result['response_status'],
                    "response_time": result['response_time'],
                    "error_message": result['error_message']
                })
        else:
            # 没有测试数据，直接执行
            result = executor.execute()
            record = models.ExecutionRecord(
                api_id=api.id,
                test_data_id=None,
                environment_id=request.environment_id,
                **result
            )
            db.add(record)
            results.append({
                "api_id": api.id,
                "api_path": api.path,
                "api_method": api.method,
                "test_data_name": None,
                "success": result['success'],
                "response_status": result['response_status'],
                "response_time": result['response_time'],
                "error_message": result['error_message']
            })
    
    db.commit()
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    return {
        "message": f"批量执行完成，共 {len(results)} 个测试",
        "total": len(results),
        "success": success_count,
        "failed": failed_count,
        "results": results
    }

# ==================== 执行记录 ====================

@app.get("/api/execution-records", response_model=List[schemas.ExecutionRecord])
def get_execution_records(
    api_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取执行记录"""
    query = db.query(models.ExecutionRecord).order_by(models.ExecutionRecord.executed_at.desc())
    
    if api_id:
        query = query.filter(models.ExecutionRecord.api_id == api_id)
    
    return query.offset(skip).limit(limit).all()

@app.get("/api/execution-records/{record_id}", response_model=schemas.ExecutionRecord)
def get_execution_record(record_id: int, db: Session = Depends(get_db)):
    """获取单个执行记录"""
    record = db.query(models.ExecutionRecord).filter(models.ExecutionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="执行记录不存在")
    return record

# ==================== 串联方案管理 ====================

@app.get("/api/chain-plans", response_model=List[schemas.ChainPlan])
def get_chain_plans(db: Session = Depends(get_db)):
    """获取所有串联方案"""
    return db.query(models.ChainPlan).order_by(models.ChainPlan.updated_at.desc()).all()

@app.post("/api/chain-plans/{plan_id}/export")
def export_chain_plan(plan_id: int, db: Session = Depends(get_db)):
    """导出串联方案到数据库"""
    plan = db.query(models.ChainPlan).filter(models.ChainPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="串联方案不存在")
    
    # 构建导出数据
    export_data = {
        "version": "1.0",
        "exportTime": datetime.now().isoformat(),
        "plan": {
            "name": plan.name,
            "description": plan.description,
            "api_ids": plan.api_ids,
            "api_params": plan.api_params or {},
            "api_assertions": plan.api_assertions or {},
            "global_variables": plan.global_variables or {},
            "stop_on_error": plan.stop_on_error,
            "delay_ms": plan.delay_ms,
            "environment_id": plan.environment_id
        }
    }
    
    # 生成导出名称（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in plan.name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_name:
        safe_name = f"plan_{plan_id}"
    export_name = f"{safe_name}_{timestamp}"
    
    # 保存到数据库
    export_record = models.ExportRecord(
        plan_id=plan_id,
        name=export_name,
        export_data=export_data
    )
    db.add(export_record)
    db.commit()
    db.refresh(export_record)
    
    return {
        "message": "流程导出成功",
        "export_id": export_record.id,
        "name": export_name,
        "created_at": export_record.created_at.isoformat()
    }

@app.get("/api/chain-plans/{plan_id}", response_model=schemas.ChainPlan)
def get_chain_plan(plan_id: int, db: Session = Depends(get_db)):
    """获取单个串联方案"""
    plan = db.query(models.ChainPlan).filter(models.ChainPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="串联方案不存在")
    return plan

@app.post("/api/chain-plans", response_model=schemas.ChainPlan)
def create_chain_plan(plan: schemas.ChainPlanCreate, db: Session = Depends(get_db)):
    """创建串联方案"""
    db_plan = models.ChainPlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@app.put("/api/chain-plans/{plan_id}", response_model=schemas.ChainPlan)
def update_chain_plan(plan_id: int, plan: schemas.ChainPlanUpdate, db: Session = Depends(get_db)):
    """更新串联方案"""
    db_plan = db.query(models.ChainPlan).filter(models.ChainPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="串联方案不存在")
    
    # 获取明确设置的字段
    update_data = plan.dict(exclude_unset=True)
    
    # 获取所有字段（包括未设置的）用于检查
    plan_dict_all = plan.dict(exclude_unset=False)
    
    # 特别处理 api_params：确保即使为空对象 {} 也能被保存
    if 'api_params' in plan_dict_all:
        update_data['api_params'] = plan.api_params
    
    # 特别处理 api_assertions：确保即使为空对象 {} 也能被保存
    if 'api_assertions' in plan_dict_all:
        update_data['api_assertions'] = plan.api_assertions
    
    # 特别处理 global_variables：确保即使为空对象 {} 也能被保存
    if hasattr(plan, 'global_variables') and 'global_variables' in plan_dict_all:
        update_data['global_variables'] = plan.global_variables
    
    for key, value in update_data.items():
        setattr(db_plan, key, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

@app.delete("/api/chain-plans/{plan_id}")
def delete_chain_plan(plan_id: int, db: Session = Depends(get_db)):
    """删除串联方案"""
    db_plan = db.query(models.ChainPlan).filter(models.ChainPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="串联方案不存在")
    
    db.delete(db_plan)
    db.commit()
    return {"message": "串联方案已删除"}

# ==================== 健康检查 ====================

@app.get("/")
def root():
    return {"message": "测试平台API服务运行中"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)

