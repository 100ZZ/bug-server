import json
from typing import Dict, List, Any

class OpenAPIParser:
    """OpenAPI 3.x / Swagger v2 通用解析器"""
    
    def __init__(self, spec_json: Dict[str, Any]):
        self.spec = spec_json
        self.is_openapi_v3 = 'openapi' in spec_json  # OpenAPI 3.x
        self.is_swagger_v2 = 'swagger' in spec_json  # Swagger 2.0
        
        if not self.is_openapi_v3 and not self.is_swagger_v2:
            raise ValueError("不支持的文档格式，仅支持 OpenAPI 3.x 或 Swagger 2.0")
        
        # 提取 components/schemas 或 definitions
        if self.is_openapi_v3:
            self.schemas = self.spec.get('components', {}).get('schemas', {})
        else:
            self.schemas = self.spec.get('definitions', {})
    
    def parse(self) -> List[Dict[str, Any]]:
        """解析文档，返回接口列表"""
        apis = []
        paths = self.spec.get('paths', {})
        
        # 提取全局的 security headers
        global_headers = self._extract_global_security_headers()
        
        for path, methods in paths.items():
            # 过滤无效路径：跳过包含 ** 的路径（Spring Boot 的通配符路由）
            if '**' in path:
                continue
            
            for method, details in methods.items():
                # 跳过非HTTP方法的字段（如 parameters, $ref 等）
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    continue
                
                # 过滤无效接口：跳过 404 错误处理等默认路由
                operation_id = details.get('operationId', '')
                tags = details.get('tags', [])
                if (operation_id.startswith('Default_') or 
                    'default-controller' in tags or
                    'default' in operation_id.lower()):
                    continue
                
                # 构建完整路径
                full_path = self._build_full_path(path)
                
                # 解析参数
                if self.is_openapi_v3:
                    parameters = self._parse_openapi3_parameters(details, methods)
                    request_body = self._parse_openapi3_request_body(details)
                else:
                    parameters = self._parse_swagger2_parameters(details.get('parameters', []))
                    request_body = self._parse_swagger2_request_body(details)
                
                # 智能识别文件上传参数：将 query 中的文件参数移到 formData
                parameters, request_body = self._extract_file_params_from_query(parameters, request_body)
                
                # 合并全局 headers 到参数中
                parameters.extend(global_headers)
                    
                api = {
                    'path': full_path,
                    'method': method.upper(),
                    'name': details.get('summary', '') or details.get('operationId', ''),  # 接口名称
                    'summary': details.get('summary', ''),
                    'operation_id': details.get('operationId', ''),
                    'description': details.get('description', ''),  # 接口详细描述
                    'tags': details.get('tags', []),
                    'parameters': parameters,
                    'request_body': request_body,
                    'responses': details.get('responses', {}),
                }
                apis.append(api)
        
        return apis
    
    def _extract_global_security_headers(self) -> List[Dict[str, Any]]:
        """提取全局的 security 定义中的 header 参数"""
        headers = []
        
        if self.is_openapi_v3:
            # OpenAPI 3.x
            components = self.spec.get('components', {})
            security_schemes = components.get('securitySchemes', {})
            
            for name, scheme in security_schemes.items():
                if scheme.get('type') == 'apiKey' and scheme.get('in') == 'header':
                    headers.append({
                        'name': scheme.get('name'),
                        'in': 'header',
                        'description': scheme.get('description', f'认证 Token'),
                        'required': False,  # 通常security不是必须的（可能有公开接口）
                        'type': 'string',
                        'schema': {'type': 'string'},
                        'default': 'Bearer test1' if 'Authorization' in scheme.get('name', '') else '1',
                        'enum': None,
                        'example': None,
                    })
        else:
            # Swagger 2.0
            security_definitions = self.spec.get('securityDefinitions', {})
            for name, scheme in security_definitions.items():
                if scheme.get('type') == 'apiKey' and scheme.get('in') == 'header':
                    headers.append({
                        'name': scheme.get('name'),
                        'in': 'header',
                        'description': scheme.get('description', f'认证 Token'),
                        'required': False,
                        'type': 'string',
                        'schema': {'type': 'string'},
                        'default': 'Bearer test1' if 'Authorization' in scheme.get('name', '') else '1',
                        'enum': None,
                        'example': None,
                    })
        
        # 添加 tenant-id header（open-saas 项目必需）
        headers.append({
            'name': 'tenant-id',
            'in': 'header',
            'description': '租户编号',
            'required': False,
            'type': 'string',
            'schema': {'type': 'string'},
            'default': 'open-saas',
            'enum': None,
            'example': None,
        })
        
        return headers
    
    def _build_full_path(self, path: str) -> str:
        """构建完整路径"""
        if self.is_swagger_v2:
            base_path = self.spec.get('basePath', '')
            if not base_path:
                return path
            base = base_path.rstrip('/')
            path = path.lstrip('/')
            return f"{base}/{path}" if path else base
        else:
            # OpenAPI 3.x 路径通常已经是完整的
            return path
    
    def _resolve_ref(self, schema: Dict[str, Any], visited: set = None) -> Dict[str, Any]:
        """解析 $ref 引用，返回完整的 schema"""
        if visited is None:
            visited = set()
        
        if not isinstance(schema, dict):
            return schema
        
        # 如果没有 $ref，直接返回
        if '$ref' not in schema:
            # 递归解析 properties 和 items 中的 $ref
            result = schema.copy()
            if 'properties' in result:
                result['properties'] = {
                    k: self._resolve_ref(v, visited)
                    for k, v in result['properties'].items()
                }
            if 'items' in result:
                result['items'] = self._resolve_ref(result['items'], visited)
            if 'allOf' in result:
                result['allOf'] = [self._resolve_ref(s, visited) for s in result['allOf']]
            if 'oneOf' in result:
                result['oneOf'] = [self._resolve_ref(s, visited) for s in result['oneOf']]
            if 'anyOf' in result:
                result['anyOf'] = [self._resolve_ref(s, visited) for s in result['anyOf']]
            return result
        
        # 解析 $ref
        ref = schema['$ref']
        
        # 避免循环引用
        if ref in visited:
            return {'type': 'object', 'description': f'循环引用: {ref}'}
        
        visited.add(ref)
        
        # 提取引用的 schema 名称
        if ref.startswith('#/'):
            parts = ref.split('/')
            if len(parts) >= 3:
                schema_name = parts[-1]
                
                # 从 schemas/definitions 中查找
                if schema_name in self.schemas:
                    referenced_schema = self.schemas[schema_name]
                    # 递归解析引用的 schema
                    resolved = self._resolve_ref(referenced_schema, visited)
                    
                    # 合并其他属性（除了 $ref）
                    result = resolved.copy()
                    for key, value in schema.items():
                        if key != '$ref':
                            result[key] = value
                    
                    return result
        
        # 如果找不到引用，返回一个默认的 object 类型
        return {'type': 'object', 'description': f'无法解析的引用: {ref}'}
    
    
    def _parse_openapi3_parameters(self, details: Dict[str, Any], path_level_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 OpenAPI 3.x 参数"""
        parsed_params = []
        
        # 先解析路径级别的参数（如果有）
        if 'parameters' in path_level_params and isinstance(path_level_params['parameters'], list):
            for param in path_level_params['parameters']:
                parsed_params.append(self._parse_single_parameter_openapi3(param))
        
        # 再解析操作级别的参数
        if 'parameters' in details:
            for param in details['parameters']:
                parsed_params.append(self._parse_single_parameter_openapi3(param))
        
        return parsed_params
    
    def _parse_single_parameter_openapi3(self, param: Dict[str, Any]) -> Dict[str, Any]:
        """解析单个 OpenAPI 3.x 参数"""
        schema = param.get('schema', {})
        return {
            'name': param.get('name'),
            'in': param.get('in'),  # query, header, path, cookie
            'description': param.get('description', ''),
            'required': param.get('required', False),
            'type': schema.get('type'),
            'schema': schema,
            'default': schema.get('default'),
            'enum': schema.get('enum'),
            'example': param.get('example') or schema.get('example'),
        }
    
    def _parse_swagger2_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析 Swagger 2.0 参数"""
        parsed_params = []
        for param in parameters:
            # 跳过 body 类型的参数（在 request_body 中处理）
            if param.get('in') == 'body':
                continue
            
            parsed_param = {
                'name': param.get('name'),
                'in': param.get('in'),  # query, header, path, formData
                'description': param.get('description', ''),
                'required': param.get('required', False),
                'type': param.get('type'),
                'schema': param.get('schema'),
                'default': param.get('default'),
                'enum': param.get('enum'),
            }
            parsed_params.append(parsed_param)
        return parsed_params
    
    def _parse_openapi3_request_body(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """解析 OpenAPI 3.x 请求体"""
        if 'requestBody' not in details:
            return {}
        
        request_body = details['requestBody']
        content = request_body.get('content', {})
        
        # 优先处理 application/json
        json_content = content.get('application/json', {})
        if json_content:
            schema = json_content.get('schema', {})
            # 解析 $ref 引用
            resolved_schema = self._resolve_ref(schema)
            return {
                'description': request_body.get('description', ''),
                'required': request_body.get('required', False),
                'content_type': 'application/json',
                'schema': resolved_schema,
            }
        
        # 处理 multipart/form-data (文件上传)
        multipart_content = content.get('multipart/form-data', {})
        if multipart_content:
            schema = multipart_content.get('schema', {})
            # 解析 $ref 引用
            resolved_schema = self._resolve_ref(schema)
            properties = resolved_schema.get('properties', {})
            
            # 将 properties 转换为 formData 参数列表
            form_params = []
            required_fields = resolved_schema.get('required', [])
            
            for param_name, param_schema in properties.items():
                param_type = param_schema.get('type', 'string')
                param_format = param_schema.get('format', '')
                
                # 如果是文件类型（binary 或 base64 格式的 string）
                if param_type == 'string' and param_format in ['binary', 'base64']:
                    param_type = 'file'
                
                param = {
                    'name': param_name,
                    'in': 'formData',
                    'description': param_schema.get('description', ''),
                    'required': param_name in required_fields,
                    'type': param_type,
                    'format': param_format,
                    'schema': param_schema,
                }
                
                form_params.append(param)
            
            return {
                'description': request_body.get('description', ''),
                'required': request_body.get('required', False),
                'content_type': 'multipart/form-data',
                'type': 'formData',
                'parameters': form_params,
                'schema': resolved_schema,
            }
        
        # 处理 application/x-www-form-urlencoded
        form_urlencoded = content.get('application/x-www-form-urlencoded', {})
        if form_urlencoded:
            schema = form_urlencoded.get('schema', {})
            # 解析 $ref 引用
            resolved_schema = self._resolve_ref(schema)
            properties = resolved_schema.get('properties', {})
            
            # 将 properties 转换为 formData 参数列表
            form_params = []
            required_fields = resolved_schema.get('required', [])
            
            for param_name, param_schema in properties.items():
                form_params.append({
                    'name': param_name,
                    'in': 'formData',
                    'description': param_schema.get('description', ''),
                    'required': param_name in required_fields,
                    'type': param_schema.get('type', 'string'),
                    'schema': param_schema,
                })
            
            return {
                'description': request_body.get('description', ''),
                'required': request_body.get('required', False),
                'content_type': 'application/x-www-form-urlencoded',
                'type': 'formData',
                'parameters': form_params,
                'schema': resolved_schema,
            }
        
        # 检查其他内容类型
        for content_type, content_detail in content.items():
            schema = content_detail.get('schema', {})
            # 解析 $ref 引用
            resolved_schema = self._resolve_ref(schema)
            return {
                'description': request_body.get('description', ''),
                'required': request_body.get('required', False),
                'content_type': content_type,
                'schema': resolved_schema,
            }
        
        return {}
    
    def _parse_swagger2_request_body(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """解析 Swagger 2.0 请求体"""
        parameters = details.get('parameters', [])
        
        # 查找 body 参数
        for param in parameters:
            if param.get('in') == 'body':
                schema = param.get('schema')
                # 解析 $ref 引用
                resolved_schema = self._resolve_ref(schema) if schema else None
                return {
                    'description': param.get('description', ''),
                    'schema': resolved_schema,
                    'required': param.get('required', False),
                    'content_type': 'application/json',
                }
        
        # 检查是否有 formData 参数
        form_params = [p for p in parameters if p.get('in') == 'formData']
        if form_params:
            return {
                'type': 'formData',
                'parameters': form_params,
                'content_type': 'application/x-www-form-urlencoded',
            }
        
        return {}
    
    def _extract_file_params_from_query(self, parameters: List[Dict[str, Any]], request_body: Dict[str, Any]) -> tuple:
        """智能识别文件上传参数：将 query 参数中明显是文件上传的参数移到 formData"""
        file_keywords = ['文件', 'file', '上传', 'upload', 'excel', 'csv', 'pdf', 'image', '图片']
        
        # 筛选出可能是文件的参数
        file_params = []
        regular_params = []
        
        for param in parameters:
            if param.get('in') != 'query':
                regular_params.append(param)
                continue
            
            param_name = param.get('name', '').lower()
            param_desc = param.get('description', '').lower()
            
            # 判断是否是文件参数
            is_file = any(keyword in param_name or keyword in param_desc for keyword in file_keywords)
            
            if is_file:
                # 转换为 formData 参数
                file_params.append({
                    'name': param['name'],
                    'in': 'formData',
                    'description': param.get('description', ''),
                    'required': param.get('required', False),
                    'type': 'file',
                })
            else:
                regular_params.append(param)
        
        # 如果识别出文件参数，更新 request_body
        if file_params:
            if not request_body or not request_body.get('type'):
                request_body = {
                    'type': 'formData',
                    'content_type': 'multipart/form-data',
                    'parameters': file_params,
                    'description': '文件上传'
                }
            elif request_body.get('type') == 'formData':
                # 如果已经有 formData，追加文件参数
                existing_params = request_body.get('parameters', [])
                request_body['parameters'] = existing_params + file_params
        
        return regular_params, request_body

def parse_swagger_file(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
    """解析 Swagger/OpenAPI 文件（支持 Swagger 2.0 和 OpenAPI 3.x）"""
    try:
        spec_json = json.loads(file_content.decode('utf-8'))
        parser = OpenAPIParser(spec_json)
        apis = parser.parse()
        
        # 添加文件名到每个API
        for api in apis:
            api['swagger_file'] = filename
        
        # 输出解析统计
        version = spec_json.get('openapi') or spec_json.get('swagger')
        print(f"成功解析 {filename}（版本: {version}），共 {len(apis)} 个接口")
            
        return apis
    except ValueError as ve:
        # 格式错误
        raise ValueError(str(ve))
    except Exception as e:
        raise ValueError(f"解析文件失败: {str(e)}")
