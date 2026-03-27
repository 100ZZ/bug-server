<template>
  <div id="app">
    <el-container class="layout-container">
      <!-- 左侧边栏 -->
      <el-aside class="app-sidebar" width="260px">
        <div class="sidebar-content">
          <!-- 顶部区域：品牌 + 项目切换 -->
          <div class="sidebar-header">
            <!-- 品牌标识 -->
            <div class="brand-section">
              <div class="brand-logo">
                <el-icon :size="24"><DataAnalysis /></el-icon>
              </div>
              <span class="brand-title">质量管理系统</span>
            </div>
            
            <!-- 项目切换器 -->
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
              <!-- 公共菜单：始终显示 -->
              <el-menu-item index="/projects/list">
                <el-icon><FolderOpened /></el-icon>
                <span>项目管理</span>
              </el-menu-item>
              
              <!-- 未选择项目时的提示 -->
              <div v-if="!hasProjectSelected" class="project-hint-section">
                <div class="project-hint-box">
                  <el-icon :size="24"><InfoFilled /></el-icon>
                  <span>请先选择项目</span>
                  <span class="hint-sub">选择项目后显示更多功能</span>
                </div>
              </div>
              
              <!-- 项目相关菜单：选择项目后显示 -->
              <template v-if="hasProjectSelected">
                <!-- 项目协同 - 右侧弹出 -->
                <div class="menu-item-with-popup" ref="projectsMenuRef">
                  <div class="menu-item-trigger" :class="{ 'is-active': isSubMenuActive('projects') }" @click="toggleSubMenu('projects', $event)">
                    <el-icon><Connection /></el-icon>
                    <span>项目协同</span>
                    <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                  </div>
                </div>

                <!-- 用例管理 - 右侧弹出 -->
                <div class="menu-item-with-popup" ref="testcasesMenuRef">
                  <div class="menu-item-trigger" :class="{ 'is-active': isSubMenuActive('testcases') }" @click="toggleSubMenu('testcases', $event)">
                    <el-icon><Document /></el-icon>
                    <span>用例管理</span>
                    <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                  </div>
                </div>

                <el-menu-item index="/bugs">
                  <el-icon><List /></el-icon>
                  <span>缺陷管理</span>
                </el-menu-item>
                <el-menu-item index="/api-environments">
                  <el-icon><Setting /></el-icon>
                  <span>配置管理</span>
                </el-menu-item>
                <el-menu-item index="/statistics">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>统计分析</span>
                </el-menu-item>

                <!-- 测试管理 - 右侧弹出 -->
                <div class="menu-item-with-popup" ref="apitestMenuRef">
                  <div class="menu-item-trigger" :class="{ 'is-active': isSubMenuActive('apitest') }" @click="toggleSubMenu('apitest', $event)">
                    <el-icon><Connection /></el-icon>
                    <span>测试管理</span>
                    <el-icon class="arrow-icon"><ArrowRight /></el-icon>
                  </div>
                </div>
              </template>
              
              <!-- 公共菜单：始终显示 -->
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
              <div class="user-menu-wrapper" ref="userMenuRef">
                <div class="user-info" @click="toggleUserMenu">
                  <div class="user-avatar">
                    <el-icon :size="20"><User /></el-icon>
                  </div>
                  <div class="user-content">
                    <span class="user-display-name">{{ currentUser.display_name || currentUser.username }}</span>
                    <span class="user-role-badge">{{ getRoleName }}</span>
                  </div>
                  <el-icon class="dropdown-icon" :class="{ 'is-open': isUserMenuOpen }"><ArrowRight /></el-icon>
                </div>
              </div>
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

    <!-- 子菜单弹出框 - 使用 Teleport 渲染到 body -->
    <Teleport to="body">
      <Transition name="popup-slide">
        <div v-if="openSubMenu" class="submenu-popup-global" :style="subMenuStyle" @click.stop>
          <!-- 项目协同 -->
          <template v-if="openSubMenu === 'projects'">
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/projects/sprints' }" @click="navigateTo('/projects/sprints')">
              <el-icon><Calendar /></el-icon>
              <span>迭代管理</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/projects/requirements' }" @click="navigateTo('/projects/requirements')">
              <el-icon><Sunny /></el-icon>
              <span>需求管理</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/projects/worktasks' }" @click="navigateTo('/projects/worktasks')">
              <el-icon><Memo /></el-icon>
              <span>任务管理</span>
            </div>
          </template>
          <!-- 用例管理 -->
          <template v-if="openSubMenu === 'testcases'">
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/testcases/detail' }" @click="navigateTo('/testcases/detail')">
              <el-icon><Document /></el-icon>
              <span>用例详情</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/testcases/review' }" @click="navigateTo('/testcases/review')">
              <el-icon><Finished /></el-icon>
              <span>用例评审</span>
            </div>
          </template>
          <!-- 测试管理 -->
          <template v-if="openSubMenu === 'apitest'">
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/apitest/api' }" @click="navigateTo('/apitest/api')">
              <el-icon><Connection /></el-icon>
              <span>接口测试</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/apitest/flow' }" @click="navigateTo('/apitest/flow')">
              <el-icon><Share /></el-icon>
              <span>流程测试</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/apitest/task' }" @click="navigateTo('/apitest/task')">
              <el-icon><List /></el-icon>
              <span>测试任务</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/apitest/codescan' }" @click="navigateTo('/apitest/codescan')">
              <el-icon><View /></el-icon>
              <span>代码扫描</span>
            </div>
            <div class="submenu-item" :class="{ 'is-active': activeMenu === '/apitest/files' }" @click="navigateTo('/apitest/files')">
              <el-icon><Folder /></el-icon>
              <span>文件管理</span>
            </div>
          </template>
        </div>
      </Transition>

      <!-- 用户菜单弹出框 -->
      <Transition name="popup-slide">
        <div v-if="isUserMenuOpen" class="user-menu-popup" :style="userMenuStyle" @click.stop>
          <div class="submenu-item" @click="handleUserMenuCommand('profile')">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </div>
          <div class="submenu-item" @click="handleUserMenuCommand('changePassword')">
            <el-icon><Lock /></el-icon>
            <span>修改密码</span>
          </div>
          <div class="submenu-divider"></div>
          <div class="submenu-item logout-item" @click="handleUserMenuCommand('logout')">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { List, DataAnalysis, FolderOpened, User, Warning, Document, Connection, Setting, ArrowDown, ArrowRight, Lock, SwitchButton, Cpu, QuestionFilled, InfoFilled, Calendar, Sunny, Memo, Finished, Share, View, Folder } from '@element-plus/icons-vue'
import { usePermissions } from './composables/usePermissions'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as authApi from './api/auth'
import { tokenManager } from './utils/token'
import SidebarProjectSelector from './components/SidebarProjectSelector.vue'
import { useProjectContext } from './composables/useProjectContext'

const router = useRouter()

// 项目上下文
const { hasProjectSelected, getCurrentProjectName } = useProjectContext()
const route = useRoute()
const activeMenu = ref('')  // 默认不选中任何项
const menuRef = ref()

const { currentUser, setCurrentUser, clearCurrentUser, isLoggedIn, getRoleName, refreshUser } = usePermissions()

// 子菜单控制
const openSubMenu = ref<string | null>(null)
const subMenuStyle = ref<{ top: string; left: string }>({
  top: '0px',
  left: '270px'
})

// 用户菜单
const userMenuRef = ref()
const isUserMenuOpen = ref(false)
const userMenuStyle = ref<{ bottom: string; left: string }>({
  bottom: '0px',
  left: '270px'
})

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
  if (isUserMenuOpen.value) {
    // 关闭其他弹出框
    openSubMenu.value = null
    window.dispatchEvent(new CustomEvent('userMenu:opened'))
    // 计算位置，下边缘对齐
    if (userMenuRef.value) {
      const rect = userMenuRef.value.getBoundingClientRect()
      // 使用 bottom 定位，从视窗底部计算
      const bottomFromViewport = window.innerHeight - rect.bottom
      userMenuStyle.value = {
        bottom: `${bottomFromViewport}px`,
        left: '270px'
      }
    }
  }
}

const handleUserMenuCommand = async (command: string) => {
  isUserMenuOpen.value = false
  if (command === 'profile') {
    profileDialogVisible.value = true
  } else if (command === 'changePassword') {
    passwordDialogVisible.value = true
  } else if (command === 'logout') {
    await handleLogout()
  }
}

const toggleSubMenu = (menu: string, event: MouseEvent) => {
  if (openSubMenu.value === menu) {
    openSubMenu.value = null
  } else {
    // 关闭用户菜单
    isUserMenuOpen.value = false
    // 通知关闭项目选择器
    window.dispatchEvent(new CustomEvent('submenu:opened'))
    // 计算弹出框位置
    const trigger = event.currentTarget as HTMLElement
    const rect = trigger.getBoundingClientRect()
    subMenuStyle.value = {
      top: `${rect.top}px`,
      left: '270px'
    }
    openSubMenu.value = menu
  }
}

// 监听项目选择器打开事件，关闭子菜单
const handleProjectSelectorOpened = () => {
  openSubMenu.value = null
  isUserMenuOpen.value = false
}

const isSubMenuActive = (prefix: string) => {
  const prefixMap: Record<string, string[]> = {
    'projects': ['/projects/sprints', '/projects/requirements', '/projects/worktasks'],
    'testcases': ['/testcases/detail', '/testcases/review'],
    'apitest': ['/apitest/api', '/apitest/flow', '/apitest/task', '/apitest/codescan', '/apitest/files']
  }
  return prefixMap[prefix]?.some(path => activeMenu.value === path || activeMenu.value.startsWith(path))
}

const navigateTo = (path: string) => {
  isUserNavigation.value = true
  activeMenu.value = path
  router.push(path)
  openSubMenu.value = null
}

// 点击外部关闭子菜单
const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (!target.closest('.menu-item-with-popup')) {
    openSubMenu.value = null
  }
  if (!target.closest('.user-menu-wrapper') && !target.closest('.user-menu-popup')) {
    isUserMenuOpen.value = false
  }
}

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

// 记录是否是用户主动导航
const isUserNavigation = ref(false)

watch(() => route.path, (newPath) => {
  // 只有用户主动导航时才更新选中状态
  if (isUserNavigation.value) {
    activeMenu.value = newPath
    nextTick(() => {
      if (menuRef.value) {
        menuRef.value.activeIndex = newPath
      }
    })
    isUserNavigation.value = false
  }
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
  window.addEventListener('projectSelector:opened', handleProjectSelectorOpened)
  document.addEventListener('click', handleClickOutside)
  
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
  window.removeEventListener('projectSelector:opened', handleProjectSelectorOpened)
  document.removeEventListener('click', handleClickOutside)
})

const handleMenuSelect = (index: string) => {
  // 标记为用户主动导航
  isUserNavigation.value = true
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
  overflow: visible;
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

/* 侧边栏顶部区域 */
.sidebar-header {
  padding: 20px 16px;
  position: relative;
  z-index: 1;
}

/* 品牌标识区域 */
.brand-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 4px;
  margin-bottom: 20px;
}

.brand-logo {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.brand-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 菜单区域 */
.menu-section {
  flex: 1;
  padding: 16px;
  padding-top: 20px;
  overflow-y: auto;
  overflow-x: visible;
  position: relative;
  z-index: 1;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
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

/* 未选择项目时的提示框 */
.project-hint-section {
  padding: 16px 8px;
  margin: 8px 0;
}

.project-hint-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px dashed rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.85);
  text-align: center;
}

.project-hint-box .el-icon {
  color: rgba(255, 255, 255, 0.7);
}

.project-hint-box span {
  font-size: 14px;
  font-weight: 500;
}

.project-hint-box .hint-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: normal;
}

/* 右侧弹出子菜单 */
.menu-item-with-popup {
  position: relative;
  margin: 6px 0;
}

.menu-item-trigger {
  display: flex;
  align-items: center;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
  border-radius: 12px;
  padding: 0 20px;
  height: 48px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item-trigger .el-icon {
  width: 18px;
  margin-right: 12px;
  font-size: 18px;
  flex-shrink: 0;
}

.menu-item-trigger span {
  flex: 1;
}

.menu-item-trigger .arrow-icon {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-right: 0;
}

.menu-item-trigger:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  transform: translateX(4px);
}

.menu-item-trigger.is-active {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
  font-weight: 600;
}

/* 子菜单弹出框 - 全局固定定位，和项目选择器保持一致 */
.submenu-popup-global {
  position: fixed;
  width: 260px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  padding: 8px;
  z-index: 3000;
}

.submenu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  transition: all 0.2s ease;
  margin: 2px 0;
}

.submenu-item .el-icon {
  width: 26px;
  height: 26px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}

.submenu-item span {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.submenu-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  transform: translateX(4px);
}

.submenu-item:hover .el-icon {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.submenu-item.is-active {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.submenu-item.is-active .el-icon {
  background: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

/* 用户菜单弹出框 */
.user-menu-popup {
  position: fixed;
  width: 260px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
  padding: 8px;
  z-index: 3000;
  top: auto;
}

.submenu-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.15);
  margin: 6px 0;
}

.submenu-item.logout-item:hover {
  background: rgba(255, 100, 100, 0.3);
}

.user-menu-wrapper {
  width: 100%;
}

.dropdown-icon.is-open {
  transform: rotate(90deg);
}

/* 弹出动画 */
.popup-slide-enter-active,
.popup-slide-leave-active {
  transition: all 0.2s ease;
}

.popup-slide-enter-from,
.popup-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
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
  display: flex !important;
  align-items: center !important;
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
  width: 18px;
  margin-right: 12px;
  font-size: 18px;
  flex-shrink: 0;
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
  gap: 10px;
  cursor: pointer;
  padding: 10px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 100%;
  min-height: 56px;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
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

.user-content {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-display-name {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-badge {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.15);
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.dropdown-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.user-info:hover .dropdown-icon {
  color: rgba(255, 255, 255, 0.8);
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


