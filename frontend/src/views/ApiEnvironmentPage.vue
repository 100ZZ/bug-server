<template>
  <div class="api-environment-page">
    <!-- 顶部：标题 + 搜索 + 新建按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Setting /></el-icon>
          环境管理
        </h2>
      </div>
      <div class="filter-row">
        <el-select 
          v-model="filters.project_id" 
          placeholder="选择项目" 
          clearable 
          @change="loadEnvironments"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
        >
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索环境名称或环境信息"
          clearable
          @keyup.enter="loadEnvironments"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadEnvironments">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建环境
        </el-button>
      </div>
    </el-card>

    <!-- 底部：环境列表 -->
    <el-card class="table-card">
      <el-table
        ref="environmentsTableRef"
        :data="paginatedEnvironments"
        v-loading="loading"
        stripe
        style="width: 100%"
        :max-height="600"
        row-key="id"
      >
        <el-table-column label="编号" width="80" type="index" :index="(index: number) => index + 1" align="center" />
        <el-table-column prop="project" label="项目" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="环境名称" align="center" show-overflow-tooltip />
        <el-table-column prop="description" label="环境说明" align="center" show-overflow-tooltip />
        <el-table-column prop="base_url" label="环境信息" align="center" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="handleEdit(row)">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button link type="danger" @click="handleDelete(row)">
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
          :total="environments.length"
        />
      </div>
    </el-card>

    <!-- 新建/编辑环境对话框 -->
    <el-dialog v-model="dialogVisible" width="700px" :close-on-click-modal="true">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建环境' ? '创建新的API测试环境，配置环境地址和公共请求头' : '修改API测试环境的配置信息' }}</span>
        </div>
      </template>
      <el-form :model="formData" label-width="100px">
        <el-form-item label="选择项目" required>
          <el-select 
            v-model="formData.project_id" 
            placeholder="选择项目" 
            style="width: 100%"
            :disabled="hasProjectSelected"
            :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
          >
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="环境名称" required>
          <el-input v-model="formData.name" placeholder="例如：开发环境、测试环境" />
        </el-form-item>
        <el-form-item label="环境信息" required>
          <el-input v-model="formData.base_url" placeholder="例如：http://192.168.100.186:48080" />
        </el-form-item>
        <el-form-item label="环境说明">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入环境说明（可选）" />
        </el-form-item>
        <el-form-item label="公共请求头">
          <el-input
            v-model="headersText"
            type="textarea"
            :rows="4"
            placeholder='JSON格式，例如：{"Content-Type": "application/json"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-start;">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, Setting } from '@element-plus/icons-vue'
import * as apitestApi from '../api/apitest'
import * as projectApi from '../api/projects'
import { useProjectContext } from '../composables/useProjectContext'
import type { ApiEnvironment, Project } from '../api/types'

const environments = ref<ApiEnvironment[]>([])
const projects = ref<Project[]>([])
const filters = reactive({
  project_id: undefined as number | undefined,
  keyword: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建环境')
const editingId = ref<number>()
const environmentsTableRef = ref()

const formData = reactive({
  project_id: 0,
  name: '',
  base_url: '',
  description: '',
  headers: undefined as Record<string, any> | undefined
})

const headersText = ref('')

const loadEnvironments = async () => {
  loading.value = true
  try {
    const params: any = {
      keyword: filters.keyword || undefined
    }
    
    // 优先使用当前项目过滤
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
    } else if (filters.project_id) {
      params.project_id = filters.project_id
    }
    
    environments.value = await apitestApi.getApiEnvironments(params)
  } catch (error: any) {
    ElMessage.error(error.message || '加载环境列表失败')
  } finally {
    loading.value = false
  }
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
  } catch (error: any) {
    ElMessage.error(error.message || '加载项目列表失败')
  }
}

const handleReset = () => {
  filters.project_id = undefined
  filters.keyword = ''
  loadEnvironments()
}

const handleCreate = async () => {
  await loadProjects()
  
  if (projects.value.length === 0) {
    ElMessage.warning('请先创建项目')
    return
  }
  
  editingId.value = undefined
  dialogTitle.value = '新建环境'
  Object.assign(formData, {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : (filters.project_id || projects.value[0].id),
    name: '',
    base_url: '',
    description: '',
    headers: undefined
  })
  headersText.value = ''
  dialogVisible.value = true
}

const handleEdit = (row: ApiEnvironment) => {
  editingId.value = row.id
  dialogTitle.value = '编辑环境'
  Object.assign(formData, {
    project_id: row.project_id,
    name: row.name,
    base_url: row.base_url,
    description: row.description || '',
    headers: row.headers
  })
  headersText.value = row.headers ? JSON.stringify(row.headers, null, 2) : ''
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.project_id || !formData.name || !formData.base_url) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    if (headersText.value.trim()) {
      formData.headers = JSON.parse(headersText.value)
    } else {
      formData.headers = undefined
    }
  } catch (error) {
    ElMessage.error('请求头JSON格式错误')
    return
  }

  try {
    if (editingId.value) {
      await apitestApi.updateApiEnvironment(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await apitestApi.createApiEnvironment(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadEnvironments()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

const handleDelete = async (row: ApiEnvironment) => {
  try {
    await ElMessageBox.confirm('确定删除该环境吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await apitestApi.deleteApiEnvironment(row.id)
    ElMessage.success('删除成功')
    loadEnvironments()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const paginatedEnvironments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return environments.value.slice(start, start + pageSize.value)
})

// 监听分页变化，重新布局表格
watch(currentPage, async () => {
  await nextTick()
  if (environmentsTableRef.value) {
    environmentsTableRef.value.doLayout()
  }
})

onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 如果有选中的项目，自动设置过滤器
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    filters.project_id = getCurrentProjectId.value
  }
  loadProjects()
  loadEnvironments()
  
  // 监听项目切换事件
  const cleanup = onProjectChanged(() => {
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.project_id = getCurrentProjectId.value
    }
    loadProjects()
    loadEnvironments()
  })
  
  // 组件卸载时清理监听
  onUnmounted(() => {
    cleanup()
  })
})
</script>

<style scoped>
.api-environment-page {
  height: 100%;
  animation: fadeIn 0.5s ease-in;
  padding: 0;
  box-sizing: border-box;
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
}

:deep(.el-table__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

:deep(.el-table__header th) {
  background: transparent;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
  padding: 16px 0;
}

:deep(.el-table__body tr) {
  transition: all 0.2s ease;
}

:deep(.el-table__body tr:hover) {
  background: #f8f9ff !important;
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

:deep(.el-table__body td) {
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped) {
  background: #fafbfc;
}

:deep(.el-tag) {
  border-radius: 6px;
  font-weight: 500;
  padding: 4px 12px;
  border: none;
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
