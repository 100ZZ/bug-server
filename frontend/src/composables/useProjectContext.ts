/**
 * 项目上下文管理 Composable
 * 用于管理当前选中的项目（单选），实现全局项目过滤功能
 * 使用数据库存储，而不是localStorage
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as projectApi from '../api/projects'
import * as authApi from '../api/auth'
import { tokenManager } from '../utils/token'

export interface ProjectContext {
  id: number
  name: string
  description?: string
}

// 当前选中的项目（单选）
const currentProject = ref<ProjectContext | null>(null)

// 项目列表缓存
const projectsCache = ref<any[]>([])

/**
 * 从数据库加载当前用户的当前项目
 */
const loadCurrentProjectFromDB = async (): Promise<ProjectContext | null> => {
  // 先检查是否有 token，避免不必要的 API 调用
  if (!tokenManager.hasToken()) {
    return null
  }
  
  try {
    const user = await authApi.getCurrentUser()
    if (user && user.current_project_id) {
      // 确保项目列表已加载
      if (projectsCache.value.length === 0) {
        await loadProjects()
      }
      
      const project = projectsCache.value.find(p => p.id === user.current_project_id)
      if (project) {
        return {
          id: project.id,
          name: project.name,
          description: project.description
        }
      }
    }
  } catch (error: any) {
    // 如果是未授权错误（401），静默处理，不输出错误
    if (error?.response?.status === 401 || error?.message?.includes('未提供认证信息') || error?.message?.includes('Unauthorized')) {
      return null
    }
    // 其他错误才输出日志
    console.error('Failed to load current project from DB:', error)
  }
  return null
}

/**
 * 保存当前项目到数据库
 */
const saveCurrentProjectToDB = async (projectId: number | null) => {
  try {
    await authApi.updateCurrentProject(projectId)
  } catch (error: any) {
    // 如果是未授权错误（401），静默处理，不输出错误
    if (error?.response?.status === 401 || error?.message?.includes('未提供认证信息') || error?.message?.includes('Unauthorized')) {
      return // 静默返回，不抛出错误
    }
    // 其他错误才输出日志并抛出
    console.error('Failed to save current project to DB:', error)
    throw error
  }
}

/**
 * 加载项目列表
 */
const loadProjects = async (): Promise<any[]> => {
  // 先检查是否有 token，避免不必要的 API 调用
  if (!tokenManager.hasToken()) {
    return []
  }
  
  try {
    const projects = await projectApi.getProjects()
    projectsCache.value = projects
    return projects
  } catch (error: any) {
    // 如果是未授权错误（401），静默处理，不输出错误
    if (error?.response?.status === 401 || error?.message?.includes('未提供认证信息') || error?.message?.includes('Unauthorized')) {
      return []
    }
    // 其他错误才输出日志
    console.error('Failed to load projects:', error)
    return []
  }
}

/**
 * 初始化：从数据库恢复项目上下文
 */
let initPromise: Promise<void> | null = null
const initProjectContext = async () => {
  const project = await loadCurrentProjectFromDB()
  if (project) {
    currentProject.value = project
  }
}

// 初始化（异步）
initPromise = initProjectContext()

export function useProjectContext() {
  /**
   * 确保项目上下文已初始化
   */
  const ensureInitialized = async () => {
    if (initPromise) {
      await initPromise
    } else {
      // 如果初始化还没开始，立即开始
      initPromise = initProjectContext()
      await initPromise
    }
  }
  /**
   * 设置当前项目（单选模式）
   */
  const setCurrentProject = async (projectId: number | null) => {
    if (!projectId) {
      currentProject.value = null
      await saveCurrentProjectToDB(null)
      // 触发项目切换事件
      window.dispatchEvent(new CustomEvent('project:changed', { detail: { project: null } }))
      return
    }

    // 确保项目列表已加载
    if (projectsCache.value.length === 0) {
      await loadProjects()
    }

    // 从缓存中查找项目
    const project = projectsCache.value.find(p => p.id === projectId)
    if (project) {
      const context: ProjectContext = {
        id: project.id,
        name: project.name,
        description: project.description
      }
      currentProject.value = context
      await saveCurrentProjectToDB(projectId)
      
      // 触发项目切换事件，通知所有页面刷新数据
      window.dispatchEvent(new CustomEvent('project:changed', { detail: { project: context } }))
    } else {
      console.error(`Project with id ${projectId} not found`)
      ElMessage.error('项目不存在')
    }
  }

  /**
   * 清除当前项目（取消项目过滤）
   */
  const clearCurrentProject = () => {
    setCurrentProject(null)
  }

  /**
   * 获取当前项目ID（用于API调用）
   */
  const getCurrentProjectId = computed(() => {
    return currentProject.value?.id || null
  })

  /**
   * 获取当前项目名称（用于显示）
   */
  const getCurrentProjectName = computed(() => {
    return currentProject.value?.name || null
  })

  /**
   * 检查是否已选择项目
   */
  const hasProjectSelected = computed(() => {
    return currentProject.value !== null
  })

  /**
   * 获取项目列表
   * 如果选中了项目，只返回选中的项目；否则返回所有项目
   */
  const getProjects = async (): Promise<any[]> => {
    if (projectsCache.value.length === 0) {
      await loadProjects()
    }
    
    // 如果选中了项目，只返回选中的项目
    if (currentProject.value) {
      const selectedProject = projectsCache.value.find(p => p.id === currentProject.value!.id)
      return selectedProject ? [selectedProject] : []
    }
    
    // 否则返回所有项目
    return projectsCache.value
  }
  
  /**
   * 获取所有项目列表（不受当前项目过滤影响）
   */
  const getAllProjects = async (): Promise<any[]> => {
    if (projectsCache.value.length === 0) {
      await loadProjects()
    }
    return projectsCache.value
  }

  /**
   * 刷新项目列表和当前项目
   */
  const refreshProjects = async () => {
    await loadProjects()
    // 重新加载当前项目
    const project = await loadCurrentProjectFromDB()
    if (project) {
      currentProject.value = project
    } else {
      currentProject.value = null
    }
  }

  /**
   * 监听项目切换事件
   */
  const onProjectChanged = (callback: (project: ProjectContext | null) => void) => {
    const handler = (event: CustomEvent) => {
      callback(event.detail.project || null)
    }
    window.addEventListener('project:changed', handler as EventListener)
    
    // 返回清理函数
    return () => {
      window.removeEventListener('project:changed', handler as EventListener)
    }
  }

  // 兼容多选API（为了向后兼容）
  const getSelectedProjectIds = computed(() => {
    return currentProject.value ? [currentProject.value.id] : []
  })

  const hasProjectsSelected = computed(() => {
    return hasProjectSelected.value
  })

  const setSelectedProjects = async (projectIds: number[]) => {
    if (projectIds.length === 0) {
      await setCurrentProject(null)
    } else {
      await setCurrentProject(projectIds[0]) // 单选模式，只取第一个
    }
  }

  return {
    currentProject: computed(() => currentProject.value),
    selectedProjects: computed(() => currentProject.value ? [currentProject.value] : []),
    setCurrentProject,
    setSelectedProjects,
    clearCurrentProject,
    getCurrentProjectId,
    getCurrentProjectName,
    hasProjectSelected,
    hasProjectsSelected,
    getSelectedProjectIds,
    getProjects,
    getAllProjects,
    refreshProjects,
    onProjectChanged,
    ensureInitialized
  }
}
