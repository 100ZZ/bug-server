import request from './index'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: any
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

// 登录
export const login = (data: LoginRequest) => {
  return request.post<LoginResponse>('/auth/login', data)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get('/auth/me')
}

// 登出
export const logout = () => {
  return request.post('/auth/logout')
}

// 修改密码
export const changePassword = (userId: number, data: ChangePasswordRequest) => {
  return request.post(`/auth/change-password?user_id=${userId}`, data)
}

// 更新当前用户的当前项目
export const updateCurrentProject = (projectId: number | null) => {
  const params: any = {}
  if (projectId !== null && projectId !== undefined) {
    params.project_id = projectId
  }
  // 如果projectId为null，不传参数，后端会清空
  return request.put('/auth/current-project', null, { params })
}
