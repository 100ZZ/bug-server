import requests
import time
import re
from typing import Dict, Any, Optional, List
from models import API, Environment, TestData
from sqlalchemy.orm import Session
import json
from jsonpath_ng import parse as jsonpath_parse

class APIExecutor:
    """API执行引擎"""
    
    def __init__(self, api: API, environment: Environment, db: Optional[Session] = None,
                 api_results: Optional[List[Dict[str, Any]]] = None,
                 global_variables: Optional[Dict[str, Any]] = None):
        self.api = api
        self.environment = environment
        self.db = db
        self.variables = {}  # 存储提取的变量（前置接口变量）
        self.api_results = api_results or []  # 执行链中所有接口的执行结果列表
        self.global_variables = global_variables or {}  # 全局变量
        
    def execute(self, 
                path_params: Optional[Dict[str, Any]] = None,
                query_params: Optional[Dict[str, Any]] = None,
                headers: Optional[Dict[str, Any]] = None,
                body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行API请求"""
        
        # 构建URL
        url = self._build_url(path_params)
        
        # 合并请求头
        print(f"  🔗 合并前的 headers 参数: {headers}")
        request_headers = self._merge_headers(headers)
        print(f"  📋 最终发送的 request_headers: {request_headers}")
        
        # 准备请求参数
        request_kwargs = {
            'method': self.api.method,
            'url': url,
            'headers': request_headers,
        }
        print(f"  🚀 准备发送请求: {self.api.method} {url}")
        print(f"  📦 请求头: {request_headers}")
        
        # 添加查询参数
        if query_params:
            request_kwargs['params'] = query_params
        
        # 添加请求体
        if body and self.api.method.upper() in ['POST', 'PUT', 'PATCH']:
            content_type = request_headers.get('Content-Type', 'application/json')
            if 'application/json' in content_type:
                request_kwargs['json'] = body
            else:
                request_kwargs['data'] = body
        
        # 执行请求
        start_time = time.time()
        try:
            response = requests.request(**request_kwargs, timeout=30)
            response_time = int((time.time() - start_time) * 1000)  # 毫秒
            
            # 解析响应体
            try:
                response_body = response.json()
            except:
                response_body = response.text
            
            # 构建响应头字典
            response_headers = dict(response.headers)
            
            return {
                'request_url': url,
                'request_method': self.api.method,
                'request_headers': request_headers,
                'request_body': body,
                'response_status': response.status_code,
                'response_headers': response_headers,
                'response_body': response_body,
                'response_time': response_time,
                'success': 200 <= response.status_code < 300,
                'error_message': None
            }
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            return {
                'request_url': url,
                'request_method': self.api.method,
                'request_headers': request_headers,
                'request_body': body,
                'response_status': None,
                'response_headers': None,
                'response_body': None,
                'response_time': response_time,
                'success': False,
                'error_message': str(e)
            }
    
    def execute_with_test_data(self, test_data: TestData) -> Dict[str, Any]:
        """使用测试数据执行API（支持前置接口）"""
        # 1. 执行前置接口（如果配置了）
        if test_data.pre_request_api_id and self.db:
            self._execute_pre_request(test_data)
        
        # 2. 替换参数中的变量占位符（包括 $.api[n] 等高级变量引用）
        print(f"  🔧 开始替换变量，api_results 数量: {len(self.api_results)}")
        print(f"  📥 替换前的 headers: {test_data.headers}")
        
        path_params = self._replace_variables(test_data.path_params)
        query_params = self._replace_variables(test_data.query_params)
        headers = self._replace_variables(test_data.headers)
        body = self._replace_variables(test_data.body)
        
        print(f"  📤 替换后的 headers: {headers}")
        print(f"  📤 替换后的 headers 类型: {type(headers)}")
        
        # 3. 执行主接口
        return self.execute(
            path_params=path_params,
            query_params=query_params,
            headers=headers,
            body=body
        )
    
    def _build_url(self, path_params: Optional[Dict[str, Any]] = None) -> str:
        """构建完整的URL"""
        url = self.environment.base_url + self.api.path
        
        # 替换路径参数
        if path_params:
            for key, value in path_params.items():
                url = url.replace(f'{{{key}}}', str(value))
        
        return url
    
    def _merge_headers(self, headers: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """合并请求头（环境请求头 + 自定义请求头）"""
        merged_headers = {}
        
        # 添加环境请求头
        if self.environment.headers:
            print(f"    🌍 环境请求头: {self.environment.headers}")
            for key, value in self.environment.headers.items():
                merged_headers[key] = str(value)
        
        # 添加自定义请求头
        if headers:
            print(f"    📝 自定义请求头: {headers}")
            print(f"    📝 自定义请求头类型: {type(headers)}")
            for key, value in headers.items():
                # 确保值是字符串类型
                str_value = str(value) if value is not None else ""
                merged_headers[key] = str_value
                print(f"      ✅ 添加 Header: {key} = {str_value}")
        else:
            print(f"    ⚠️ 自定义请求头为空或None")
        
        print(f"    📋 合并后的请求头: {merged_headers}")
        return merged_headers
    
    def _execute_pre_request(self, test_data: TestData) -> None:
        """执行前置接口并提取变量"""
        try:
            # 获取前置接口配置
            pre_api = self.db.query(API).filter(API.id == test_data.pre_request_api_id).first()
            if not pre_api:
                print(f"⚠️ 警告: 找不到前置接口 ID={test_data.pre_request_api_id}")
                return
            
            # 获取前置接口的测试数据（如果指定）
            pre_test_data = None
            if test_data.pre_request_test_data_id:
                pre_test_data = self.db.query(TestData).filter(
                    TestData.id == test_data.pre_request_test_data_id
                ).first()
            
            # 创建前置接口的执行器（传递当前的 api_results，以便前置接口也能引用之前的接口）
            pre_executor = APIExecutor(
                pre_api, 
                self.environment, 
                self.db,
                api_results=self.api_results.copy(),  # 传递已有的 api_results
                global_variables=self.global_variables  # 传递全局变量
            )
            
            # 执行前置接口
            if pre_test_data:
                print(f"🔄 执行前置接口: {pre_api.method} {pre_api.path} (使用测试数据: {pre_test_data.name})")
                result = pre_executor.execute(
                    path_params=pre_test_data.path_params,
                    query_params=pre_test_data.query_params,
                    headers=pre_test_data.headers,
                    body=pre_test_data.body
                )
            else:
                print(f"🔄 执行前置接口: {pre_api.method} {pre_api.path} (无测试数据)")
                result = pre_executor.execute()
            
            # 检查前置接口是否执行成功
            if not result.get('success'):
                error_msg = result.get('error_message', '未知错误')
                print(f"❌ 前置接口执行失败: {error_msg}")
                return
            
            # 保存前置接口结果到 api_results，供 $.api[n] 引用
            if not self.api_results:
                self.api_results = []
            self.api_results.append(result)  # 追加到列表末尾
            print(f"📦 前置接口结果已保存到 api_results，当前索引: {len(self.api_results) - 1}")
            print(f"   响应体: {result.get('response_body')}")
            
            # 提取变量（用于 {{变量名}} 格式）
            response_body = result.get('response_body')
            if response_body and test_data.variable_extractions:
                self._extract_variables(response_body, test_data.variable_extractions)
                print(f"✅ 前置接口执行成功，提取变量: {list(self.variables.keys())}")
            
        except Exception as e:
            print(f"❌ 执行前置接口时发生错误: {str(e)}")
    
    def _extract_variables(self, response_body: Any, extraction_rules: Dict[str, str]) -> None:
        """从响应中提取变量
        
        Args:
            response_body: 响应体（通常是字典）
            extraction_rules: 提取规则，格式: {"varName": "$.data.accessToken"}
        """
        if not isinstance(response_body, dict):
            print(f"⚠️ 警告: 响应体不是字典类型，无法提取变量")
            return
        
        for var_name, jsonpath_expr in extraction_rules.items():
            try:
                # 使用 JSONPath 提取值
                if jsonpath_expr.startswith('$.'):
                    # 使用 jsonpath_ng 库
                    jsonpath_expression = jsonpath_parse(jsonpath_expr)
                    matches = jsonpath_expression.find(response_body)
                    if matches:
                        value = matches[0].value
                        self.variables[var_name] = value
                        print(f"  📌 提取变量 {var_name} = {value}")
                    else:
                        print(f"  ⚠️ 未找到匹配的值: {jsonpath_expr}")
                else:
                    # 简单的字典键访问，支持点号分隔的路径
                    keys = jsonpath_expr.split('.')
                    value = response_body
                    for key in keys:
                        if isinstance(value, dict) and key in value:
                            value = value[key]
                        else:
                            print(f"  ⚠️ 路径不存在: {jsonpath_expr}")
                            value = None
                            break
                    if value is not None:
                        self.variables[var_name] = value
                        print(f"  📌 提取变量 {var_name} = {value}")
            except Exception as e:
                print(f"  ❌ 提取变量 {var_name} 时出错: {str(e)}")
    
    def _replace_variables(self, data: Any) -> Any:
        """递归替换数据中的变量占位符
        
        支持的占位符格式:
        1. {{variableName}} - 前置接口提取的变量
        2. $.api[n].response_body.field - 引用执行链中第n个接口的响应
        3. $.global.变量名 - 引用全局变量
        4. list.find(id=122).name - 从列表中查找特定条件的项
        """
        if data is None:
            return data
        
        if isinstance(data, str):
            # 先处理 $.api[n]、$.global 格式
            data = self._replace_advanced_variables(data)
            
            # 再处理 {{variableName}} 格式（前置接口变量）
            for var_name, var_value in self.variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                if placeholder in data:
                    # 如果整个字符串就是占位符，直接返回变量值（保持类型）
                    if data == placeholder:
                        return var_value
                    # 否则进行字符串替换
                    data = data.replace(placeholder, str(var_value))
            return data
        
        elif isinstance(data, dict):
            # 递归处理字典
            return {key: self._replace_variables(value) for key, value in data.items()}
        
        elif isinstance(data, list):
            # 递归处理列表
            return [self._replace_variables(item) for item in data]
        
        else:
            # 其他类型直接返回
            return data
    
    def _replace_advanced_variables(self, text: str) -> str:
        """替换高级变量引用格式
        
        支持格式:
        - $.api[n].response_body.field - 引用执行链中第n个接口的响应
        - $.global.变量名 - 引用全局变量
        - list.find(id=122).name - 从列表中查找特定条件的项
        
        字符串拼接场景：
        - "Bearer $.api[0].response_body.data.accessToken" 
          → "Bearer ef0dc0acd13c4396b40053552a20352d"
        - 支持在字符串任意位置使用变量引用
        
        优化思路：
        1. 如果整个字符串就是一个变量引用，直接解析 JSONPath（更快）
        2. 如果字符串包含变量引用（字符串拼接），使用正则表达式匹配替换
        """
        if not isinstance(text, str):
            return text
        
        # 先检查整个字符串是否就是一个变量引用（优化：避免不必要的正则匹配）
        if text.strip().startswith('$.api['):
            # 尝试直接解析整个字符串
            value = self._parse_variable_reference(text.strip())
            if value is not None:
                return str(value)
        
        # 如果整个字符串不是变量引用，或者解析失败，使用正则表达式匹配替换
        # 匹配 $.api[n] 格式（索引从 1 开始）
        # 注意：需要匹配完整路径，即使前后有其他文本（如 "Bearer " 前缀）
        # 使用非贪婪匹配，匹配到字符串结束或遇到明显的分隔符（引号、逗号、大括号等）
        pattern = r'\$\.api\[(\d+)\]\.response_body((?:\.[a-zA-Z_][a-zA-Z0-9_]*|\[[0-9]+\])*?)(?=\$\.|{{|["\']|,|}|$|\))'
        matches = list(re.finditer(pattern, text))
        for match in reversed(matches):  # 从后往前替换，避免索引变化
            user_index = int(match.group(1))  # 用户输入的索引（从 1 开始）
            jsonpath = match.group(2).strip()  # 后续的 JSONPath，去除首尾空格
            
            # 如果 jsonpath 以点开头，去掉开头的点
            if jsonpath.startswith('.'):
                jsonpath = jsonpath[1:]
            
            # 获取对应的结果列表
            results = self.api_results
            
            # 将用户索引转换为数组索引（用户从 1 开始，数组从 0 开始）
            array_index = user_index - 1
            
            # 检查索引是否有效
            print(f"  🔍 尝试从 $.api[{user_index}] 提取值（数组索引: {array_index}），路径: {jsonpath}")
            print(f"  📊 api_results 列表长度: {len(results)}")
            
            if 0 <= array_index < len(results):
                result = results[array_index]
                response_body = result.get('response_body')
                print(f"  📦 响应体类型: {type(response_body)}, 内容: {response_body}")
                
                if response_body:
                    # 提取值
                    value = self._extract_value_by_jsonpath(response_body, jsonpath)
                    print(f"  🎯 提取到的值: {value}")
                    
                    if value is not None:
                        # 替换整个引用
                        full_ref = match.group(0)
                        text = text[:match.start()] + str(value) + text[match.end():]
                        print(f"  ✅ 替换变量: {full_ref} -> {value}")
                        print(f"  📝 替换后的文本: {text}")
                    else:
                        print(f"  ⚠️ 无法从 $.api[{user_index}].response_body.{jsonpath} 提取值")
                        print(f"  📋 响应体: {response_body}")
                        # 打印可用路径用于调试
                        if isinstance(response_body, dict):
                            print(f"  🔑 可用键: {list(response_body.keys())}")
            else:
                print(f"  ❌ 索引 {user_index} 超出范围，api_results 列表只有 {len(results)} 个元素（有效范围: 1-{len(results)}）")
        
        # 匹配 $.global.变量名 格式
        if text.startswith('$.global.'):
            # 直接解析全局变量
            parts = text.split('.', 2)
            if len(parts) == 3:
                var_name = parts[2]
                if var_name in self.global_variables:
                    return str(self.global_variables[var_name])
        else:
            # 使用正则表达式匹配字符串中的全局变量引用
            pattern = r'\$\.global\.([a-zA-Z_][a-zA-Z0-9_]*)'
            matches = list(re.finditer(pattern, text))
            for match in reversed(matches):  # 从后往前替换
                var_name = match.group(1)
                if var_name in self.global_variables:
                    value = self.global_variables[var_name]
                    full_ref = match.group(0)
                    text = text[:match.start()] + str(value) + text[match.end():]
                    print(f"  ✅ 替换全局变量: {full_ref} -> {value}")
        
        return text
    
    def _parse_variable_reference(self, ref: str) -> Any:
        """直接解析变量引用字符串
        
        例如: $.api[1].response_body.data.accessToken
        返回: 提取的值
        注意: 索引从 1 开始（$.api[1] 表示第一个接口）
        """
        # 解析 $.api[n] 格式（索引从 1 开始）
        if ref.startswith('$.api['):
            # 提取索引和路径
            match = re.match(r'\$\.api\[(\d+)\]\.response_body(.*)', ref)
            if match:
                user_index = int(match.group(1))  # 用户输入的索引（从 1 开始）
                jsonpath = match.group(2).strip()
                
                # 如果 jsonpath 以点开头，去掉开头的点
                if jsonpath.startswith('.'):
                    jsonpath = jsonpath[1:]
                
                # 获取对应的结果列表
                results = self.api_results
                
                # 将用户索引转换为数组索引（用户从 1 开始，数组从 0 开始）
                array_index = user_index - 1
                
                # 检查索引是否有效
                if 0 <= array_index < len(results):
                    result = results[array_index]
                    response_body = result.get('response_body')
                    if response_body:
                        # 直接使用 JSONPath 提取值
                        return self._extract_value_by_jsonpath(response_body, jsonpath)
        
        # 解析 $.global.变量名 格式
        if ref.startswith('$.global.'):
            var_name = ref.replace('$.global.', '')
            if var_name in self.global_variables:
                return self.global_variables[var_name]
        
        return None
    
    def _extract_value_by_jsonpath(self, data: Any, jsonpath: str) -> Any:
        """使用 JSONPath 从数据中提取值，支持 list.find(...) 语法"""
        if not jsonpath or jsonpath == '':
            return data
        
        # 处理 list.find(...) 语法
        find_pattern = r'\.find\(([^)]+)\)'
        find_match = re.search(find_pattern, jsonpath)
        if find_match:
            # 提取 find 条件，如 "id=122"
            condition_str = find_match.group(1)
            # 分割条件
            if '=' in condition_str:
                key, value = condition_str.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')  # 去除引号
                
                # 获取 find 之前的路径
                before_find = jsonpath[:find_match.start()]
                # 获取 find 之后的路径
                after_find = jsonpath[find_match.end():]
                
                # 先获取列表
                if before_find:
                    list_data = self._extract_value_by_jsonpath(data, before_find)
                else:
                    list_data = data
                
                # 在列表中查找匹配的项
                if isinstance(list_data, list):
                    for item in list_data:
                        if isinstance(item, dict):
                            # 尝试匹配值（支持字符串和数字）
                            item_value = item.get(key)
                            if item_value is not None:
                                # 尝试转换为相同类型进行比较
                                try:
                                    # 如果 value 是数字字符串，尝试转换为数字
                                    if isinstance(item_value, (int, float)):
                                        try:
                                            value_num = float(value) if '.' in value else int(value)
                                            if item_value == value_num:
                                                # 找到匹配项，继续提取后续路径
                                                if after_find:
                                                    return self._extract_value_by_jsonpath(item, after_find)
                                                else:
                                                    return item
                                        except ValueError:
                                            pass
                                    
                                    # 字符串比较
                                    if str(item_value) == str(value):
                                        # 找到匹配项，继续提取后续路径
                                        if after_find:
                                            return self._extract_value_by_jsonpath(item, after_find)
                                        else:
                                            return item
                                except Exception:
                                    pass
                    return None
        
        # 使用 JSONPath 提取
        # 去掉开头的点（如果有）
        jsonpath = jsonpath.lstrip('.')
        
        try:
            # 使用 jsonpath_ng 库（如果路径以 $. 开头）
            if jsonpath.startswith('$.'):
                jsonpath_expression = jsonpath_parse(jsonpath)
                matches = jsonpath_expression.find(data)
                if matches:
                    return matches[0].value
            else:
                # 简单的点号分隔路径
                keys = jsonpath.split('.')
                value = data
                for key in keys:
                    if not key:  # 跳过空键
                        continue
                    # 处理数组索引，如 list[0]
                    if '[' in key and ']' in key:
                        key_name, index_str = key.split('[')
                        index = int(index_str.rstrip(']'))
                        if isinstance(value, dict) and key_name in value:
                            value = value[key_name]
                            if isinstance(value, list) and 0 <= index < len(value):
                                value = value[index]
                            else:
                                return None
                        else:
                            return None
                    else:
                        if isinstance(value, dict) and key in value:
                            value = value[key]
                        elif isinstance(value, list):
                            # 如果是列表，尝试访问第一个元素
                            if len(value) > 0:
                                value = value[0]
                                if isinstance(value, dict) and key in value:
                                    value = value[key]
                                else:
                                    return None
                            else:
                                return None
                        else:
                            return None
                return value
        except Exception as e:
            print(f"  ⚠️ JSONPath 提取失败: {jsonpath}, 错误: {str(e)}")
            return None

