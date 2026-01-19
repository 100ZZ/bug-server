<template>
  <div class="sidebar-project-selector" ref="selectorContainer">
    <div class="project-selector-wrapper">
      <!-- 选中项目后使用 dropdown -->
      <el-dropdown 
        v-if="hasProjectSelected && currentProjectName"
        trigger="click"
        popper-class="project-selector-popper"
        @command="handleProjectSelect"
      >
        <div class="project-info">
          <div class="project-avatar">
            <el-icon :size="20" class="pointer-icon"><Pointer /></el-icon>
          </div>
          <div class="project-details">
            <div class="project-name">{{ currentProjectName }}</div>
            <div class="project-hint">当前项目</div>
          </div>
          <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item 
              v-for="project in projects" 
              :key="project.id"
              :command="project.id"
              :class="{ 'is-selected': selectedProjectId === project.id }"
            >
              <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <span>{{ project.name }}</span>
                <el-icon v-if="selectedProjectId === project.id" class="selected-icon">
                  <Check />
                </el-icon>
              </div>
            </el-dropdown-item>
            <!-- 手动插入分割线 -->
            <li class="custom-divider"></li>
            <el-dropdown-item command="clear">
              <span style="color: rgba(255, 255, 255, 0.7);">清除已选项目</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <!-- 未选中项目时显示 el-select -->
      <el-select
        v-else
        ref="selectRef"
        v-model="selectedProjectId"
        placeholder="请选择项目"
        filterable
        clearable
        :style="selectStyle"
        @change="handleProjectChange"
        @visible-change="handleVisibleChange"
        @focus="handleFocus"
        @blur="handleBlur"
        size="default"
        popper-class="project-selector-popper"
        :value-key="'id'"
      >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          >
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ project.name }}</span>
              <el-icon v-if="selectedProjectId === project.id" class="selected-icon">
                <Check />
              </el-icon>
            </div>
          </el-option>
        </el-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Check, Pointer, ArrowDown } from '@element-plus/icons-vue'
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

const selectedProjectId = ref<number | null>(null)
const projects = ref<any[]>([])
const selectRef = ref()
const selectorContainer = ref()

const currentProjectName = computed(() => getCurrentProjectName.value || '')

// 处理 dropdown 选择
const handleProjectSelect = async (command: number | string) => {
  if (command === 'clear') {
    // 清除项目过滤
    await handleProjectChange(null)
  } else {
    // 选择项目
    await handleProjectChange(command as number)
  }
}

// 动态样式 - 选中后显示紫色背景
const selectStyle = computed(() => {
  if (hasProjectSelected.value) {
    return {
      width: '100%',
      '--el-input-bg-color': 'linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%)',
      '--el-input-text-color': '#ffffff',
      '--el-input-icon-color': '#ffffff'
    }
  }
  return {
    width: '100%'
  }
})

// 辅助函数：查找wrapper元素
const findWrapperElement = (): HTMLElement | null => {
  // 方法1: 从 project-selector-wrapper 查找 el-select__wrapper
  const projectWrapper = document.querySelector('.project-selector-wrapper')
  if (projectWrapper) {
    const wrapper = projectWrapper.querySelector('.el-select__wrapper') as HTMLElement | null
    if (wrapper) {
      return wrapper
    }
  }
  
  // 方法2: 从 sidebar-project-selector 查找
  const container = document.querySelector('.sidebar-project-selector')
  if (container) {
    const wrapper = container.querySelector('.el-select__wrapper') as HTMLElement | null
    if (wrapper) {
      return wrapper
    }
  }
  
  // 方法3: 通过 el-select 查找
  const wrapper = document.querySelector('.sidebar-project-selector .el-select .el-select__wrapper') as HTMLElement | null
  if (wrapper) {
    return wrapper
  }
  
  return null
}

// 直接操作 DOM 更新背景样式 - 必须在 watch 之前定义
const updateBackgroundStyle = () => {
  // 使用 setTimeout 确保 Element Plus 的内部 DOM 完全渲染
  nextTick(() => {
    setTimeout(() => {
      forceUpdateBackground()
    }, 300) // 延迟300ms等待 Element Plus 完全渲染
  })
}

// 监听当前项目变化，立即更新显示
watch(() => currentProject.value, (newProject) => {
  if (newProject) {
    selectedProjectId.value = newProject.id
  } else {
    selectedProjectId.value = null
  }
  // 强制更新背景样式
  updateBackgroundStyle()
}, { immediate: true })

// 监听选中状态变化，更新背景样式
watch(() => hasProjectSelected.value, () => {
  updateBackgroundStyle()
})

// 监听登录状态变化，登录后重新加载项目列表
watch(() => isLoggedIn.value, (newValue, oldValue) => {
  // 从未登录到登录状态，重新加载项目列表
  if (newValue && !oldValue) {
    loadProjectsList()
  }
  // 从登录到未登录状态，清空项目列表
  if (!newValue && oldValue) {
    projects.value = []
    selectedProjectId.value = null
  }
})

// 加载项目列表 - 使用 getAllProjects 显示所有项目供用户选择
const loadProjectsList = async () => {
  // 如果未登录，不加载项目列表
  if (!isLoggedIn.value) {
    projects.value = []
    return
  }
  
  try {
    projects.value = await getAllProjects()
    // 同步已选中的项目ID
    selectedProjectId.value = getCurrentProjectId.value
  } catch (error: any) {
    // 如果是未授权错误（401），静默处理，不输出错误和提示
    if (error?.response?.status === 401 || error?.message?.includes('未提供认证信息') || error?.message?.includes('Unauthorized')) {
      projects.value = []
      return
    }
    // 其他错误才输出日志和提示
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

// 项目选择变化
const handleProjectChange = async (projectId: number | null) => {
  if (projectId !== null) {
    await setCurrentProject(projectId)
    // 立即更新选中状态，确保UI立即响应
    selectedProjectId.value = projectId
    ElMessage.success('项目切换成功')
  } else {
    await setCurrentProject(null)
    // 立即更新选中状态
    selectedProjectId.value = null
    ElMessage.success('已取消项目过滤')
  }
  // 更新背景样式
  updateBackgroundStyle()
}

// 下拉框展开/关闭事件 - 强制设置背景颜色
const handleVisibleChange = () => {
  // 立即执行，不需要等待渲染（此时元素已存在）
  setTimeout(() => {
    forceUpdateBackground()
  }, 10)
}

// 获得焦点事件
const handleFocus = () => {
  setTimeout(() => {
    forceUpdateBackground()
  }, 10)
}

// 失去焦点事件
const handleBlur = () => {
  setTimeout(() => {
    forceUpdateBackground()
  }, 10)
}

// 强制更新背景颜色 - 完全匹配用户信息框
const forceUpdateBackground = () => {
  const wrapper = findWrapperElement()
  
  if (!wrapper) {
    return
  }
  
  // 完全匹配用户信息框的样式
  wrapper.style.setProperty('background', 'rgba(255, 255, 255, 0.15)', 'important')
  wrapper.style.setProperty('background-color', 'rgba(255, 255, 255, 0.15)', 'important')
  wrapper.style.setProperty('backdrop-filter', 'blur(10px)', 'important')
  wrapper.style.setProperty('border', '1px solid rgba(255, 255, 255, 0.2)', 'important')
  wrapper.style.setProperty('box-shadow', 'none', 'important')
}

// 监听项目切换事件，同步选中状态
const handleProjectChanged = () => {
  selectedProjectId.value = getCurrentProjectId.value
  updateBackgroundStyle()
}

onMounted(() => {
  loadProjectsList()
  
  // 初始化选中状态
  selectedProjectId.value = getCurrentProjectId.value
  
  // 监听项目切换事件
  window.addEventListener('project:changed', handleProjectChanged)
  
  // 初始化背景样式
  updateBackgroundStyle()
})

// 组件卸载时移除事件监听
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('project:changed', handleProjectChanged)
})
</script>

<style scoped>
.sidebar-project-selector {
  padding: 0;
}

/* 项目选择器包装容器 - 和菜单项保持一致 */
.project-selector-wrapper {
  width: 100%;
  margin: 6px 0; /* 和菜单项的 margin 一致 */
  position: relative;
}

/* el-dropdown 完全填充容器 */
.project-selector-wrapper :deep(.el-dropdown) {
  width: 100%;
  display: block;
}

/* 项目信息展示区域 - 完全匹配用户信息框 */
.project-info {
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

.project-info:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

/* 项目图标圆圈 */
.project-avatar {
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

/* 指针图标旋转 - 指向右边 */
.project-avatar .pointer-icon {
  transform: rotate(90deg);
}

/* 项目详情区域 */
.project-details {
  flex: 1;
  min-width: 0;
}

/* 项目名称 */
.project-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 项目提示文字 */
.project-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
}

/* 下拉箭头 */
.dropdown-icon {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.project-info:hover .dropdown-icon {
  transform: translateY(2px);
}

/* el-select 占据整个宽度 */
:deep(.el-select) {
  width: 100%;
}

/* el-select 外层容器 - 完全匹配用户信息框的样式 */
:deep(.el-select .el-select__wrapper) {
  background: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  padding: 0 32px 0 32px !important; /* 左右对称padding，确保文字居中 */
  height: 48px !important;
  line-height: 48px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* 选中项目后 - 完全匹配用户信息框 */
:deep(.el-select.has-selected .el-select__wrapper),
:deep(.has-selected .el-select__wrapper),
.sidebar-project-selector :deep(.el-select.has-selected .el-select__wrapper) {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  padding: 0 32px 0 32px !important;
  transition: all 0.3s ease !important;
}

/* 文字居中 - 确保placeholder和选中文字都居中 */
:deep(.el-select .el-input__inner),
:deep(.el-select input),
:deep(.el-select .el-select__input) {
  text-align: center !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
  width: 100% !important;
  margin: 0 auto !important;
}

/* 下拉箭头位置调整 */
:deep(.el-select .el-input__suffix) {
  right: 12px !important;
}

/* hover效果 - 参考用户信息框的hover效果 */
:deep(.el-select .el-select__wrapper:hover) {
  background: rgba(255, 255, 255, 0.25) !important;
  background-color: rgba(255, 255, 255, 0.25) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
}

/* focus效果 - 保持默认样式 */
:deep(.el-select .el-select__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  box-shadow: none !important;
}

/* 选中后的hover效果 - 参考用户信息框的hover效果 */
:deep(.el-select.has-selected .el-select__wrapper:hover) {
  background: rgba(255, 255, 255, 0.25) !important;
  background-color: rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
  transform: translateY(-2px);
}

/* 选中后的focus效果 - 保持默认样式 */
:deep(.el-select.has-selected .el-select__wrapper.is-focus),
:deep(.el-select.has-selected .el-select__wrapper[aria-expanded="true"]) {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  box-shadow: none !important;
}

/* 选中状态的文字和图标 - 默认白色，居中，不加粗 */
:deep(.el-select .el-input__inner),
:deep(.el-select input),
:deep(.el-select.has-selected .el-input__inner),
:deep(.el-select.has-selected input),
:deep(.el-select .el-select__input) {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 500 !important;
  text-align: center !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

:deep(.el-select .el-input__suffix .el-icon),
:deep(.el-select.has-selected .el-input__suffix .el-icon) {
  color: #ffffff !important;
}

/* 输入框内部文字 - 白色 */
:deep(.el-select .el-input__inner),
:deep(.el-select .el-select__input),
:deep(.el-select .el-select__input-inner),
:deep(.el-select .el-select__tags-text),
:deep(.el-select input),
:deep(.el-select .el-input input),
:deep(.el-select .el-input__inner input) {
  color: #ffffff !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  opacity: 1 !important;
  visibility: visible !important;
  -webkit-text-fill-color: #ffffff !important;
}

/* placeholder文字 - 更明显的白色，居中显示 */
:deep(.el-select .el-input__inner::placeholder),
:deep(.el-select .el-input__inner::-webkit-input-placeholder) {
  color: rgba(255, 255, 255, 0.8) !important;
  opacity: 1 !important;
  text-align: center !important;
}

/* 图标颜色 */
:deep(.el-select .el-input__suffix .el-icon),
:deep(.el-select .el-input__suffix-inner .el-icon),
.sidebar-project-selector .el-select .el-input__suffix .el-icon,
.sidebar-project-selector .el-select.has-selected .el-input__suffix .el-icon,
.sidebar-project-selector .el-select.has-selected .el-input__suffix-inner .el-icon {
  color: #ffffff !important;
}

.selected-icon {
  color: #ffffff !important;
  font-size: 16px;
}
</style>

<style>
/* 全局样式：完全匹配用户信息框的样式 */
.sidebar-project-selector .el-select .el-select__wrapper,
body .sidebar-project-selector .el-select .el-select__wrapper,
html body .sidebar-project-selector .el-select .el-select__wrapper {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  height: 48px !important;
  min-height: 48px !important;
  transition: all 0.3s ease !important;
}

.sidebar-project-selector .el-select .el-select__wrapper:hover,
body .sidebar-project-selector .el-select .el-select__wrapper:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  background-color: rgba(255, 255, 255, 0.25) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
}

.sidebar-project-selector .el-select .el-select__wrapper.is-focus,
.sidebar-project-selector .el-select .el-select__wrapper[aria-expanded="true"],
body .sidebar-project-selector .el-select .el-select__wrapper.is-focus,
body .sidebar-project-selector .el-select .el-select__wrapper[aria-expanded="true"] {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  box-shadow: none !important;
}

/* 选中后的样式 - 完全匹配用户信息框 */
.sidebar-project-selector .el-select.has-selected .el-select__wrapper,
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper,
html body .sidebar-project-selector .el-select.has-selected .el-select__wrapper {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  transition: all 0.3s ease !important;
}

.sidebar-project-selector .el-select.has-selected .el-select__wrapper:hover,
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  background-color: rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2) !important;
  transform: translateY(-2px);
}

.sidebar-project-selector .el-select.has-selected .el-select__wrapper.is-focus,
.sidebar-project-selector .el-select.has-selected .el-select__wrapper[aria-expanded="true"],
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper.is-focus,
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper[aria-expanded="true"] {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  box-shadow: none !important;
}

/* 所有文字都是白色 - 更强制的覆盖，不加粗 */
.sidebar-project-selector .el-select .el-select__input,
.sidebar-project-selector .el-select .el-select__input-inner,
.sidebar-project-selector .el-select .el-input__inner,
.sidebar-project-selector .el-select .el-select__tags-text,
.sidebar-project-selector .el-select.has-selected .el-select__input,
.sidebar-project-selector .el-select.has-selected .el-select__input-inner,
.sidebar-project-selector .el-select.has-selected .el-input__inner,
.sidebar-project-selector .el-select.has-selected .el-select__tags-text,
.sidebar-project-selector .el-select.has-selected .el-input__wrapper *,
.sidebar-project-selector .el-select .el-input__wrapper span,
.sidebar-project-selector .el-select.has-selected .el-input__wrapper span,
.sidebar-project-selector .el-select input,
.sidebar-project-selector .el-select .el-input input,
.sidebar-project-selector .el-select .el-input__inner input,
.sidebar-project-selector .el-select.has-selected input {
  color: #ffffff !important;
  opacity: 1 !important;
  visibility: visible !important;
  display: inline-block !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 500 !important;
  text-align: center !important;
}

/* 选中状态下的文字特别加强 - 确保显示为白色，不加粗 */
.sidebar-project-selector .el-select.has-selected .el-input__inner,
.sidebar-project-selector .el-select.has-selected input,
.sidebar-project-selector .el-select.has-selected .el-input__wrapper span,
.sidebar-project-selector .el-select.has-selected .el-select__selected-item {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 500 !important;
  text-align: center !important;
}

/* placeholder 文字更明显，居中显示 */
.sidebar-project-selector .el-select .el-input__inner::placeholder,
.sidebar-project-selector .el-select .el-input__inner::-webkit-input-placeholder {
  color: rgba(255, 255, 255, 0.8) !important;
  opacity: 1 !important;
  text-align: center !important;
}

.sidebar-project-selector .el-select .el-input__suffix,
.sidebar-project-selector .el-select .el-input__suffix-inner {
  color: rgba(255, 255, 255, 0.9) !important;
}

/* 下拉选项样式 - 参考 user-dropdown-popper 的实现方式 */
.project-selector-popper {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
  /* 确保下拉菜单宽度与项目选择器一致 */
  min-width: 228px !important;
  width: 228px !important;
}

/* el-select 下拉菜单样式 */
.project-selector-popper .el-select-dropdown {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
  border: none !important;
  padding: 8px !important;
  backdrop-filter: blur(10px);
  width: 100% !important;
  margin-top: 0 !important;
}

/* el-dropdown 下拉菜单样式 - 和 el-select 保持一致 */
.project-selector-popper .el-dropdown-menu {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
  border: none !important;
  padding: 8px !important;
  backdrop-filter: blur(10px);
  min-width: 228px !important;
  width: 228px !important;
}

/* el-select 下拉项样式 */
.project-selector-popper .el-select-dropdown__item {
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

.project-selector-popper .el-select-dropdown__item:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateX(4px);
}

/* Element Plus 选中项的 class 是 is-selected */
.project-selector-popper .el-select-dropdown__item.selected,
.project-selector-popper .el-select-dropdown__item.is-selected {
  background: rgba(255, 255, 255, 0.25) !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.project-selector-popper .el-select-dropdown__item.selected:hover,
.project-selector-popper .el-select-dropdown__item.is-selected:hover {
  background: rgba(255, 255, 255, 0.35) !important;
  color: #ffffff !important;
}

/* 确保选中项的所有子元素都是白色 */
.project-selector-popper .el-select-dropdown__item.selected *,
.project-selector-popper .el-select-dropdown__item.is-selected * {
  color: #ffffff !important;
}

.project-selector-popper .el-select-dropdown__item .el-icon {
  font-size: 16px !important;
  color: rgba(255, 255, 255, 0.85) !important;
}

/* el-dropdown 下拉项样式 - 和 el-select 保持一致 */
.project-selector-popper .el-dropdown-menu__item {
  border-radius: 8px !important;
  padding: 10px 16px !important;
  transition: all 0.3s ease !important;
  color: rgba(255, 255, 255, 0.85) !important;
  margin: 2px 0 !important;
  background: transparent !important;
}

.project-selector-popper .el-dropdown-menu__item:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateX(4px);
}

.project-selector-popper .el-dropdown-menu__item.is-selected {
  background: rgba(255, 255, 255, 0.25) !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.project-selector-popper .el-dropdown-menu__item.is-selected:hover {
  background: rgba(255, 255, 255, 0.35) !important;
  color: #ffffff !important;
}

.project-selector-popper .el-dropdown-menu__item.is-selected * {
  color: #ffffff !important;
}

.project-selector-popper .el-dropdown-menu__item .el-icon {
  font-size: 16px !important;
  color: rgba(255, 255, 255, 0.85) !important;
}

/* 自定义分割线样式 - 柔和的浅白色 */
.project-selector-popper .custom-divider {
  height: 1px !important;
  background: rgba(255, 255, 255, 0.2) !important;
  margin: 8px 12px !important;
  list-style: none !important;
  padding: 0 !important;
  overflow: hidden !important;
}

/* 确保箭头也是紫色，去掉白色边缘 */
.project-selector-popper .el-popper__arrow::before {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
}

/* 去掉下拉菜单的白色边缘 */
.project-selector-popper {
  box-shadow: none !important;
  border: none !important;
  background: transparent !important;
}

.project-selector-popper .el-select-dropdown {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
}

/* 确保 popper 容器本身没有边框 */
.project-selector-popper.el-popper {
  border: none !important;
  background: transparent !important;
}

/* 去掉所有可能的白色边框和轮廓 */
.project-selector-popper * {
  border-color: transparent !important;
  outline: none !important;
}

.project-selector-popper .el-select-dropdown,
.project-selector-popper .el-select-dropdown__item {
  border: none !important;
  outline: none !important;
}

/* 全局强制样式 - 所有状态都使用用户信息框的样式 */
/* 未选中状态 - 和用户信息框一样的背景 */
.sidebar-project-selector .el-select:not(.has-selected) .el-input__wrapper,
body .sidebar-project-selector .el-select:not(.has-selected) .el-input__wrapper,
html body .sidebar-project-selector .el-select:not(.has-selected) .el-input__wrapper {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

/* 已选中状态 - 完全匹配用户信息框 */
.sidebar-project-selector .el-select.has-selected .el-select__wrapper,
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper,
html body .sidebar-project-selector .el-select.has-selected .el-select__wrapper {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

/* 所有状态的白色文字 - 全局强制，默认就应用，居中，不加粗 */
.sidebar-project-selector .el-input__inner,
.sidebar-project-selector input,
.sidebar-project-selector .el-select .el-input__inner,
.sidebar-project-selector .el-select input,
.sidebar-project-selector .el-select .el-select__input,
body .sidebar-project-selector .el-select .el-input__inner,
body .sidebar-project-selector .el-select input,
body .sidebar-project-selector .el-select.has-selected .el-input__inner,
body .sidebar-project-selector .el-select.has-selected input,
.sidebar-project-selector .has-selected .el-input__inner,
.sidebar-project-selector .has-selected input {
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 500 !important;
  text-align: center !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

/* 所有状态的白色图标 - 全局强制，默认就应用 */
.sidebar-project-selector .el-input__suffix .el-icon,
.sidebar-project-selector .el-select .el-input__suffix .el-icon,
body .sidebar-project-selector .el-select .el-input__suffix .el-icon,
body .sidebar-project-selector .el-select.has-selected .el-input__suffix .el-icon,
.sidebar-project-selector .has-selected .el-input__suffix .el-icon {
  color: #ffffff !important;
}

/* 最高优先级 - 完全匹配用户信息框（包括所有状态）*/
.sidebar-project-selector .el-select__wrapper,
.sidebar-project-selector .el-select .el-select__wrapper,
.sidebar-project-selector .has-selected .el-select__wrapper,
.sidebar-project-selector .el-select.has-selected .el-select__wrapper,
.sidebar-project-selector .el-select.has-selected > .el-select > .el-select__wrapper,
body .sidebar-project-selector .el-select__wrapper,
body .sidebar-project-selector .has-selected .el-select__wrapper,
html body .sidebar-project-selector .el-select__wrapper,
html body .sidebar-project-selector .has-selected .el-select__wrapper,
.project-selector-wrapper .el-select__wrapper,
.project-selector-wrapper .el-select .el-select__wrapper,
.project-selector-wrapper .has-selected .el-select__wrapper,
.project-selector-wrapper .el-select.has-selected .el-select__wrapper {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: none !important;
}

/* focus 和展开状态 - 保持默认样式 */
.sidebar-project-selector .el-select__wrapper.is-focus,
.sidebar-project-selector .el-select__wrapper[aria-expanded="true"],
.sidebar-project-selector .el-select .el-select__wrapper.is-focus,
.sidebar-project-selector .el-select .el-select__wrapper[aria-expanded="true"],
.sidebar-project-selector .el-select.has-selected .el-select__wrapper.is-focus,
.sidebar-project-selector .el-select.has-selected .el-select__wrapper[aria-expanded="true"],
body .sidebar-project-selector .el-select__wrapper.is-focus,
body .sidebar-project-selector .el-select__wrapper[aria-expanded="true"],
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper.is-focus,
body .sidebar-project-selector .el-select.has-selected .el-select__wrapper[aria-expanded="true"],
.project-selector-wrapper .el-select__wrapper.is-focus,
.project-selector-wrapper .el-select__wrapper[aria-expanded="true"],
.project-selector-wrapper .el-select.has-selected .el-select__wrapper.is-focus,
.project-selector-wrapper .el-select.has-selected .el-select__wrapper[aria-expanded="true"] {
  background: rgba(255, 255, 255, 0.15) !important;
  background-color: rgba(255, 255, 255, 0.15) !important;
  box-shadow: none !important;
}
</style>
