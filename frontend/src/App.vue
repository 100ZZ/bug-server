<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 左侧边栏 -->
      <el-aside class="app-sidebar" width="260px">
        <div class="sidebar-content">
          <!-- Logo 区域 -->
          <div class="logo-section">
            <div class="logo">
              <el-icon :size="24" class="logo-icon"><Warning /></el-icon>
              <h1>质量管理系统</h1>
            </div>
            <el-tooltip
              effect="dark"
              placement="right"
              :show-after="300"
            >
              <template #content>
                <div style="max-width: 300px; line-height: 1.6;">
                  如果有任何问题，
                  <a 
                    href="https://di-matrix.feishu.cn/docx/TsgUdaWCnojvWxxnNkMc9GsZn3f" 
                    target="_blank"
                    style="color: #409eff; text-decoration: underline;"
                  >
                    提交问题
                  </a>
                </div>
              </template>
              <el-icon :size="16" class="help-icon">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>

          <!-- 项目选择器 -->
          <div class="project-selector-section">
            <SidebarProjectSelector />
          </div>

          <!-- 菜单区域 -->
          <div class="menu-section">
            <el-menu
              :default-active="activeMenu"
              :active-text-color="'#ffffff'"
              mode="vertical"
              :unique-opened="false"
              @select="handleMenuSelect"
              ref="menuRef"
              :router="false"
            >
              <el-sub-menu index="/projects">
                <template #title>
                  <el-icon><FolderOpened /></el-icon>
                  <span>项目协同</span>
                </template>
                <el-menu-item index="/projects/list">
                  <span>项目管理</span>
                </el-menu-item>
                <el-menu-item index="/projects/sprints">
                  <span>迭代管理</span>
                </el-menu-item>
              </el-sub-menu>
              <el-sub-menu index="/testcases">
                <template #title>
                  <el-icon><Document /></el-icon>
                  <span>用例管理</span>
                </template>
                <el-menu-item index="/testcases/detail">
                  <span>用例详情</span>
                </el-menu-item>
                <el-menu-item index="/testcases/review">
                  <span>用例评审</span>
                </el-menu-item>
              </el-sub-menu>
              <el-sub-menu index="/apitest">
                <template #title>
                  <el-icon><Connection /></el-icon>
                  <span>测试管理</span>
                </template>
                <el-menu-item index="/apitest/api">
                  <span>接口测试</span>
                </el-menu-item>
                <el-menu-item index="/apitest/flow">
                  <span>流程测试</span>
                </el-menu-item>
                <el-menu-item index="/apitest/task">
                  <span>测试任务</span>
                </el-menu-item>
                <el-menu-item index="/apitest/codescan">
                  <span>代码扫描</span>
                </el-menu-item>
                <el-menu-item index="/apitest/files">
                  <span>文件管理</span>
                </el-menu-item>
              </el-sub-menu>
              <el-menu-item index="/bugs">
                <el-icon><List /></el-icon>
                <span>缺陷管理</span>
              </el-menu-item>
              <el-menu-item index="/api-environments">
                <el-icon><Setting /></el-icon>
                <span>环境管理</span>
              </el-menu-item>
              <el-menu-item index="/statistics">
                <el-icon><DataAnalysis /></el-icon>
                <span>统计分析</span>
              </el-menu-item>
              <el-menu-item index="/models">
                <el-icon><Cpu /></el-icon>
                <span>模型管理</span>
              </el-menu-item>
              <el-menu-item index="/users">
                <el-icon><User /></el-icon>
                <span>用户管理</span>
              </el-menu-item>
            </el-menu>
          </div>

          <!-- 用户信息区域 -->
          <div class="user-section">
            <template v-if="!isLoggedIn">
              <el-button type="primary" class="login-button" @click="showLoginDialog">
                <el-icon><User /></el-icon>
                <span>登录</span>
              </el-button>
            </template>
            <template v-else>
              <el-dropdown @command="handleUserCommand" trigger="click" class="user-dropdown" popper-class="user-dropdown-popper">
                <div class="user-info">
                  <div class="user-avatar">
                    <el-icon :size="24"><User /></el-icon>
                  </div>
                  <div class="user-details">
                    <div class="user-name">{{ currentUser.display_name || currentUser.username }}</div>
                    <div class="user-role">{{ getRoleName }}</div>
                  </div>
                  <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      <span>个人信息</span>
                    </el-dropdown-item>
                    <el-dropdown-item command="changePassword">
                      <el-icon><Lock /></el-icon>
                      <span>修改密码</span>
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      <span>退出登录</span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </div>
        </div>
      </el-aside>

      <!-- 主内容区 -->
      <el-container class="main-container">
        <el-main class="app-main">
          <div class="main-content">
            <router-view v-slot="{ Component }">
              <transition name="fade-slide" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 登录对话框 -->
    <el-dialog v-model="loginDialogVisible" width="400px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">用户登录</span>
          <span class="dialog-description">请输入您的用户名和密码进行登录</span>
        </div>
      </template>
      <el-form :model="loginForm" label-width="70px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" @keyup.enter="handleLogin" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="loginDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleLogin" :loading="loginLoading">登录</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" width="400px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">修改密码</span>
          <span class="dialog-description">修改您的登录密码，请妥善保管新密码</span>
        </div>
      </template>
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 个人信息对话框 -->
    <el-dialog v-model="profileDialogVisible" width="500px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">个人信息</span>
          <span class="dialog-description">查看您的账户基本信息</span>
        </div>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="显示名称">{{ currentUser.display_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentUser.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ getRoleName }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="profileDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { List, DataAnalysis, FolderOpened, User, Warning, Document, Connection, Setting, ArrowDown, Lock, SwitchButton, Cpu, QuestionFilled } from '@element-plus/icons-vue'
import { usePermissions } from './composables/usePermissions'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as authApi from './api/auth'
import { tokenManager } from './utils/token'
import SidebarProjectSelector from './components/SidebarProjectSelector.vue'

const router = useRouter()
const route = useRoute()
const activeMenu = ref(route.path)
const menuRef = ref()

const { currentUser, setCurrentUser, clearCurrentUser, isLoggedIn, getRoleName, refreshUser } = usePermissions()

// 权限映射
const rolePermissions: Record<string, any> = {
  admin: {
    projects: ['read', 'create', 'update', 'delete'],
    users: ['read', 'create', 'update', 'delete'],
    bugs: ['read', 'create', 'update', 'delete'],
    comments: ['read', 'create', 'update', 'delete'],
    statistics: ['read'],
    models: ['read', 'create', 'update', 'delete']
  },
  product: {
    projects: ['read', 'create', 'update', 'delete'],
    users: ['read'],
    bugs: ['read', 'create', 'update', 'delete'],
    comments: ['read', 'create', 'update', 'delete'],
    statistics: ['read'],
    models: ['read']
  },
  developer: {
    projects: ['read', 'create', 'update', 'delete'],
    users: ['read'],
    bugs: ['read', 'create', 'update', 'delete'],
    comments: ['read', 'create', 'update', 'delete'],
    statistics: ['read'],
    models: ['read']
  },
  tester: {
    projects: ['read', 'create', 'update', 'delete'],
    users: ['read'],
    bugs: ['read', 'create', 'update', 'delete'],
    comments: ['read', 'create', 'update', 'delete'],
    statistics: ['read'],
    models: ['read']
  },
  guest: {
    projects: ['read'],
    users: ['read'],
    bugs: ['read'],
    comments: ['read'],
    statistics: ['read'],
    models: ['read']
  }
}

const roleNames: Record<string, string> = {
  admin: '管理员',
  product: '产品',
  developer: '开发',
  tester: '测试',
  guest: '游客'
}

// 登录对话框
const loginDialogVisible = ref(false)
const loginLoading = ref(false)
const loginForm = reactive({
  username: '',
  password: ''
})

// 修改密码对话框
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 个人信息对话框
const profileDialogVisible = ref(false)

// 登录后要跳转的路由
const pendingRoute = ref<string | null>(null)

watch(() => route.path, (newPath) => {
  // 直接使用实际路径，让子菜单项能够正确选中
  activeMenu.value = newPath
  // 确保菜单组件更新选中状态
  nextTick(() => {
    if (menuRef.value) {
      menuRef.value.activeIndex = newPath
    }
  })
})

// 监听 401 未授权事件
const handleUnauthorized = () => {
  clearCurrentUser()
  showLoginDialog()
}

// 监听需要认证的路由访问事件
const handleAuthRequired = (event: Event) => {
  const customEvent = event as CustomEvent<{ route?: string }>
  pendingRoute.value = customEvent.detail?.route || null
  showLoginDialog()
}

onMounted(async () => {
  window.addEventListener('auth:unauthorized', handleUnauthorized)
  window.addEventListener('auth:required', handleAuthRequired as EventListener)
  
  // 应用启动时，从 localStorage 恢复 token 并加载用户信息
  if (tokenManager.hasToken()) {
    try {
      await refreshUser()
    } catch (error) {
      console.error('Failed to load user on mount:', error)
      // 如果 token 无效，清除它
      tokenManager.clearToken()
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('auth:unauthorized', handleUnauthorized)
  window.removeEventListener('auth:required', handleAuthRequired as EventListener)
})

const handleMenuSelect = (index: string) => {
  // 更新 activeMenu 为选中的菜单项路径
  activeMenu.value = index
  try {
    router.push(index).catch((err) => {
      // 忽略导航重复的错误
      if (err.name !== 'NavigationDuplicated') {
        console.error('Navigation error:', err)
      }
    })
  } catch (error) {
    console.error('Menu select error:', error)
  }
}

const showLoginDialog = () => {
  loginForm.username = ''
  loginForm.password = ''
  loginDialogVisible.value = true
}

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loginLoading.value = true
  try {
    const response: any = await authApi.login(loginForm)
    
    // 设置用户信息和权限（包含 token）
    const user = response.user
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
    await setCurrentUser({
      user_id: user.id,
      username: user.username,
      email: user.email,
      role: primaryRole,
      role_name: roleNames[primaryRole] || primaryRole,
      permissions: rolePermissions[primaryRole] || rolePermissions.guest,
      token: response.access_token  // 添加 token 到用户对象
    })
    
    ElMessage.success('登录成功')
    loginDialogVisible.value = false
    
    // 如果有待跳转的路由，登录后跳转
    if (pendingRoute.value) {
      router.push(pendingRoute.value)
      pendingRoute.value = null
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    const errorMessage = error.response?.data?.detail || error.message || '登录失败，请检查用户名和密码'
    ElMessage.error(errorMessage)
  } finally {
    loginLoading.value = false
  }
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      profileDialogVisible.value = true
      break
    case 'changePassword':
      passwordForm.old_password = ''
      passwordForm.new_password = ''
      passwordForm.confirm_password = ''
      passwordDialogVisible.value = true
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = async () => {
  ElMessageBox.confirm('确定退出登录吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearCurrentUser()
      ElMessage.success('已退出登录')
    }
  }).catch(() => {})
}

const handleChangePassword = async () => {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    ElMessage.warning('请填写完整信息')
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }

  if (passwordForm.new_password.length < 6) {
    ElMessage.warning('新密码长度至少为6位')
    return
  }

  passwordLoading.value = true
  try {
    await authApi.changePassword(currentUser.value.user_id, {
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    
    ElMessage.success('密码修改成功，请重新登录')
    passwordDialogVisible.value = false
    
    // 退出登录
    setTimeout(() => {
      clearCurrentUser()
      showLoginDialog()
    }, 1000)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '密码修改失败')
  } finally {
    passwordLoading.value = false
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

#app {
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  min-height: 100vh;
}

.layout-container {
  height: 100%;
  display: flex;
}

/* ========== 左侧边栏样式 ========== */
.app-sidebar {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  box-shadow: 4px 0 30px rgba(102, 126, 234, 0.15);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow: hidden;
  z-index: 1000;
  transition: all 0.3s ease;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.sidebar-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  pointer-events: none;
}

/* Logo 区域 */
.logo-section {
  padding: 32px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  z-index: 1;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.help-icon {
  position: absolute;
  bottom: 8px;
  right: 8px;
  color: rgba(255, 255, 255, 0.8);
  cursor: help;
  transition: all 0.3s ease;
}

.help-icon:hover {
  color: #ffffff;
  transform: scale(1.1);
}

.logo:hover {
  transform: translateX(4px);
}

.logo-icon {
  color: #ffffff !important;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.logo h1 {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  letter-spacing: 0.5px;
  line-height: 1.4;
  white-space: nowrap;
}

/* 项目选择器区域 */
.project-selector-section {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  z-index: 1;
  background: rgba(0, 0, 0, 0.1);
}

/* 菜单区域 */
.menu-section {
  flex: 1;
  padding: 20px 16px;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  z-index: 1;
}

.menu-section::-webkit-scrollbar {
  width: 4px;
}

.menu-section::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
}

.menu-section::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.menu-section::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 主内容区 */
.main-container {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-main {
  padding: 24px;
  overflow-y: auto;
  background: transparent;
  position: relative;
  flex: 1;
}

.app-main::-webkit-scrollbar {
  width: 8px;
}

.app-main::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.app-main::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 4px;
}

.app-main::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

.main-content {
  position: relative;
  z-index: 1;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 路由过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

/* ========== 侧边栏菜单样式 ========== */
.app-sidebar .el-menu {
  border: none !important;
  background: transparent !important;
}

.app-sidebar .el-menu-item {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85) !important;
  border-radius: 12px;
  margin: 6px 0;
  padding: 0 20px !important;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.app-sidebar .el-menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: transparent;
  transform: translateX(-4px);
  transition: transform 0.3s ease;
  border-radius: 0 4px 4px 0;
}

.app-sidebar .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateX(4px);
}

.app-sidebar .el-menu-item:hover::before {
  transform: translateX(0);
}

.app-sidebar .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.25) !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
}

.app-sidebar .el-menu-item.is-active::before {
  transform: translateX(0);
  background: transparent;
}

.app-sidebar .el-menu-item .el-icon {
  margin-right: 12px;
  font-size: 18px;
}

/* 子菜单样式 */
.app-sidebar .el-sub-menu {
  margin: 6px 0;
}

.app-sidebar .el-sub-menu__title {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85) !important;
  border-radius: 12px;
  padding: 0 20px !important;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.app-sidebar .el-sub-menu__title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: transparent;
  transform: translateX(-4px);
  transition: transform 0.3s ease;
  border-radius: 0 4px 4px 0;
}

.app-sidebar .el-sub-menu__title:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateX(4px);
}

.app-sidebar .el-sub-menu__title:hover::before {
  transform: translateX(0);
}

/* 父菜单不应该有选中状态，移除 is-active 样式 */
.app-sidebar .el-sub-menu.is-active > .el-sub-menu__title {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.85) !important;
  font-weight: normal !important;
}

.app-sidebar .el-sub-menu.is-active > .el-sub-menu__title::before {
  transform: translateX(-4px);
  background: transparent;
}

.app-sidebar .el-sub-menu__title .el-icon {
  margin-right: 12px;
  font-size: 18px;
}

.app-sidebar .el-sub-menu__icon-arrow {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* 子菜单展开内容 */
.app-sidebar .el-menu--inline {
  background: rgba(0, 0, 0, 0.1) !important;
  border-radius: 8px;
  margin: 4px 0;
  padding: 4px 0;
}

.app-sidebar .el-menu--inline .el-menu-item {
  padding-left: 52px !important;
  height: 42px;
  line-height: 42px;
  font-size: 14px;
}

.app-sidebar .el-menu--inline .el-menu-item::before {
  display: none;
}

/* ========== 用户信息区域样式 ========== */
.user-section {
  padding: 20px 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  z-index: 1;
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: #ffffff !important;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-button:hover {
  background: rgba(255, 255, 255, 0.3) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.user-dropdown {
  width: 100%;
  position: relative;
}


.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.user-info:hover .dropdown-icon {
  transform: translateY(2px);
}

/* 用户下拉菜单样式 - 与左侧透明紫色样式一致 */
.user-dropdown-popper {
  width: 228px !important; /* 260px sidebar - 32px padding (16px * 2) = 228px */
  min-width: 228px !important;
  max-width: 228px !important;
  padding: 0 !important;
  left: 16px !important; /* 对齐到sidebar左侧padding */
}

.user-dropdown-popper .el-dropdown-menu {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
  border: none !important;
  padding: 8px !important;
  backdrop-filter: blur(10px);
  width: 100% !important;
  margin-top: 0 !important;
}

.user-dropdown-popper .el-dropdown-menu__item {
  border-radius: 8px !important;
  padding: 10px 16px !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  transition: all 0.3s ease !important;
  color: rgba(255, 255, 255, 0.85) !important;
  margin: 2px 0 !important;
  background: transparent !important;
}

.user-dropdown-popper .el-dropdown-menu__item:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateX(4px);
}

.user-dropdown-popper .el-dropdown-menu__item.is-divided {
  border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
  margin-top: 8px !important;
  padding-top: 12px !important;
}

.user-dropdown-popper .el-dropdown-menu__item .el-icon {
  font-size: 16px !important;
  color: rgba(255, 255, 255, 0.85) !important;
}

/* 确保箭头也是紫色，去掉白色边缘 */
.user-dropdown-popper .el-popper__arrow::before {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
}

/* 去掉下拉菜单的白色边缘 */
.user-dropdown-popper {
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
}

.user-dropdown-popper .el-dropdown-menu {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
}

/* 确保 popper 容器本身没有边框 */
.user-dropdown-popper.el-popper {
  border: none !important;
  background: transparent !important;
}

/* 去掉所有可能的白色边框和轮廓 */
.user-dropdown-popper * {
  border-color: transparent !important;
  outline: none !important;
}

.user-dropdown-popper .el-dropdown-menu,
.user-dropdown-popper .el-dropdown-menu__item {
  border: none !important;
  outline: none !important;
}

/* 对话框样式美化 - 只保留圆角和阴影 */
:deep(.el-dialog) {
  border-radius: 16px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15) !important;
}

:deep(.el-dialog__header) {
  background: transparent !important;
  border-bottom: none !important;
}

:deep(.el-dialog__footer) {
  background: transparent !important;
  border-top: none !important;
}

/* 表单样式美化 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #495057;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #667eea inset;
}

:deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 1px #667eea inset;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

/* 对话框中的所有按钮样式 - 使用更具体的选择器 */
:deep(.el-dialog .el-button),
:deep(.el-dialog__footer .el-button),
:deep(.el-dialog__footer button),
:deep(.el-dialog button.el-button) {
  border-radius: 8px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

:deep(.el-dialog .el-button--primary),
:deep(.el-dialog__footer .el-button--primary),
:deep(.el-dialog__footer button.el-button--primary),
:deep(.el-dialog button.el-button--primary),
:deep(.el-dialog .el-button[type="primary"]),
:deep(.el-dialog__footer .el-button[type="primary"]) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  background-color: transparent !important;
  border: none !important;
  border-color: transparent !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
  color: #ffffff !important;
}

:deep(.el-dialog .el-button--primary:hover),
:deep(.el-dialog__footer .el-button--primary:hover),
:deep(.el-dialog__footer button.el-button--primary:hover),
:deep(.el-dialog button.el-button--primary:hover),
:deep(.el-dialog .el-button[type="primary"]:hover),
:deep(.el-dialog__footer .el-button[type="primary"]:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  background-color: transparent !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
  color: #ffffff !important;
}

:deep(.el-dialog .el-button--primary:focus),
:deep(.el-dialog__footer .el-button--primary:focus) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  background-color: transparent !important;
  color: #ffffff !important;
}

:deep(.el-dialog .el-button:not(.el-button--primary)),
:deep(.el-dialog__footer .el-button:not(.el-button--primary)) {
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
}

:deep(.el-dialog .el-button:not(.el-button--primary):hover),
:deep(.el-dialog__footer .el-button:not(.el-button--primary):hover) {
  transform: translateY(-2px) !important;
}

/* ElMessageBox 确认框按钮样式 - 只保留按钮样式 */
:deep(.el-message-box) {
  border-radius: 16px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15) !important;
  overflow: hidden !important;
}

:deep(.el-message-box__header) {
  background: transparent !important;
  border-bottom: none !important;
}

:deep(.el-message-box__btns) {
  background: transparent !important;
  border-top: none !important;
}

:deep(.el-message-box__btns .el-button),
:deep(.el-message-box__btns button),
:deep(.el-message-box__btns button.el-button) {
  border-radius: 8px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

:deep(.el-message-box__btns .el-button--primary),
:deep(.el-message-box__btns button.el-button--primary),
:deep(.el-message-box__btns .el-button[type="primary"]) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  background-color: transparent !important;
  border: none !important;
  border-color: transparent !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
  color: #ffffff !important;
}

:deep(.el-message-box__btns .el-button--primary:hover),
:deep(.el-message-box__btns button.el-button--primary:hover),
:deep(.el-message-box__btns .el-button[type="primary"]:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  background-color: transparent !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
  color: #ffffff !important;
}

:deep(.el-message-box__btns .el-button--primary:focus) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  background-color: transparent !important;
  color: #ffffff !important;
}

:deep(.el-message-box__btns .el-button:not(.el-button--primary)) {
  border-radius: 8px !important;
  transition: all 0.3s ease !important;
}

:deep(.el-message-box__btns .el-button:not(.el-button--primary):hover) {
  transform: translateY(-2px) !important;
}

/* 确保操作栏的 link 按钮没有背景色 */
:deep(.el-button.is-link) {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

:deep(.el-button.is-link:hover) {
  background: transparent !important;
}

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

/* 个人信息对话框中的描述列表样式 */
:deep(.el-dialog .el-descriptions) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-dialog .el-descriptions__header) {
  margin-bottom: 16px;
}

:deep(.el-dialog .el-descriptions__table) {
  border-radius: 8px;
}

:deep(.el-dialog .el-descriptions__label) {
  font-weight: 500;
  color: #495057;
  background: #f8f9fa;
}

:deep(.el-dialog .el-descriptions__content) {
  color: #212529;
}

/* 对话框标题和说明样式 */
.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.dialog-description {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}
</style>


