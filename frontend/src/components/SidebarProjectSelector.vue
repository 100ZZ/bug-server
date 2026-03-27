<template>
  <div class="workspace-selector" ref="containerRef">
    <!-- 项目切换区域 -->
    <div 
      class="workspace-trigger"
      ref="triggerRef"
      :class="{ 'is-active': isDropdownOpen, 'has-project': hasProjectSelected }"
      @click="toggleDropdown"
    >
      <div class="workspace-icon" :class="avatarColorClass">
        <span v-if="hasProjectSelected">{{ projectInitial }}</span>
        <el-icon v-else :size="16"><Grid /></el-icon>
      </div>
      <div class="workspace-content">
        <span class="workspace-name">{{ displayName }}</span>
        <span class="workspace-hint">点击切换项目</span>
      </div>
      <el-icon class="workspace-arrow" :class="{ 'is-open': isDropdownOpen }">
        <ArrowRight />
      </el-icon>
    </div>

    <!-- 下拉面板 -->
    <Transition name="dropdown-fade">
      <div v-show="isDropdownOpen" class="workspace-dropdown" :style="dropdownStyle">
        <!-- 搜索 -->
        <div class="dropdown-header">
          <div class="search-box">
            <el-icon class="search-icon"><Search /></el-icon>
            <input 
              ref="searchRef"
              v-model="searchQuery" 
              type="text" 
              placeholder="搜索项目..."
              @keydown.esc="closeDropdown"
            />
          </div>
        </div>

        <!-- 项目列表 -->
        <div class="dropdown-body">
          <div class="project-list">
            <div 
              v-for="project in filteredProjects" 
              :key="project.id"
              class="project-item"
              :class="{ 'is-current': selectedProjectId === project.id }"
              @click="selectProject(project)"
            >
              <div class="project-icon" :class="getAvatarColor(project.id)">
                {{ getInitial(project.name) }}
              </div>
              <span class="project-name">{{ project.name }}</span>
              <el-icon v-if="selectedProjectId === project.id" class="check-icon">
                <Check />
              </el-icon>
            </div>

            <!-- 空状态 -->
            <div v-if="filteredProjects.length === 0" class="empty-state">
              <span>没有找到项目</span>
            </div>
          </div>
        </div>

        <!-- 底部操作 -->
        <div v-if="hasProjectSelected" class="dropdown-footer">
          <div class="clear-btn" @click="clearProject">
            <el-icon><CircleClose /></el-icon>
            <span>退出项目空间</span>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 遮罩 -->
    <Transition name="fade">
      <div v-if="isDropdownOpen" class="dropdown-mask" @click="closeDropdown"></div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Grid, ArrowRight, Search, Check, CircleClose } from '@element-plus/icons-vue'
import { useProjectContext } from '../composables/useProjectContext'
import { usePermissions } from '../composables/usePermissions'

const {
  currentProject,
  setCurrentProject,
  getCurrentProjectId,
  getCurrentProjectName,
  hasProjectSelected,
  getAllProjects
} = useProjectContext()

const { isLoggedIn } = usePermissions()

const containerRef = ref()
const triggerRef = ref()
const searchRef = ref()
const selectedProjectId = ref<number | null>(null)
const projects = ref<any[]>([])
const isDropdownOpen = ref(false)
const searchQuery = ref('')
const dropdownStyle = ref<{ top: string }>({ top: '80px' })

// 显示名称
const displayName = computed(() => {
  return hasProjectSelected.value && getCurrentProjectName.value 
    ? getCurrentProjectName.value 
    : '选择项目'
})

// 项目首字母
const projectInitial = computed(() => {
  const name = getCurrentProjectName.value
  return name ? name.charAt(0).toUpperCase() : ''
})

// 头像颜色
const avatarColors = ['color-blue', 'color-purple', 'color-green', 'color-orange', 'color-pink', 'color-cyan']

const avatarColorClass = computed(() => {
  if (!selectedProjectId.value) return 'color-default'
  return getAvatarColor(selectedProjectId.value)
})

const getAvatarColor = (id: number) => avatarColors[id % avatarColors.length]
const getInitial = (name: string) => name ? name.charAt(0).toUpperCase() : ''

// 过滤项目
const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  const q = searchQuery.value.toLowerCase()
  return projects.value.filter(p => p.name.toLowerCase().includes(q))
})

// 切换下拉
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
  if (isDropdownOpen.value) {
    // 计算下拉框位置，与 trigger 顶部对齐
    if (triggerRef.value) {
      const rect = triggerRef.value.getBoundingClientRect()
      dropdownStyle.value = { top: `${rect.top}px` }
    }
    // 通知关闭其他下拉框
    window.dispatchEvent(new CustomEvent('projectSelector:opened'))
    searchQuery.value = ''
    nextTick(() => searchRef.value?.focus())
  }
}

const closeDropdown = () => {
  isDropdownOpen.value = false
  searchQuery.value = ''
}

// 监听子菜单打开事件，关闭自己
const handleSubMenuOpened = () => {
  closeDropdown()
}

// 用户菜单打开时关闭项目选择器
const handleUserMenuOpened = () => {
  closeDropdown()
}

// 选择项目
const selectProject = async (project: any) => {
  selectedProjectId.value = project.id
  await setCurrentProject(project.id)
  ElMessage.success(`切换到: ${project.name}`)
  closeDropdown()
}

// 清除项目
const clearProject = async () => {
  selectedProjectId.value = null
  await setCurrentProject(null)
  ElMessage.success('已退出项目空间')
  closeDropdown()
}

// 加载项目
const loadProjects = async () => {
  if (!isLoggedIn.value) {
    projects.value = []
    return
  }
  try {
    projects.value = await getAllProjects()
    selectedProjectId.value = getCurrentProjectId.value
  } catch (error: any) {
    if (error?.response?.status !== 401) {
      console.error('加载项目失败:', error)
    }
  }
}

// 监听
watch(() => currentProject.value, (p) => {
  selectedProjectId.value = p?.id || null
}, { immediate: true })

watch(() => isLoggedIn.value, (newVal, oldVal) => {
  if (newVal && !oldVal) loadProjects()
  if (!newVal && oldVal) {
    projects.value = []
    selectedProjectId.value = null
  }
})

const handleProjectChanged = () => {
  selectedProjectId.value = getCurrentProjectId.value
}

onMounted(() => {
  loadProjects()
  selectedProjectId.value = getCurrentProjectId.value
  window.addEventListener('project:changed', handleProjectChanged)
  window.addEventListener('submenu:opened', handleSubMenuOpened)
  window.addEventListener('userMenu:opened', handleUserMenuOpened)
})

onUnmounted(() => {
  window.removeEventListener('project:changed', handleProjectChanged)
  window.removeEventListener('submenu:opened', handleSubMenuOpened)
  window.removeEventListener('userMenu:opened', handleUserMenuOpened)
})
</script>

<style scoped>
.workspace-selector {
  position: relative;
}

/* 触发器 */
.workspace-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  min-height: 56px;
}

.workspace-trigger:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.workspace-trigger.is-active {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.workspace-trigger.has-project {
  background: rgba(255, 255, 255, 0.1);
}

/* 图标 */
.workspace-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}

.color-default { background: rgba(255, 255, 255, 0.2); }
.color-blue { background: rgba(255, 255, 255, 0.2); }
.color-purple { background: rgba(255, 255, 255, 0.2); }
.color-green { background: rgba(255, 255, 255, 0.2); }
.color-orange { background: rgba(255, 255, 255, 0.2); }
.color-pink { background: rgba(255, 255, 255, 0.2); }
.color-cyan { background: rgba(255, 255, 255, 0.2); }

/* 内容 */
.workspace-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.workspace-name {
  font-size: 13px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
  line-height: 1.3;
}

.workspace-hint {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  line-height: 1.2;
}

/* 箭头 */
.workspace-arrow {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.workspace-arrow.is-open {
  transform: rotate(90deg);
}

/* 下拉面板 - 从右侧弹出，紫色渐变背景 */
.workspace-dropdown {
  position: fixed;
  top: 80px;
  left: 270px;
  width: 260px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 2000;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

/* 搜索头部 */
.dropdown-header {
  padding: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 8px 12px;
}

.search-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  flex-shrink: 0;
}

.search-box input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 13px;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

/* 项目列表 */
.dropdown-body {
  max-height: 240px;
  overflow-y: auto;
}

.dropdown-body::-webkit-scrollbar {
  width: 4px;
}

.dropdown-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.project-list {
  padding: 8px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: rgba(255, 255, 255, 0.85);
  margin: 2px 0;
}

.project-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  transform: translateX(4px);
}

.project-item.is-current {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.project-item.is-current:hover {
  background: rgba(255, 255, 255, 0.35);
}

.project-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  flex-shrink: 0;
}

.project-name {
  flex: 1;
  font-size: 13px;
  color: inherit;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.project-item.is-current .project-name {
  color: #ffffff;
}

.check-icon {
  color: #ffffff;
  font-size: 16px;
  flex-shrink: 0;
}

/* 空状态 */
.empty-state {
  padding: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

/* 底部 */
.dropdown-footer {
  padding: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.85);
  font-size: 13px;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  transform: translateX(4px);
}

/* 遮罩 */
.dropdown-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

/* 动画 */
.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: all 0.2s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
