import request from './index'

/**
 * 获取用户权限
 */
export const getUserPermissions = (userId: number) => {
  return request.get(`/permissions/${userId}`)
}

/**
 * 获取所有角色列表
 */
export const getAllRoles = () => {
  return request.get('/roles')
}

