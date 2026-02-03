<template>
  <div class="bugs-page">
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><List /></el-icon>
          缺陷管理
        </h2>
      </div>
      <div class="filter-row">
        <el-select 
          v-model="filters.project_id" 
          placeholder="选择项目" 
          clearable 
          @change="loadBugs"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
        >
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable @change="loadBugs">
          <el-option label="待处理" value="open" />
          <el-option label="进行中" value="in_progress" />
          <el-option label="已解决" value="resolved" />
          <el-option label="已关闭" value="closed" />
          <el-option label="重新打开" value="reopened" />
        </el-select>
        <el-select v-model="filters.assignee_id" placeholder="处理人" clearable @change="loadBugs" style="width: 180px">
          <el-option 
            v-for="user in users" 
            :key="user.id" 
            :label="user.display_name || user.username" 
            :value="user.id" 
          />
        </el-select>
        <el-input v-model="filters.keyword" placeholder="搜索标题或描述" clearable @keyup.enter="loadBugs">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadBugs">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button 
          v-if="canCreate('bugs')" 
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新建缺陷
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table 
        :data="paginatedBugs" 
        v-loading="loading" 
        stripe
        @row-click="handleRowClick"
        :row-style="{ cursor: 'pointer' }"
        :max-height="600"
      >
        <el-table-column label="编号" width="70" type="index" align="center" />
        <el-table-column prop="project" label="项目" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee" label="处理人" show-overflow-tooltip align="center">
          <template #default="{ row }">
            {{ row.assignee?.display_name || row.assignee?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" align="center">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ getSeverityLabel(row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" align="center">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="175" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" v-if="canUpdate('bugs') || canDelete('bugs')">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button 
                v-if="canUpdate('bugs')" 
                link 
                type="primary"
                @click.stop="handleEdit(row)"
              >
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button 
                v-if="canDelete('bugs')" 
                link 
                type="danger"
                @click.stop="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 12px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, sizes, jumper, ->, total"
          :total="bugs.length"
        />
      </div>
    </el-card>

    <!-- 创建/编辑抽屉 -->
    <el-drawer 
      v-model="drawerVisible" 
      :title="drawerTitle" 
      size="80%"
    >
      <div class="bug-drawer-content">
        <!-- 左侧：标题和描述 -->
        <div class="drawer-left">
          <el-form :model="formData" label-position="top">
            <el-form-item label="标题" required>
              <el-input 
                v-model="formData.title" 
                placeholder="请输入缺陷标题" 
                size="large"
              />
            </el-form-item>
            
            <el-form-item label="前端页面">
              <el-input 
                v-model="formData.page_url" 
                placeholder="请输入前端页面URL或页面名称"
              />
            </el-form-item>
            
            <el-form-item label="环境信息">
              <el-input 
                v-model="formData.environment" 
                placeholder="请输入环境信息（如：测试环境、生产环境等）"
              />
            </el-form-item>
            
            <el-form-item label="缺陷描述" class="description-form-item">
              <el-input 
                v-model="formData.description" 
                type="textarea" 
                placeholder="请输入详细描述，支持粘贴截图（Ctrl+V）"
                @paste="handlePaste"
                class="description-textarea-full"
              />
              <!-- 图片预览区域 -->
              <div v-if="pastedImages.length > 0" class="image-preview-area">
                <div v-for="(img, index) in pastedImages" :key="index" class="image-item">
                  <el-image 
                    :src="getImageUrl(img)" 
                    :preview-src-list="pastedImages.map(getImageUrl)"
                    :initial-index="index"
                    fit="cover"
                    class="img-thumbnail"
                  />
                  <div class="image-delete" @click="removeImage(index)">🗑️</div>
                </div>
              </div>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 右侧：元数据字段 -->
        <div class="drawer-right">
          <el-form :model="formData" label-position="top" label-width="100px">
            <el-form-item label="项目" required>
              <el-select 
                v-model="formData.project_id" 
                placeholder="选择项目" 
                style="width: 100%"
                :disabled="hasProjectSelected"
                :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
              >
                <el-option 
                  v-for="project in projects" 
                  :key="project.id" 
                  :label="project.name" 
                  :value="project.id" 
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="状态" required>
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="待处理" value="open" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已解决" value="resolved" />
                <el-option label="已关闭" value="closed" />
                <el-option label="重新打开" value="reopened" />
                <el-option label="待定" value="pending" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="处理人">
              <el-select v-model="formData.assignee_id" placeholder="选择处理人" clearable style="width: 100%">
                <el-option 
                  v-for="user in users" 
                  :key="user.id" 
                  :label="user.display_name || user.username" 
                  :value="user.id" 
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="版本">
              <el-input v-model="formData.version" placeholder="发现版本" />
            </el-form-item>
            
            <el-form-item label="迭代">
              <el-select 
                v-model="formData.module" 
                placeholder="选择迭代" 
                clearable
                filterable
                style="width: 100%"
              >
                <el-option 
                  v-for="sprint in sprints" 
                  :key="sprint.id" 
                  :label="sprint.name" 
                  :value="String(sprint.id)" 
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="缺陷类型" required>
              <el-select v-model="formData.type" style="width: 100%">
                <el-option label="缺陷" value="bug" />
                <el-option label="故障" value="defect" />
                <el-option label="改进" value="improvement" />
                <el-option label="任务" value="task" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="严重程度" required>
              <el-select v-model="formData.severity" style="width: 100%">
                <el-option label="致命" value="fatal" />
                <el-option label="严重" value="serious" />
                <el-option label="一般" value="general" />
                <el-option label="轻微" value="slight" />
                <el-option label="建议" value="suggestion" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="优先级" required>
              <el-select v-model="formData.priority" style="width: 100%">
                <el-option label="阻塞" value="blocker" />
                <el-option label="严重" value="critical" />
                <el-option label="主要" value="major" />
                <el-option label="次要" value="minor" />
                <el-option label="轻微" value="trivial" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="预估工时（小时）">
              <el-input-number 
                v-model="formData.estimated_hours" 
                :min="0" 
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="开始日期">
              <el-date-picker 
                v-model="formData.start_date" 
                type="date" 
                placeholder="选择开始日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            
            <el-form-item label="截止日期">
              <el-date-picker 
                v-model="formData.due_date" 
                type="date" 
                placeholder="选择截止日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <!-- 底部操作按钮 -->
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="drawerVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Delete, EditPen, List } from '@element-plus/icons-vue'
import * as bugApi from '../api/bugs'
import * as projectApi from '../api/projects'
import * as userApi from '../api/users'
import * as sprintApi from '../api/sprints'
import { usePermissions } from '../composables/usePermissions'
import { useProjectContext } from '../composables/useProjectContext'
import type { Bug, Project, User, Sprint } from '../api/types'

const { canCreate, canUpdate, canDelete, getCurrentUser } = usePermissions()

const bugs = ref<Bug[]>([])
const projects = ref<Project[]>([])
const users = ref<User[]>([])
const sprints = ref<Sprint[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const saving = ref(false)
const drawerVisible = ref(false)
const drawerTitle = ref('新建缺陷')
const editingId = ref<number>()
const editingBugKey = ref<string>()  // 当前编辑的缺陷编号
const pastedImages = ref<string[]>([])  // 存储图片URL（服务器返回的相对路径）
const pendingImageFiles = ref<File[]>([])  // 新建时暂存的待上传图片文件

const filters = reactive({
  project_id: undefined,
  status: undefined,
  assignee_id: undefined,
  keyword: ''
})

const formData = reactive({
  project_id: undefined,
  title: '',
  page_url: '',
  environment: '',
  description: '',
  type: 'bug',
  priority: 'major',
  severity: 'general',
  status: 'open',
  assignee_id: undefined,
  reporter_id: getCurrentUser()?.id || 1,
  steps_to_reproduce: '',
  version: '',
  module: '',
  estimated_hours: undefined,
  due_date: undefined,
  attachments: [] as string[]
})

const loadBugs = async () => {
  loading.value = true
  try {
    const params: any = { ...filters }
    
    // 优先使用当前项目过滤
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
    }
    
    bugs.value = await bugApi.getBugs(params)
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  filters.project_id = undefined
  filters.status = undefined
  filters.assignee_id = undefined
  filters.keyword = ''
  loadBugs()
}

const { 
  getProjects: getFilteredProjects, 
  getCurrentProjectId, 
  hasProjectSelected,
  onProjectChanged,
  ensureInitialized
} = useProjectContext()

const loadProjects = async () => {
  try {
    // 使用 useProjectContext 的 getProjects，会自动根据选中的项目过滤
    projects.value = await getFilteredProjects()
    
    // 如果有选中的项目，自动设置过滤器
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.project_id = getCurrentProjectId.value
    }
  } catch (error) {
    console.error(error)
  }
}

const loadUsers = async () => {
  try {
    users.value = await userApi.getUsers()
  } catch (error) {
    console.error(error)
  }
}

const loadSprints = async () => {
  try {
    const params: any = { limit: 1000 }
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
    } else if (formData.project_id) {
      params.project_id = formData.project_id
    }
    sprints.value = await sprintApi.getSprints(params)
  } catch (error) {
    console.error(error)
  }
}

const paginatedBugs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return bugs.value.slice(start, start + pageSize.value)
})

const handleCreate = () => {
  editingId.value = undefined
  editingBugKey.value = undefined
  drawerTitle.value = '新建缺陷'
  pastedImages.value = []
  pendingImageFiles.value = []
  Object.assign(formData, {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : undefined,
    title: '',
    page_url: '',
    environment: '',
    description: '',
    type: 'bug',
    priority: 'major',
    severity: 'general',
    status: 'open',
    assignee_id: undefined,
    reporter_id: getCurrentUser()?.id || 1,
    steps_to_reproduce: '',
    version: '',
    module: '',
    estimated_hours: undefined,
    due_date: undefined,
    attachments: []
  })
  drawerVisible.value = true
}

const handleEdit = (row: Bug) => {
  editingId.value = row.id
  editingBugKey.value = row.bug_key
  drawerTitle.value = '编辑缺陷'
  pendingImageFiles.value = []
  
  // 加载已有的附件图片（现在存储的是URL路径）
  pastedImages.value = row.attachments ? [...row.attachments] : []
  
  // 转换数据类型
  const editData = {
    ...row,
    attachments: row.attachments || [],
    // 确保 estimated_hours 是数字类型
    estimated_hours: row.estimated_hours ? parseFloat(row.estimated_hours as any) : undefined
  }
  
  Object.assign(formData, editData)
  drawerVisible.value = true
}

// 行点击事件
const handleRowClick = (row: Bug) => {
  if (canUpdate('bugs')) {
    handleEdit(row)
  }
}

const handleSave = async () => {
  if (!formData.project_id || !formData.title) {
    ElMessage.warning('请填写必填项：项目和标题')
    return
  }

  saving.value = true
  try {
    let bugKey = editingBugKey.value
    
    if (editingId.value) {
      // 编辑模式：直接更新（图片已经在粘贴时上传了）
      const dataToSave = {
        ...formData,
        attachments: pastedImages.value
      }
      await bugApi.updateBug(editingId.value, dataToSave)
      ElMessage.success('更新成功')
    } else {
      // 新建模式：先创建缺陷，再上传图片
      // 先创建不带附件的缺陷
      const dataToSave = {
        ...formData,
        attachments: []
      }
      const createdBug = await bugApi.createBug(dataToSave)
      bugKey = createdBug.bug_key
      
      // 上传所有待上传的图片
      if (pendingImageFiles.value.length > 0) {
        const uploadedUrls: string[] = []
        for (const file of pendingImageFiles.value) {
          try {
            const result = await bugApi.uploadBugImage(bugKey, file)
            uploadedUrls.push(result.url)
          } catch (uploadError: any) {
            console.error('图片上传失败:', uploadError)
            ElMessage.warning('部分图片上传失败')
          }
        }
        
        // 更新缺陷的附件列表
        if (uploadedUrls.length > 0) {
          await bugApi.updateBug(createdBug.id, { attachments: uploadedUrls })
        }
      }
      
      ElMessage.success('创建成功')
    }
    drawerVisible.value = false
    loadBugs()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
    console.error('保存错误:', error)
  } finally {
    saving.value = false
  }
}

// 处理图片粘贴
const handlePaste = async (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (!items) return
  
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      if (file) {
        if (editingBugKey.value) {
          // 编辑模式：直接上传图片到服务器
          try {
            const result = await bugApi.uploadBugImage(editingBugKey.value, file)
            pastedImages.value.push(result.url)
            ElMessage.success('图片已上传')
          } catch (error: any) {
            ElMessage.error('图片上传失败: ' + (error.message || '未知错误'))
          }
        } else {
          // 新建模式：暂存文件，显示预览
          pendingImageFiles.value.push(file)
          // 生成本地预览URL
          const previewUrl = URL.createObjectURL(file)
          pastedImages.value.push(previewUrl)
          ElMessage.success('图片已添加，将在保存时上传')
        }
      }
    }
  }
}

// 获取图片完整URL（处理相对路径）
const getImageUrl = (url: string) => {
  if (!url) return ''
  // 如果是 blob: 开头的本地预览URL，直接返回
  if (url.startsWith('blob:')) return url
  // 如果是相对路径（以 /api/ 开头），添加基础URL
  if (url.startsWith('/api/')) {
    // 获取当前页面的 origin
    return url
  }
  // 如果是完整URL或base64，直接返回
  return url
}

// 删除粘贴的图片
const removeImage = async (index: number) => {
  const imageUrl = pastedImages.value[index]
  
  // 如果是编辑模式且是服务器上的图片，需要调用删除接口
  if (editingBugKey.value && imageUrl.startsWith('/api/bugs/')) {
    try {
      // 从URL中提取文件名
      const filename = imageUrl.split('/').pop()
      if (filename) {
        await bugApi.deleteBugImage(editingBugKey.value, filename)
      }
    } catch (error: any) {
      console.error('删除图片失败:', error)
      // 即使删除失败也从列表中移除
    }
  }
  
  // 如果是本地预览URL，释放内存
  if (imageUrl.startsWith('blob:')) {
    URL.revokeObjectURL(imageUrl)
    // 同时从待上传列表中移除对应的文件
    pendingImageFiles.value.splice(index, 1)
  }
  
  pastedImages.value.splice(index, 1)
  ElMessage.info('图片已删除')
}

const handleDelete = async (row: Bug) => {
  try {
    await ElMessageBox.confirm('确定删除此缺陷吗？', '提示', {
      type: 'warning'
    })
    await bugApi.deleteBug(row.id)
    ElMessage.success('删除成功')
    loadBugs()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    bug: 'danger',
    defect: 'danger',
    improvement: 'success',
    task: 'info'
  }
  return map[type] || 'info'
}

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    bug: '缺陷',
    defect: '故障',
    improvement: '改进',
    task: '任务'
  }
  return map[type] || type
}

const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = {
    blocker: 'danger',
    critical: 'danger',
    major: 'warning',
    minor: 'info',
    trivial: 'info'
  }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const map: Record<string, string> = {
    blocker: '阻塞',
    critical: '严重',
    major: '主要',
    minor: '次要',
    trivial: '轻微'
  }
  return map[priority] || priority
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    open: 'info',
    in_progress: 'warning',
    resolved: 'success',
    closed: 'info',
    reopened: 'danger',
    pending: 'warning'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    open: '待处理',
    in_progress: '进行中',
    resolved: '已解决',
    closed: '已关闭',
    reopened: '重新打开',
    pending: '待定'
  }
  return map[status] || status
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    fatal: 'danger',
    serious: 'danger',
    general: 'warning',
    slight: 'info',
    suggestion: ''
  }
  return map[severity] || 'info'
}

const getSeverityLabel = (severity: string) => {
  const map: Record<string, string> = {
    fatal: '致命',
    serious: '严重',
    general: '一般',
    slight: '轻微',
    suggestion: '建议'
  }
  return map[severity] || severity
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 监听表单项目变化，重新加载迭代列表
watch(() => formData.project_id, (newProjectId) => {
  if (newProjectId) {
    loadSprints()
  }
})

onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 如果有选中的项目，自动设置过滤器
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    filters.project_id = getCurrentProjectId.value
  }
  loadBugs()
  loadProjects()
  loadUsers()
  loadSprints()
  
  // 监听项目切换事件
  const cleanup = onProjectChanged(() => {
    // 项目切换时重新加载项目列表和数据
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.project_id = getCurrentProjectId.value
    }
    loadProjects()
    loadBugs()
    loadSprints()
  })
  
  // 组件卸载时清理监听
  onUnmounted(() => {
    cleanup()
  })
})
</script>

<style scoped>
.bugs-page {
  height: 100%;
  animation: fadeIn 0.5s ease-in;
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

.filter-card {
  margin-bottom: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

.filter-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.8);
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f2f5;
}

.filter-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.5px;
}

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.table-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
}

.table-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.8);
}

/* 表格样式美化 */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  font-size: 14px;
}

:deep(.el-table__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

:deep(.el-table__header th) {
  background: transparent;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
  padding: 14px 8px;
}

:deep(.el-table__header th .cell) {
  text-align: center;
  padding: 0 4px;
}

:deep(.el-table__body tr) {
  transition: background-color 0.2s ease;
}

:deep(.el-table__body tr:hover) {
  background: #f8f9ff !important;
}

:deep(.el-table__body td) {
  padding: 12px 8px;
  border-bottom: 1px solid #f0f2f5;
}

:deep(.el-table__body td .cell) {
  line-height: 1.5;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped) {
  background: #fafbfc;
}

/* 操作列样式 */
.table-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  padding: 2px 8px;
  border: none;
  font-size: 12px;
}

/* 操作栏按钮美化 - 编辑和执行使用紫色系，删除保留红色，无背景色 */
:deep(.el-button.is-link.action-btn) {
  padding: 6px 12px !important;
  margin: 0 4px !important;
  border-radius: 6px !important;
  transition: all 0.3s ease !important;
  font-weight: 500 !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.el-button.is-link.action-btn .el-icon) {
  font-size: 14px !important;
  color: inherit !important;
}

/* 编辑和执行按钮使用紫色系 */
:deep(.el-button.is-link.action-btn[type="primary"]),
:deep(.el-button.is-link.action-btn.el-button--primary),
:deep(.el-button.is-link.action-btn[type="success"]),
:deep(.el-button.is-link.action-btn.el-button--success) {
  color: #667eea !important;
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

:deep(.el-button.is-link.action-btn[type="primary"]:hover),
:deep(.el-button.is-link.action-btn.el-button--primary:hover),
:deep(.el-button.is-link.action-btn[type="success"]:hover),
:deep(.el-button.is-link.action-btn.el-button--success:hover) {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
  color: #764ba2 !important;
  transform: translateY(-1px);
}

/* 删除按钮保留红色 */
:deep(.el-button.is-link.action-btn[type="danger"]),
:deep(.el-button.is-link.action-btn.el-button--danger) {
  color: #f56c6c !important;
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

:deep(.el-button.is-link.action-btn[type="danger"]:hover),
:deep(.el-button.is-link.action-btn.el-button--danger:hover) {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
  color: #e55252 !important;
  transform: translateY(-1px);
}

/* 分页样式美化 */
:deep(.el-pagination) {
  margin-top: 20px;
}

:deep(.el-pagination .el-pager li) {
  border-radius: 6px;
  margin: 0 2px;
  transition: all 0.2s ease;
}

:deep(.el-pagination .el-pager li:hover) {
  background: #667eea;
  color: #ffffff;
  transform: translateY(-2px);
}

:deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  font-weight: 600;
}

/* 输入框和按钮美化 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
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

:deep(.el-select .el-input__wrapper) {
  border-radius: 8px;
}

/* 抽屉样式美化 */
:deep(.el-drawer) {
  border-radius: 16px 0 0 16px;
}

:deep(.el-drawer__header) {
  background: #ffffff;
  color: #303133;
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
  border-radius: 16px 0 0 0;
}

:deep(.el-drawer__title) {
  color: #303133;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-drawer__close-btn) {
  color: #909399;
  font-size: 20px;
}

:deep(.el-drawer__close-btn:hover) {
  color: #303133;
}

/* 抽屉内容布局 */
.bug-drawer-content {
  display: flex;
  gap: 24px;
  height: calc(100vh - 120px);
  overflow: hidden;
  padding-top: 12px;
}

.drawer-left {
  flex: 1;
  overflow-y: auto;
  padding-right: 12px;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.drawer-left .el-form {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.drawer-left .el-form :deep(.el-form-item) {
  margin-bottom: 12px;
}

.drawer-left .el-form :deep(.el-form-item__label) {
  margin-bottom: 4px;
}

.description-form-item {
  margin-bottom: 0 !important;
}

/* 描述输入框 */
.description-textarea-full :deep(.el-textarea__inner) {
  height: 300px !important;
  resize: vertical;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.6;
}

/* 标题输入框粗体 */
.drawer-left .el-form-item:first-child :deep(.el-input__inner) {
  font-weight: bold;
  font-size: 16px;
}

/* 图片预览区域 */
.image-preview-area {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  align-content: flex-start;
  gap: 6px;
  margin-top: 6px;
  padding: 6px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 220px;
  overflow-y: auto;
  flex-shrink: 0;
}

.image-item {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  flex-shrink: 0;
}

.img-thumbnail {
  width: 100%;
  height: 100%;
  cursor: zoom-in;
}

.image-delete {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.image-item:hover .image-delete {
  opacity: 1;
}

.image-delete:hover {
  transform: scale(1.2);
  background: rgba(255, 0, 0, 0.1);
}

.drawer-right {
  width: 320px;
  flex-shrink: 0;
  overflow-y: auto;
  padding-left: 12px;
  border-left: 1px solid #e4e7ed;
}


/* 抽屉底部按钮 */
.drawer-footer {
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

/* 自定义滚动条 */
.drawer-left::-webkit-scrollbar,
.drawer-right::-webkit-scrollbar {
  width: 6px;
}

.drawer-left::-webkit-scrollbar-thumb,
.drawer-right::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.drawer-left::-webkit-scrollbar-thumb:hover,
.drawer-right::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .bug-drawer-content {
    flex-direction: column;
  }
  
  .drawer-right {
    width: 100%;
    border-left: none;
    border-top: 1px solid #e4e7ed;
    padding-left: 0;
    padding-top: 12px;
  }
}

</style>

