"""测试数据生成器"""
import random
import string
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class TestDataGenerator:
    """根据接口定义生成测试数据"""
    
    @staticmethod
    def generate_value_by_type(param_type: str, param_name: str = "", 
                                enum_values: Optional[List] = None,
                                default_value: Any = None) -> Any:
        """根据类型生成值"""
        if default_value is not None:
            return default_value
        
        if enum_values:
            return enum_values[0]
        
        param_name_lower = param_name.lower()
        
        # 根据参数名推断值
        if 'email' in param_name_lower:
            return 'test@example.com'
        elif 'phone' in param_name_lower or 'mobile' in param_name_lower:
            return '13800138000'
        elif 'name' in param_name_lower and 'user' in param_name_lower:
            return 'testuser'
        elif 'password' in param_name_lower or 'pwd' in param_name_lower:
            return 'Test123456'
        elif 'url' in param_name_lower:
            return 'https://example.com'
        elif 'date' in param_name_lower:
            return datetime.now().strftime('%Y-%m-%d')
        elif 'time' in param_name_lower:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif 'age' in param_name_lower:
            return 25
        elif 'count' in param_name_lower or 'num' in param_name_lower:
            return 10
        elif 'price' in param_name_lower or 'amount' in param_name_lower:
            return 99.99
        elif 'status' in param_name_lower:
            return 1
        elif 'id' in param_name_lower:
            return 1
        elif 'page' in param_name_lower:
            return 1
        elif 'size' in param_name_lower or 'limit' in param_name_lower:
            return 10
        
        # 根据类型生成值
        if not param_type:
            return 'test_value'
        
        param_type_lower = param_type.lower()
        
        if param_type_lower in ['integer', 'int', 'int32', 'int64']:
            return random.randint(1, 100)
        elif param_type_lower in ['number', 'float', 'double']:
            return round(random.uniform(1, 100), 2)
        elif param_type_lower == 'boolean':
            return True
        elif param_type_lower == 'string':
            if 'date' in param_name_lower:
                return datetime.now().strftime('%Y-%m-%d')
            return 'test_string'
        elif param_type_lower == 'array':
            return []
        else:
            return 'test_value'
    
    @staticmethod
    def generate_from_schema(schema: Dict[str, Any]) -> Any:
        """根据schema生成值"""
        if not schema:
            return {}
        
        schema_type = schema.get('type')
        
        # 如果有 properties，说明是 object 类型（即使没有显式声明 type）
        if 'properties' in schema:
            result = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                # 只生成必填字段或当字段数量较少时生成所有字段
                if prop_name in required or len(properties) <= 10:
                    result[prop_name] = TestDataGenerator.generate_from_schema(prop_schema)
            
            return result if result else {}
        
        # 如果没有类型但有 $ref，说明 schema 没有被完全解析
        # 这种情况理论上不应该发生，但为了兼容性，返回一个警告对象
        if not schema_type and '$ref' in schema:
            ref = schema.get('$ref', '')
            print(f"⚠️ 警告: 遇到未解析的 $ref: {ref}，这可能导致测试数据不正确")
            # 返回空对象而不是猜测
            return {}
        
        if schema_type == 'object' or not schema_type:
            # 没有类型或object类型，都生成对象
            result = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                # 只生成必填字段或常见字段
                if prop_name in required or len(properties) <= 10:
                    result[prop_name] = TestDataGenerator.generate_from_schema(prop_schema)
            
            return result if result else {}
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            # 生成一个示例元素
            return [TestDataGenerator.generate_from_schema(items_schema)]
        
        else:
            # 基本类型
            return TestDataGenerator.generate_value_by_type(
                schema_type,
                schema.get('description', ''),
                schema.get('enum'),
                schema.get('default')
            )
    
    @staticmethod
    def generate_test_data(api: Any) -> Dict[str, Any]:
        """为API生成测试数据"""
        test_data = {
            'path_params': {},
            'query_params': {},
            'headers': {},
            'body': {},  # 初始化为空字典而不是 None
            'form_data': {}
        }
        
        # 解析参数
        if api.parameters:
            for param in api.parameters:
                if not param:
                    continue
                    
                param_name = param.get('name')
                param_in = param.get('in')
                param_type = param.get('type')
                param_schema = param.get('schema')
                enum_values = param.get('enum')
                default_value = param.get('default')
                
                if not param_name:
                    continue
                
                # 生成值
                if param_in == 'path':
                    value = TestDataGenerator.generate_value_by_type(
                        param_type, param_name, enum_values, default_value
                    )
                    test_data['path_params'][param_name] = value
                    
                elif param_in == 'query':
                    value = TestDataGenerator.generate_value_by_type(
                        param_type, param_name, enum_values, default_value
                    )
                    test_data['query_params'][param_name] = value
                    
                elif param_in == 'header':
                    value = TestDataGenerator.generate_value_by_type(
                        param_type, param_name, enum_values, default_value
                    )
                    test_data['headers'][param_name] = value
                
                elif param_in == 'formData':
                    # formData 参数放到 form_data 中
                    if param_type == 'file':
                        value = '<file upload>'
                    else:
                        value = TestDataGenerator.generate_value_by_type(
                            param_type, param_name, enum_values, default_value
                        )
                    test_data['form_data'][param_name] = value
                    
                elif param_in == 'body' and param_schema:
                    body_data = TestDataGenerator.generate_from_schema(param_schema)
                    # 确保body是字典类型（空字典也是有效的）
                    if isinstance(body_data, dict):
                        test_data['body'] = body_data  # 保留空字典 {}
                    else:
                        test_data['body'] = {}
        
        # 解析请求体
        if api.request_body:
            # 处理 formData 类型的请求体
            if api.request_body.get('type') == 'formData' and api.request_body.get('parameters'):
                for param in api.request_body['parameters']:
                    param_name = param.get('name')
                    param_type = param.get('type')
                    
                    # 如果是文件类型，给一个特殊标记
                    if param_type == 'file':
                        value = '<file upload>'
                    else:
                        value = TestDataGenerator.generate_value_by_type(
                            param_type, param_name, 
                            param.get('enum'), 
                            param.get('default')
                        )
                    test_data['form_data'][param_name] = value
            
            # 处理普通 JSON 请求体
            elif not test_data['body']:
                schema = api.request_body.get('schema')
                if schema:
                    body_data = TestDataGenerator.generate_from_schema(schema)
                    # 确保body是字典类型（空字典也是有效的）
                    if isinstance(body_data, dict):
                        test_data['body'] = body_data  # 保留空字典 {}
                    else:
                        test_data['body'] = {}
        
        # 保留空字典而不是转换为 None，这样前端可以正确显示 {}
        # 如果确实没有任何数据，保持为空字典 {}
        # 注意：空字典 {} 在 Python 中会被 if not 判断为 True，所以需要显式检查长度
        if len(test_data['path_params']) == 0:
            test_data['path_params'] = {}
        if len(test_data['query_params']) == 0:
            test_data['query_params'] = {}
        if len(test_data['headers']) == 0:
            test_data['headers'] = {}
        if len(test_data['form_data']) == 0:
            test_data['form_data'] = {}
        # body 保持为 None 或 Dict（空字典也是有效的）
        
        return test_data

