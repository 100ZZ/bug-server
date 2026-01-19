import request from './index'
import type { ApiEnvironment, ApiEndpoint, ApiTestData, ApiExecutionRecord, ApiTestFlow, FlowExecuteResult, FlowVariable } from './types'

// 环境管理
export const getApiEnvironments = (params?: { project_id?: number; keyword?: string; skip?: number; limit?: number }) => {
  return request.get<any, ApiEnvironment[]>('/environments', { params })
}

export const createApiEnvironment = (data: Partial<ApiEnvironment>) => {
  return request.post<any, ApiEnvironment>('/environments', data)
}

export const updateApiEnvironment = (id: number, data: Partial<ApiEnvironment>) => {
  return request.put<any, ApiEnvironment>(`/environments/${id}`, data)
}

export const deleteApiEnvironment = (id: number) => {
  return request.delete(`/environments/${id}`)
}

// 接口端点管理
export const getApiEndpoints = (params?: { project_id?: number; method?: string; tag?: string; keyword?: string; is_favorite?: boolean; skip?: number; limit?: number }) => {
  return request.get<any, ApiEndpoint[]>('/api-endpoints', { params })
}

export const getApiEndpoint = (id: number) => {
  return request.get<any, ApiEndpoint>(`/api-endpoints/${id}`)
}

export const createApiEndpoint = (data: Partial<ApiEndpoint>) => {
  return request.post<any, ApiEndpoint>('/api-endpoints', data)
}

export const updateApiEndpoint = (id: number, data: Partial<ApiEndpoint>) => {
  return request.put<any, ApiEndpoint>(`/api-endpoints/${id}`, data)
}

export const deleteApiEndpoint = (id: number) => {
  return request.delete(`/api-endpoints/${id}`)
}

export const toggleFavoriteEndpoint = (id: number, is_favorite: boolean) => {
  return request.put(`/api-endpoints/${id}/favorite`, null, { params: { is_favorite } })
}

export const toggleFavoriteFlow = (id: number, is_favorite: boolean) => {
  return request.put(`/api-flows/${id}/favorite`, null, { params: { is_favorite } })
}

// 测试数据管理
export const getApiTestDataList = (endpointId?: number) => {
  return request.get<any, ApiTestData[]>('/api-test-data', {
    params: endpointId ? { endpoint_id: endpointId } : undefined
  })
}

export const getApiTestData = (id: number) => {
  return request.get<any, ApiTestData>(`/api-test-data/${id}`)
}

export const createApiTestData = (data: Partial<ApiTestData>) => {
  return request.post<any, ApiTestData>('/api-test-data', data)
}

export const updateApiTestData = (id: number, data: Partial<ApiTestData>) => {
  return request.put<any, ApiTestData>(`/api-test-data/${id}`, data)
}

export const deleteApiTestData = (id: number) => {
  return request.delete(`/api-test-data/${id}`)
}

// 接口执行
export interface ApiExecuteRequest {
  environment_id: number
  test_data_id?: number
  path_params?: Record<string, any>
  query_params?: Record<string, any>
  headers?: Record<string, any>
  body?: Record<string, any>
  assertions?: Array<{
    type: string
    operator: string
    target?: string
    expected?: any
  }>
  global_variables?: Record<string, any>  // 全局变量，用于模板替换
}

export const executeApiEndpoint = (endpointId: number, data: ApiExecuteRequest) => {
  return request.post<any, ApiExecutionRecord>(`/api-endpoints/${endpointId}/execute`, data)
}

// 执行记录
export const getApiExecutionRecords = (params?: { endpoint_id?: number; environment_id?: number; skip?: number; limit?: number }) => {
  return request.get<any, ApiExecutionRecord[]>('/api-execution-records', { params })
}

export const getApiExecutionRecord = (id: number) => {
  return request.get<any, ApiExecutionRecord>(`/api-execution-records/${id}`)
}

// 流程测试
export const getApiFlows = (params?: { project_id?: number; keyword?: string; is_favorite?: boolean }) => {
  return request.get<any, ApiTestFlow[]>('/api-flows', { params })
}

export const getApiFlow = (id: number) => {
  return request.get<any, ApiTestFlow>(`/api-flows/${id}`)
}

export const createApiFlow = (data: Partial<ApiTestFlow>) => {
  return request.post<any, ApiTestFlow>('/api-flows', data)
}

export const updateApiFlow = (id: number, data: Partial<ApiTestFlow>) => {
  return request.put<any, ApiTestFlow>(`/api-flows/${id}`, data)
}

export const deleteApiFlow = (id: number) => {
  return request.delete(`/api-flows/${id}`)
}

export const executeApiFlow = (id: number, data?: { environment_id?: number; global_variables?: Record<string, any> }) => {
  return request.post<any, FlowExecuteResult>(`/api-flows/${id}/execute`, data)
}

// 流程变量管理
export const getFlowVariables = (flowId: number) => {
  return request.get<any, FlowVariable[]>(`/api-flows/${flowId}/variables`)
}

export const saveFlowVariables = (flowId: number, variables: Array<{ id?: number; key: string; value: string }>) => {
  return request.post<any, FlowVariable[]>(`/api-flows/${flowId}/variables`, { variables })
}

export const deleteFlowVariable = (flowId: number, variableId: number) => {
  return request.delete(`/api-flows/${flowId}/variables/${variableId}`)
}

// Swagger同步和上传
export interface SyncSwaggerRequest {
  environment_id: number
  project_id: number
  swagger_path?: string
}

export const syncSwaggerFromEnvironment = (data: SyncSwaggerRequest) => {
  return request.post<any, { message: string; deleted_count: number; imported_count: number; test_data_count: number }>('/api-endpoints/sync', null, {
    params: {
      environment_id: data.environment_id,
      project_id: data.project_id,
      swagger_path: data.swagger_path || '/v3/api-docs'
    }
  })
}

export const uploadSwaggerFile = (file: File, projectId: number) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<any, { message: string; deleted_count: number; imported_count: number; test_data_count: number; filename: string }>('/api-endpoints/upload', formData, {
    params: {
      project_id: projectId
    },
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 流程导出和导入
export interface FlowExportRecord {
  id: number
  flow_id: number
  name: string
  export_data: any
  created_at: string
}

export const exportApiFlow = (flowId: number) => {
  return request.post<any, FlowExportRecord>(`/api-flows/${flowId}/export`)
}

export const getFlowExports = (flowId: number) => {
  return request.get<any, FlowExportRecord[]>(`/api-flows/${flowId}/exports`)
}

export const getFlowExport = (flowId: number, exportId: number) => {
  return request.get<any, FlowExportRecord>(`/api-flows/${flowId}/exports/${exportId}`)
}

export const importApiFlow = (flowId: number, exportId: number) => {
  return request.post<any, ApiTestFlow>(`/api-flows/${flowId}/import/${exportId}`)
}

export const deleteFlowExport = (flowId: number, exportId: number) => {
  return request.delete(`/api-flows/${flowId}/exports/${exportId}`)
}

// 录制接口
export interface RecordApiRequest {
  project_id: number
  environment_id: number
  start_url: string
  max_depth: number
  login_url?: string
  login_username?: string
  login_password?: string
  login_data?: Record<string, any>
}

export const recordApiFromUrl = (data: RecordApiRequest) => {
  return request.post<any, { message: string; discovered_count: number; imported_count: number }>('/api-endpoints/record', data)
}

// ==================== 测试任务 ====================

export interface TestTaskItem {
  id?: number
  item_type: 'api' | 'flow'
  item_id: number
  sort_order: number
}

export interface TestTask {
  id: number
  name: string
  project_id: number
  description?: string
  status: 'idle' | 'running' | 'success' | 'failed'
  is_favorite: boolean
  cron_expression?: string
  environment_id?: number
  created_at: string
  updated_at: string
  items?: TestTaskItem[]
  project?: {
    id: number
    name: string
  }
}

export interface TestTaskCreate {
  name: string
  project_id: number
  description?: string
  items?: TestTaskItem[]
  cron_expression?: string
  environment_id?: number
}

export interface TestTaskUpdate {
  name?: string
  description?: string
  items?: TestTaskItem[]
  is_favorite?: boolean
  cron_expression?: string
  environment_id?: number
}

export interface TestTaskExecutionRequest {
  environment_id: number
}

export interface TestTaskExecutionResult {
  item_type: 'api' | 'flow'
  item_id: number
  item_name: string
  success: boolean
  status_code?: number
  error_message?: string
  execution_time?: number
  details?: any
}

export interface TestTaskExecution {
  id: number
  task_id: number
  environment_id?: number
  status: 'running' | 'success' | 'failed'
  total_count: number
  success_count: number
  failed_count: number
  execution_results?: TestTaskExecutionResult[]
  error_message?: string
  started_at: string
  completed_at?: string
}

// 获取测试任务列表
export const getTestTasks = (params?: {
  project_id?: number
  keyword?: string
  status?: string
  is_favorite?: boolean
}) => {
  return request.get<TestTask[]>('/test-tasks', { params })
}

// 获取测试任务详情
export const getTestTask = (taskId: number) => {
  return request.get<TestTask>(`/test-tasks/${taskId}`)
}

// 创建测试任务
export const createTestTask = (data: TestTaskCreate) => {
  return request.post<TestTask>('/test-tasks', data)
}

// 更新测试任务
export const updateTestTask = (taskId: number, data: TestTaskUpdate) => {
  return request.put<TestTask>(`/test-tasks/${taskId}`, data)
}

// 删除测试任务
export const deleteTestTask = (taskId: number) => {
  return request.delete(`/test-tasks/${taskId}`)
}

// 切换收藏状态
export const toggleTestTaskFavorite = (taskId: number) => {
  return request.post<{ message: string; is_favorite: boolean }>(`/test-tasks/${taskId}/toggle-favorite`)
}

// 执行测试任务
export const executeTestTask = (taskId: number, data: TestTaskExecutionRequest) => {
  return request.post<TestTaskExecution>(`/test-tasks/${taskId}/execute`, data)
}

// 获取执行记录列表
export const getTestTaskExecutions = (taskId: number) => {
  return request.get<TestTaskExecution[]>(`/test-tasks/${taskId}/executions`)
}

// 获取执行记录详情
export const getTestTaskExecution = (taskId: number, executionId: number) => {
  return request.get<TestTaskExecution>(`/test-tasks/${taskId}/executions/${executionId}`)
}
