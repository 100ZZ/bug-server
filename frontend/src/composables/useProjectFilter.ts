/**
 * 项目过滤辅助 Composable
 * 用于简化页面中项目过滤的应用（单选模式）
 */
import { computed, onMounted, onUnmounted } from 'vue'
import { useProjectContext } from './useProjectContext'

export function useProjectFilter() {
  const {
    getCurrentProjectId,
    getCurrentProjectName,
    hasProjectSelected
  } = useProjectContext()

  /**
   * 应用项目过滤到 API 参数
   * @param params 原始 API 参数对象
   * @returns 添加了项目过滤后的参数对象
   */
  const applyProjectFilter = (params: any = {}) => {
    const projectId = getCurrentProjectId.value
    if (hasProjectSelected.value && projectId) {
      // 使用 project_id 参数（单选模式）
      params.project_id = projectId
    }
    return params
  }

  /**
   * 获取应该使用的项目ID（用于表单默认值）
   * @param fallbackProjectId 如果没有选择项目上下文时的备用项目ID
   * @returns 项目ID
   */
  const getProjectIdForForm = (fallbackProjectId?: number): number | null => {
    const projectId = getCurrentProjectId.value
    if (hasProjectSelected.value && projectId) {
      return projectId
    }
    return fallbackProjectId || null
  }

  /**
   * 监听项目切换并执行回调
   * @param callback 项目切换时的回调函数
   * @returns 清理函数
   */
  const watchProjectChange = (callback: () => void) => {
    const handler = () => {
      callback()
    }
    window.addEventListener('project:changed', handler)
    
    return () => {
      window.removeEventListener('project:changed', handler)
    }
  }

  return {
    getCurrentProjectId,
    getCurrentProjectName,
    hasProjectSelected,
    applyProjectFilter,
    getProjectIdForForm,
    watchProjectChange
  }
}
