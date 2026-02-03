<template>
  <div class="projects-page">
    <!-- 搜索和操作栏 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><FolderOpened /></el-icon>
          项目管理
        </h2>
      </div>
      <div class="filter-row">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索项目名称或负责人"
          clearable
          @keyup.enter="loadProjects"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadProjects">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button 
          v-if="canCreate('projects')" 
          type="primary" 
          style="margin-left: auto"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新建项目
        </el-button>
      </div>
    </el-card>

    <!-- 项目列表 -->
    <el-card class="table-card">
      <el-table
        :data="paginatedProjects"
        v-loading="loading"
        style="width: 100%"
        stripe
      >
      <el-table-column label="编号" width="80" type="index" :index="(index) => (currentPage - 1) * pageSize + index + 1" align="center" />
      <el-table-column prop="name" label="项目名称" min-width="180" align="center" />
      <el-table-column prop="key" label="简称" min-width="180" align="center" />
      <el-table-column prop="lead" label="负责人" min-width="120" align="center" />
      <el-table-column label="项目成员" min-width="200" align="center">
        <template #default="{ row }">
          <div class="member-tags">
            <el-tag v-for="member in (row.members || [])" :key="member.id" size="small" type="info">
              {{ member.display_name || member.username }}
            </el-tag>
            <span v-if="!row.members || row.members.length === 0" class="text-muted">暂无成员</span>
          </div>
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
          :total="filteredProjects.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" width="600px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建项目' ? '创建新项目，设置项目名称、负责人和成员信息' : '修改项目的配置信息和成员列表' }}</span>
        </div>
      </template>
      <el-form :model="formData" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="简称">
          <el-input 
            v-model="formData.key" 
            placeholder="请输入简称" 
          />
        </el-form-item>
        <el-form-item label="负责人">
          <el-select
            v-model="formData.lead"
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
        <el-form-item label="项目成员">
          <el-select
            v-model="formData.member_ids"
            placeholder="选择项目成员（可多选）"
            multiple
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.display_name || user.username"
              :value="user.id"
            />
          </el-select>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, FolderOpened } from '@element-plus/icons-vue'
import * as projectApi from '../api/projects'
import * as userApi from '../api/users'
import type { Project, User } from '../api/types'
import { usePermissions } from '../composables/usePermissions'

const handleReset = () => {
  searchKeyword.value = ''
  currentPage.value = 1
}

const loadProjects = async () => {
  loading.value = true
  try {
    projects.value = await projectApi.getProjects({ limit: 1000 })
  } finally {
    loading.value = false
  }
}

const { canCreate, canUpdate, canDelete } = usePermissions()

const projects = ref<Project[]>([])
const users = ref<User[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建项目')
const editingId = ref<number>()

const formData = reactive({
  name: '',
  key: '',
  lead: '',
  member_ids: [] as number[]
})

const loadUsers = async () => {
  try {
    users.value = await userApi.getUsers({ status: 'active' })
  } catch (error) {
    // 忽略错误，避免影响项目列表加载
  }
}

const handleCreate = () => {
  editingId.value = undefined
  dialogTitle.value = '新建项目'
  Object.assign(formData, { name: '', key: '', lead: '', member_ids: [] })
  dialogVisible.value = true
}

const handleEdit = (row: Project) => {
  editingId.value = row.id
  dialogTitle.value = '编辑项目'
  Object.assign(formData, {
    name: row.name,
    key: row.key || '',
    lead: row.lead || '',
    member_ids: row.member_ids || (row.members ? row.members.map(m => m.id) : [])
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.name) {
    ElMessage.warning('请填写项目名称')
    return
  }

  try {
    if (editingId.value) {
      await projectApi.updateProject(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await projectApi.createProject(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadProjects()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
  }
}

const handleDelete = async (row: Project) => {
  try {
    await ElMessageBox.confirm('确定删除此项目吗？', '提示', { type: 'warning' })
    await projectApi.deleteProject(row.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const filteredProjects = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) {
    return projects.value
  }
  return projects.value.filter((project) => {
    const name = (project.name || '').toLowerCase()
    const lead = (project.lead || '').toLowerCase()
    return name.includes(keyword) || lead.includes(keyword)
  })
})

const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredProjects.value.slice(start, start + pageSize.value)
})

onMounted(() => {
  loadProjects()
  loadUsers()
})
</script>

<style scoped>
.projects-page {
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

.member-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.text-muted {
  color: #909399;
  font-size: 14px;
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

