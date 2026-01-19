/**
 * Token 管理工具
 * 使用 localStorage 持久化存储 token，刷新页面后仍可恢复登录状态
 */

const TOKEN_KEY = 'bug_server_access_token'

export const tokenManager = {
  /**
   * 设置 token
   */
  setToken(token: string) {
    try {
      localStorage.setItem(TOKEN_KEY, token)
    } catch (error) {
      console.error('Failed to save token to localStorage:', error)
    }
  },

  /**
   * 获取 token
   */
  getToken(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY)
    } catch (error) {
      console.error('Failed to get token from localStorage:', error)
      return null
    }
  },

  /**
   * 清除 token
   */
  clearToken() {
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch (error) {
      console.error('Failed to remove token from localStorage:', error)
    }
  },

  /**
   * 检查是否有 token
   */
  hasToken(): boolean {
    return this.getToken() !== null
  }
}

