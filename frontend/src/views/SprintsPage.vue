<template>
  <div class="sprints-page">
    <!-- 搜索和操作栏 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Calendar /></el-icon>
          迭代管理
        </h2>
      </div>
      <div class="filter-row">
        <el-select
          v-model="searchProjectId"
          placeholder="选择项目"
          clearable
          @change="loadSprints"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1, width: '200px' }"
          :loading="!projects || projects.length === 0"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索迭代名称或负责人"
          clearable
          @keyup.enter="loadSprints"
          style="width: 280px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadSprints">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button 
          v-if="canCreate('projects')" 
          type="primary" 
          style="margin-left: auto"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新建迭代
        </el-button>
      </div>
    </el-card>

    <!-- 迭代列表 -->
    <el-card class="table-card">
      <el-table
        :data="paginatedSprints"
        v-loading="loading"
        style="width: 100%"
        stripe
      >
        <el-table-column label="编号" width="80" type="index" :index="(index) => (currentPage - 1) * pageSize + index + 1" align="center" />
        <el-table-column prop="name" label="名称" min-width="180" align="center" />
        <el-table-column label="项目" min-width="150" align="center">
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="goal" label="目标" min-width="200" align="center" show-overflow-tooltip />
        <el-table-column prop="owner" label="负责人" min-width="120" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row)" size="small">
              {{ getStatusLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="起始时间" width="120" align="center">
          <template #default="{ row }">
            {{ formatDate(row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_date" label="截止时间" width="120" align="center">
          <template #default="{ row }">
            {{ formatDate(row.end_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center" v-if="canUpdate('projects') || canDelete('projects')">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button 
                v-if="canUpdate('projects')" 
                link 
                type="primary" 
                size="small"
                @click="handleEdit(row)"
              >
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button 
                v-if="canDelete('projects')" 
                link 
                type="danger" 
                size="small"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, sizes, jumper, ->, total"
          :total="filteredSprints.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" width="600px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建迭代' ? '创建新迭代，设置迭代名称、目标、负责人和时间范围' : '修改迭代的配置信息' }}</span>
        </div>
      </template>
      <el-form :model="formData" label-width="100px">
        <el-form-item label="所属项目" required>
          <el-select
            v-model="formData.project_id"
            placeholder="选择项目"
            filterable
            style="width: 100%"
            :disabled="hasProjectSelected || !!editingId"
            :style="{ opacity: (hasProjectSelected || !!editingId) ? 0.6 : 1 }"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="formData.name" placeholder="请输入迭代名称" />
        </el-form-item>
        <el-form-item label="目标">
          <el-input 
            v-model="formData.goal" 
            type="textarea"
            :rows="3"
            placeholder="请输入迭代目标" 
          />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="formData.owner"
            placeholder="选择负责人"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.display_name || user.username"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="起始时间" required>
          <el-date-picker
            v-model="formData.start_date"
            type="date"
            placeholder="选择起始时间"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="截止时间" required>
          <el-date-picker
            v-model="formData.end_date"
            type="date"
            placeholder="选择截止时间"
            style="width: 100%"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, Calendar } from '@element-plus/icons-vue'
import * as sprintApi from '../api/sprints'
import * as projectApi from '../api/projects'
import * as userApi from '../api/users'
import type { Sprint, Project, User } from '../api/types'
import { usePermissions } from '../composables/usePermissions'
import { useProjectContext } from '../composables/useProjectContext'

const { canCreate, canUpdate, canDelete } = usePermissions()
const { getCurrentProjectId, hasProjectSelected, onProjectChanged, ensureInitialized } = useProjectContext()

const handleReset = () => {
  searchKeyword.value = ''
  if (!hasProjectSelected.value) {
    searchProjectId.value = undefined
  }
  currentPage.value = 1
  loadSprints()
}

const loadSprints = async () => {
  if (!isMounted) return
  loading.value = true
  try {
    const params: any = { limit: 1000 }
    // 优先使用当前选择的项目，否则使用搜索框中的项目
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
      // 同步搜索框的项目ID
      searchProjectId.value = getCurrentProjectId.value
    } else if (searchProjectId.value) {
      params.project_id = searchProjectId.value
    }
    sprints.value = await sprintApi.getSprints(params)
  } catch (error) {
    if (isMounted) {
      ElMessage.error('加载迭代失败')
    }
  } finally {
    if (isMounted) {
      loading.value = false
    }
  }
}

const sprints = ref<Sprint[]>([])
const projects = ref<Project[]>([])
const users = ref<User[]>([])
const searchKeyword = ref('')
const searchProjectId = ref<number | undefined>(undefined)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建迭代')
const editingId = ref<number>()

const formData = reactive({
  project_id: undefined as number | undefined,
  name: '',
  goal: '',
  owner: '',
  start_date: '',
  end_date: ''
})

const loadProjects = async () => {
  try {
    projects.value = await projectApi.getProjects({ limit: 1000 })
  } catch (error) {
    console.error('Failed to load projects:', error)
  }
}

const loadUsers = async () => {
  try {
    users.value = await userApi.getUsers({ status: 'active' })
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}

const handleCreate = () => {
  editingId.value = undefined
  dialogTitle.value = '新建迭代'
  Object.assign(formData, {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : undefined,
    name: '',
    goal: '',
    owner: '',
    start_date: '',
    end_date: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row: Sprint) => {
  editingId.value = row.id
  dialogTitle.value = '编辑迭代'
  // 如果已选择项目，使用当前项目ID；否则使用行数据中的项目ID
  const projectId = hasProjectSelected.value && getCurrentProjectId.value 
    ? getCurrentProjectId.value 
    : row.project_id
  Object.assign(formData, {
    project_id: projectId,
    name: row.name,
    goal: row.goal || '',
    owner: row.owner || '',
    start_date: row.start_date,
    end_date: row.end_date
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.project_id || !formData.name || !formData.start_date || !formData.end_date) {
    ElMessage.warning('请填写必填项：项目、名称、起始时间和截止时间')
    return
  }

  if (formData.end_date < formData.start_date) {
    ElMessage.warning('截止时间不能早于起始时间')
    return
  }

  try {
    if (editingId.value) {
      await sprintApi.updateSprint(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await sprintApi.createSprint(formData as any)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadSprints()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
  }
}

const handleDelete = async (row: Sprint) => {
  try {
    await ElMessageBox.confirm('确定删除此迭代吗？', '提示', { type: 'warning' })
    await sprintApi.deleteSprint(row.id)
    ElMessage.success('删除成功')
    loadSprints()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const getSprintStatus = (sprint: Sprint): 'not_started' | 'in_progress' | 'ended' => {
  if (!sprint.start_date || !sprint.end_date) {
    return 'not_started'
  }
  
  const now = new Date()
  const startDate = new Date(sprint.start_date)
  const endDate = new Date(sprint.end_date)
  
  // 设置时间为当天的 00:00:00，以便只比较日期
  now.setHours(0, 0, 0, 0)
  startDate.setHours(0, 0, 0, 0)
  endDate.setHours(0, 0, 0, 0)
  
  if (now < startDate) {
    return 'not_started'
  } else if (now >= startDate && now <= endDate) {
    return 'in_progress'
  } else {
    return 'ended'
  }
}

const getStatusLabel = (sprint: Sprint): string => {
  const status = getSprintStatus(sprint)
  const statusMap = {
    not_started: '未开始',
    in_progress: '进行中',
    ended: '已结束'
  }
  return statusMap[status]
}

const getStatusType = (sprint: Sprint): string | undefined => {
  const status = getSprintStatus(sprint)
  const typeMap: Record<string, string | undefined> = {
    not_started: 'info',
    in_progress: 'success',
    ended: 'warning'  // 使用 'warning' 代替空字符串，表示已结束的状态
  }
  return typeMap[status]
}

const filteredSprints = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) {
    return sprints.value
  }
  return sprints.value.filter((sprint) => {
    const name = (sprint.name || '').toLowerCase()
    const owner = (sprint.owner || '').toLowerCase()
    return name.includes(keyword) || owner.includes(keyword)
  })
})

const paginatedSprints = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredSprints.value.slice(start, start + pageSize.value)
})

let cleanupProjectChanged: (() => void) | null = null
let isMounted = false

onMounted(async () => {
  isMounted = true
  // 确保项目上下文已初始化
  await ensureInitialized()
  loadProjects()
  loadUsers()
  // 初始化时，如果已选择项目，设置搜索框的项目ID
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    searchProjectId.value = getCurrentProjectId.value
  }
  loadSprints()
  cleanupProjectChanged = onProjectChanged(() => {
    if (!isMounted) return
    // 项目切换时，更新搜索框的项目ID
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      searchProjectId.value = getCurrentProjectId.value
    } else {
      searchProjectId.value = undefined
    }
    loadSprints()
  })
})

onUnmounted(() => {
  isMounted = false
  if (cleanupProjectChanged) {
    cleanupProjectChanged()
  }
})

watch(() => getCurrentProjectId.value, (newVal, oldVal) => {
  // 避免初始化时重复加载
  if (newVal === oldVal) return
  // 当项目ID变化时，更新搜索框的项目ID
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    searchProjectId.value = getCurrentProjectId.value
  } else {
    searchProjectId.value = undefined
  }
  loadSprints()
}, { immediate: false })
</script>

<style scoped>
.sprints-page {
  animation: fadeIn 0.4s ease;
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

/* 统一表格行高 */
:deep(.el-table__body td) {
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
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
