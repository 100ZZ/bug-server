export interface Project {
  id: number
  name: string
  key?: string
  description?: string
  lead?: string
  member_ids?: number[]
  members?: User[]
  created_at: string
  updated_at: string
}

export interface Sprint {
  id: number
  project_id: number
  name: string
  goal?: string
  owner?: string
  start_date: string
  end_date: string
  created_at: string
  updated_at: string
  project?: Project
}

export interface User {
  id: number
  username: string
  email: string
  display_name?: string
  avatar_url?: string
  roles: string[]
  status: string
  created_at: string
  updated_at: string
}

export interface Bug {
  id: number
  bug_key: string
  project_id: number
  title: string
  description?: string
  type: string
  priority: string
  severity: string
  status: string
  resolution: string
  assignee_id?: number
  reporter_id: number
  verifier_id?: number
  environment?: string
  version?: string
  fix_version?: string
  module?: string
  steps_to_reproduce?: string
  expected_result?: string
  actual_result?: string
  attachments?: string[]
  tags?: string[]
  due_date?: string
  estimated_hours?: number
  actual_hours?: number
  resolved_at?: string
  closed_at?: string
  created_at: string
  updated_at: string
  project?: Project
  reporter?: User
  assignee?: User
  verifier?: User
}

export interface Comment {
  id: number
  bug_id: number
  user_id: number
  content: string
  attachments?: string[]
  created_at: string
  updated_at: string
  user?: User
}

export interface Statistics {
  total: number
  open: number
  in_progress: number
  resolved: number
  closed: number
  by_priority: Record<string, number>
  by_severity: Record<string, number>
  by_type: Record<string, number>
}

export interface TestCase {
  id: number
  case_key: string
  project_id: number
  title: string
  module?: string
  precondition?: string
  steps?: Array<{ step: string; expected: string }>
  expected_result?: string
  priority: string
  type: string
  status: string
  tags?: string[]
  created_by: number
  updated_by?: number
  created_at: string
  updated_at: string
  project?: Project
  creator?: User
  updater?: User
}

export interface TestCaseReview {
  id: number
  project_id: number
  sprint_id?: number
  name: string
  initiator_id: number
  start_date: string // ISO date string
  end_date: string // ISO date string
  status: string // 'not_started' | 'in_progress' | 'ended'
  created_at: string
  updated_at: string
  project?: Project
  sprint?: Sprint
  initiator?: User
  review_items?: TestCaseReviewItem[]
}

export interface TestCaseReviewItem {
  id: number
  review_id: number
  testcase_id: number
  reviewer_id?: number
  status: string // 'pending' | 'approved' | 'rejected'
  comments?: string
  reviewed_at?: string
  created_at: string
  updated_at: string
  review?: TestCaseReview
  testcase?: TestCase
  reviewer?: User
}

// 接口测试相关类型
export interface ApiEnvironment {
  id: number
  project_id: number
  name: string
  base_url: string
  description?: string
  headers?: Record<string, any>
  created_at: string
  updated_at: string
  project?: Project
}

export interface ApiEndpoint {
  id: number
  project_id: number
  name: string
  path: string
  method: string
  description?: string
  tags?: string[]
  parameters?: SwaggerParameter[]  // Swagger参数列表
  request_body?: SwaggerRequestBody  // Swagger请求体定义
  is_favorite?: boolean  // 是否收藏
  created_at: string
  updated_at: string
  project?: Project
}

// Swagger参数类型
export interface SwaggerParameter {
  name: string
  in: 'path' | 'query' | 'header' | 'cookie' | 'formData'
  description?: string
  required?: boolean
  type?: string
  schema?: Record<string, any>
  default?: any
  enum?: any[]
  example?: any
}

// Swagger请求体类型
export interface SwaggerRequestBody {
  description?: string
  required?: boolean
  content_type?: string
  schema?: Record<string, any>
  type?: string
  parameters?: SwaggerParameter[]  // formData参数
}

export interface ApiTestData {
  id: number
  endpoint_id: number
  name: string
  path_params?: Record<string, any>
  query_params?: Record<string, any>
  headers?: Record<string, any>
  body?: Record<string, any>
  expected_status: number
  assertions?: Array<{
    type: string
    operator: string
    target?: string
    expected?: any
  }>
  created_at: string
  updated_at: string
}

export interface ApiExecutionRecord {
  id: number
  endpoint_id: number
  test_data_id?: number
  environment_id: number
  request_url?: string
  request_method?: string
  request_headers?: Record<string, any>
  request_body?: any
  response_status?: number
  response_headers?: Record<string, any>
  response_body?: string
  response_time?: number
  success: boolean
  error_message?: string
  executed_at: string
}

export interface FlowExtractRule {
  name: string
  path: string
  step_index?: number  // 从第几个接口提取（1-based），如果为undefined或0，则从当前接口提取
}

export interface FlowStep {
  endpoint_id: number
  environment_id?: number
  test_data_id?: number
  alias?: string
  enabled?: boolean  // 是否启用，默认为true
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
  extracts?: FlowExtractRule[]
}

export interface ApiTestFlow {
  id: number
  project_id: number
  name: string
  description?: string
  environment_id?: number
  global_variables?: Record<string, any>
  steps: FlowStep[]
  is_favorite?: boolean
  created_at: string
  updated_at: string
  project?: Project
}

export interface FlowExecuteResult {
  success: boolean
  results: Array<{
    index: number
    endpoint_id: number
    endpoint_name?: string
    url?: string
    method?: string
    success: boolean
    status?: number
    response_time?: number
    error_message?: string
    alias?: string
    extracted?: Record<string, any>
    // 请求信息
    request_headers?: Record<string, any>
    request_path_params?: Record<string, any>
    request_query_params?: Record<string, any>
    request_body?: any
    request_assertions?: Array<{
      type: string
      operator: string
      target?: string
      expected?: any
    }>
    // 响应信息
    response_headers?: Record<string, any>
    response_body?: string
  }>
  context: Record<string, any>
}

export interface FlowVariable {
  id: number
  flow_id: number
  key: string
  value: string
  created_at?: string
  updated_at?: string
}

export interface CodeScan {
  id: number
  project_id: number
  project?: Project
  project_name: string
  branch: string
  scan_path: string
  language?: string
  sonar_project_key?: string
  sonar_host?: string
  sonar_login?: string
  scan_time?: string
  result?: 'passed' | 'failed'
  scanning?: boolean
  created_at: string
  updated_at: string
}

export interface Model {
  id: number
  name: string
  provider: 'openai' | 'deepseek' | 'qwen' | 'doubao' | 'local'
  type: 'api' | 'local'
  api_key?: string
  api_base?: string
  model_path?: string
  model_name?: string
  is_default: boolean
  status: 'active' | 'inactive'
  description?: string
  created_at: string
  updated_at: string
}

export interface CodeScanResult {
  id: number
  scan_id: number
  scan?: CodeScan
  status?: 'running' | 'completed' | 'failed'
  error_message?: string
  scan_output?: string
  issues?: Array<{
    severity: string
    type: string
    message: string
    file: string
    line?: number
    rule?: string
  }>
  metrics?: {
    bugs?: number
    vulnerabilities?: number
    code_smells?: number
    coverage?: number
    duplicated_lines?: number
  }
  status: 'running' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

