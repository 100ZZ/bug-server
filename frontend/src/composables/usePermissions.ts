/**
 * 权限管理 Composable
 */
import { ref, computed } from 'vue'
import request from '../api/index'
import { tokenManager } from '../utils/token'

export interface Permission {
  projects: string[]
  users: string[]
  bugs: string[]
  comments: string[]
  statistics: string[]
}

export interface UserPermission {
  user_id: number
  username: string
  email?: string
  display_name?: string
  role: string
  role_name: string
  permissions: Permission
  token?: string
}

// 默认游客权限
const getGuestUser = (): UserPermission => ({
  user_id: 0,
  username: 'guest',
  role: 'guest',
  role_name: '游客',
  permissions: {
    projects: ['read'],
    users: ['read'],
    bugs: ['read'],
    comments: ['read'],
    statistics: ['read']
  }
})

// 当前用户信息
const currentUser = ref<UserPermission>(getGuestUser())

// 从后端加载用户信息
let userLoadingPromise: Promise<void> | null = null
const loadUserFromServer = async (): Promise<void> => {
  if (!tokenManager.hasToken()) {
    currentUser.value = getGuestUser()
    return
  }

  try {
    const user = await request.get('/auth/me')
    const roleNames: Record<string, string> = {
      admin: '管理员',
      product: '产品经理',
      developer: '开发人员',
      tester: '测试人员',
      guest: '游客'
    }
    const rolePermissions: Record<string, Permission> = {
      admin: {
        projects: ['create', 'read', 'update', 'delete'],
        users: ['create', 'read', 'update', 'delete'],
        bugs: ['create', 'read', 'update', 'delete'],
        comments: ['create', 'read', 'update', 'delete'],
        statistics: ['read']
      },
      product: {
        projects: ['read'],
        users: ['read'],
        bugs: ['create', 'read', 'update'],
        comments: ['create', 'read'],
        statistics: ['read']
      },
      developer: {
        projects: ['read'],
        users: ['read'],
        bugs: ['read', 'update'],
        comments: ['create', 'read'],
        statistics: ['read']
      },
      tester: {
        projects: ['read'],
        users: ['read'],
        bugs: ['create', 'read', 'update'],
        comments: ['create', 'read'],
        statistics: ['read']
      },
      guest: {
        projects: ['read'],
        users: ['read'],
        bugs: ['read'],
        comments: ['read'],
        statistics: ['read']
      }
    }

    // 从 roles 数组中取第一个角色（或优先使用 'admin'）
    const userRoles = user.roles || []
    let primaryRole = 'guest'
    if (userRoles.length > 0) {
      if (userRoles.includes('admin')) {
        primaryRole = 'admin'
      } else {
        primaryRole = userRoles[0]
      }
    }

    currentUser.value = {
      user_id: user.id,
      username: user.username,
      email: user.email,
      display_name: user.display_name,
      role: primaryRole,
      role_name: roleNames[primaryRole] || primaryRole,
      permissions: rolePermissions[primaryRole] || rolePermissions.guest
    }
  } catch (error) {
    console.error('Failed to load user from server:', error)
    currentUser.value = getGuestUser()
    tokenManager.clearToken()
  }
}

export function usePermissions() {
  /**
   * 检查是否有权限
   */
  const hasPermission = (resource: keyof Permission, action: string): boolean => {
    if (!currentUser.value || !currentUser.value.permissions) {
      return false
    }
    
    const resourcePermissions = currentUser.value.permissions[resource]
    if (!resourcePermissions) {
      return false
    }
    
    return resourcePermissions.includes(action)
  }

  /**
   * 检查是否可以创建
   */
  const canCreate = (resource: keyof Permission): boolean => {
    return hasPermission(resource, 'create')
  }

  /**
   * 检查是否可以更新
   */
  const canUpdate = (resource: keyof Permission): boolean => {
    return hasPermission(resource, 'update')
  }

  /**
   * 检查是否可以删除
   */
  const canDelete = (resource: keyof Permission): boolean => {
    return hasPermission(resource, 'delete')
  }

  /**
   * 检查是否可以读取
   */
  const canRead = (resource: keyof Permission): boolean => {
    return hasPermission(resource, 'read')
  }

  /**
   * 检查是否是管理员
   */
  const isAdmin = computed(() => {
    return currentUser.value?.role === 'admin'
  })

  /**
   * 检查是否是游客
   */
  const isGuest = computed(() => {
    return currentUser.value?.role === 'guest'
  })

  /**
   * 检查是否是项目成员（admin 始终返回 true）
   */
  const isProjectMember = (project: { members?: Array<{ id: number }> } | null | undefined): boolean => {
    if (!project) return false
    // admin 可以操作所有项目
    if (currentUser.value?.role === 'admin') return true
    // 检查当前用户是否在项目成员列表中
    if (!project.members || project.members.length === 0) return false
    const userId = currentUser.value?.user_id
    if (!userId) return false
    return project.members.some(member => member.id === userId)
  }

  /**
   * 设置当前用户
   */
  const setCurrentUser = async (user: UserPermission) => {
    // 保存 token 到内存
    if (user.token) {
      tokenManager.setToken(user.token)
    }
    
    // 从服务器重新加载用户信息（确保数据最新）
    await loadUserFromServer()
  }

  /**
   * 清除当前用户（登出）
   */
  const clearCurrentUser = () => {
    // 清除 token
    tokenManager.clearToken()
    
    // 重置为游客权限
    currentUser.value = getGuestUser()
  }

  /**
   * 刷新用户信息（从服务器重新加载）
   */
  const refreshUser = async () => {
    await loadUserFromServer()
  }

  /**
   * 获取当前用户
   */
  const getCurrentUser = () => {
    return currentUser.value
  }

  /**
   * 获取角色名称
   */
  const getRoleName = computed(() => {
    return currentUser.value?.role_name || ''
  })

  /**
   * 检查是否已登录
   */
  const isLoggedIn = computed(() => {
    return currentUser.value.user_id > 0
  })

  // 初始化时，如果有 token，尝试加载用户信息
  if (tokenManager.hasToken() && currentUser.value.user_id === 0) {
    if (!userLoadingPromise) {
      userLoadingPromise = loadUserFromServer()
    }
  }

  return {
    currentUser,
    hasPermission,
    canCreate,
    canUpdate,
    canDelete,
    canRead,
    isAdmin,
    isGuest,
    isLoggedIn,
    isProjectMember,
    setCurrentUser,
    clearCurrentUser,
    getCurrentUser,
    getRoleName,
    refreshUser
  }
}

