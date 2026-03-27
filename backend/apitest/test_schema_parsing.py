"""测试 Schema 解析的脚本"""
import requests
import json
from swagger_parser import OpenAPIParser
from data_generator import TestDataGenerator

def test_auth_login_schema():
    """测试 AuthLoginReqVO schema 的解析"""
    
    # 1. 下载 Swagger 文档
    swagger_url = "http://192.168.100.186:48080/v3/api-docs"
    print(f"📥 正在下载 Swagger 文档: {swagger_url}")
    
    try:
        response = requests.get(swagger_url, timeout=30)
        response.raise_for_status()
        spec = response.json()
        print("✅ Swagger 文档下载成功\n")
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return
    
    # 2. 检查 schemas 中是否有 AuthLoginReqVO
    parser = OpenAPIParser(spec)
    print(f"📋 文档中的 schemas 数量: {len(parser.schemas)}")
    
    if 'AuthLoginReqVO' in parser.schemas:
        print("✅ 找到 AuthLoginReqVO 定义")
        auth_login_schema = parser.schemas['AuthLoginReqVO']
        print(f"\n原始 AuthLoginReqVO schema:")
        print(json.dumps(auth_login_schema, indent=2, ensure_ascii=False))
    else:
        print("❌ 未找到 AuthLoginReqVO 定义")
        print(f"\n可用的 schemas (前20个):")
        for i, name in enumerate(list(parser.schemas.keys())[:20]):
            print(f"  {i+1}. {name}")
        return
    
    # 3. 解析所有接口
    print("\n" + "="*60)
    print("📝 解析接口...")
    apis = parser.parse()
    
    # 4. 查找 login 接口
    login_api = None
    for api in apis:
        if '/admin-api/system/auth/login' in api['path']:
            login_api = api
            break
    
    if not login_api:
        print("❌ 未找到 /admin-api/system/auth/login 接口")
        return
    
    print(f"✅ 找到 login 接口: {login_api['method']} {login_api['path']}")
    
    # 5. 检查 request_body
    request_body = login_api.get('request_body', {})
    print(f"\n📦 request_body 结构:")
    print(json.dumps(request_body, indent=2, ensure_ascii=False))
    
    # 6. 检查 schema 是否被正确解析
    schema = request_body.get('schema', {})
    print(f"\n🔍 request_body 中的 schema:")
    print(json.dumps(schema, indent=2, ensure_ascii=False))
    
    if '$ref' in schema:
        print("\n⚠️ 警告: schema 中仍然包含 $ref，说明没有被完全解析！")
    elif 'properties' in schema:
        print(f"\n✅ schema 包含 properties，字段列表:")
        for prop_name in schema['properties'].keys():
            print(f"  - {prop_name}")
    else:
        print("\n⚠️ 警告: schema 既没有 $ref 也没有 properties！")
    
    # 7. 测试数据生成
    print("\n" + "="*60)
    print("🔧 测试数据生成...")
    
    # 创建一个模拟的 API 对象
    class MockAPI:
        def __init__(self, api_data):
            self.parameters = api_data.get('parameters')
            self.request_body = api_data.get('request_body')
    
    mock_api = MockAPI(login_api)
    test_data = TestDataGenerator.generate_test_data(mock_api)
    
    print(f"\n生成的测试数据 body:")
    print(json.dumps(test_data.get('body'), indent=2, ensure_ascii=False))
    
    # 8. 对比期望的字段
    if 'properties' in schema:
        expected_fields = set(schema['properties'].keys())
        actual_fields = set(test_data.get('body', {}).keys())
        
        print(f"\n📊 字段对比:")
        print(f"  期望字段: {expected_fields}")
        print(f"  实际字段: {actual_fields}")
        
        missing = expected_fields - actual_fields
        extra = actual_fields - expected_fields
        
        if missing:
            print(f"  ⚠️ 缺少字段: {missing}")
        if extra:
            print(f"  ⚠️ 多余字段: {extra}")
        if not missing and not extra:
            print(f"  ✅ 字段完全匹配！")

if __name__ == '__main__':
    test_auth_login_schema()
