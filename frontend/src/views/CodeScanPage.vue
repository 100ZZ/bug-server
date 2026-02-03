<template>
  <div class="code-scan-page">
    <!-- 顶部：标题 + 搜索 + 新建按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><DocumentCopy /></el-icon>
          代码扫描
        </h2>
      </div>
      <div class="filter-row">
        <el-select 
          v-model="filters.project_id" 
          placeholder="选择项目" 
          clearable 
          @change="loadScans" 
          style="width: 200px"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
        >
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索工程、分支或扫描路径"
          clearable
          @keyup.enter="loadScans"
          style="width: 300px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadScans">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增任务
        </el-button>
      </div>
    </el-card>

    <!-- 底部：扫描任务列表 -->
    <el-card class="table-card">
      <el-table
        :data="paginatedScans"
        v-loading="loading"
        stripe
        style="width: 100%"
        :max-height="600"
        row-key="id"
      >
        <el-table-column label="编号" width="80" type="index" :index="(index: number) => index + 1" align="center" />
        <el-table-column prop="project" label="项目" show-overflow-tooltip align="center">
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="工程" show-overflow-tooltip align="center" />
        <el-table-column prop="branch" label="分支" show-overflow-tooltip align="center" />
        <el-table-column prop="language" label="编程语言" width="120" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.language || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="scan_path" label="扫描路径" show-overflow-tooltip align="center" />
        <el-table-column prop="sonar_host" label="Sonar Host" show-overflow-tooltip align="center">
          <template #default="{ row }">
            {{ row.sonar_host || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="scanningIds.has(row.id)" type="warning">扫描中</el-tag>
            <el-tag v-else-if="row.result === 'passed'" type="success">通过</el-tag>
            <el-tooltip 
              v-else-if="row.result === 'failed'" 
              :content="truncateText(row.error_message || '扫描不通过', 100)" 
              placement="top"
              :show-after="300"
            >
              <el-tag type="danger" style="cursor: help;">不通过</el-tag>
            </el-tooltip>
            <el-tag v-else type="info">未扫描</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <div class="action-row">
                <el-button link type="primary" @click="handleEdit(row)">
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button link type="danger" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
              <div class="action-row">
                <el-button 
                  v-if="scanningIds.has(row.id)" 
                  link 
                  type="danger" 
                  @click="handleStopScan(row)"
                >
                  <el-icon><VideoPause /></el-icon>
                  停止
                </el-button>
                <el-button 
                  v-else 
                  link 
                  type="primary" 
                  @click="handleScan(row)"
                >
                  <el-icon><VideoPlay /></el-icon>
                  扫描
                </el-button>
                <el-button link type="primary" @click="handleViewDetail(row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
              </div>
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
          :total="scans.length"
        />
      </div>
    </el-card>

    <!-- 扫描详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="扫描详情"
      direction="rtl"
      size="72%"
      class="scan-detail-drawer"
    >
      <template #header>
        <div class="drawer-header-inner">
          <div class="drawer-header-left">
            <el-icon class="drawer-header-icon"><View /></el-icon>
            <div>
              <span class="drawer-title">扫描详情</span>
              <span class="drawer-subtitle" v-if="detailRow">{{ detailRow.project_name }} / {{ detailRow.branch }}</span>
            </div>
          </div>
          <a
            v-if="detailRow && detailRow.sonar_host"
            href="javascript:void(0)"
            class="drawer-sonar-link"
            @click.prevent="openSonarPage(detailRow)"
          >
            <el-icon><Link /></el-icon>
            <span>打开 Sonar</span>
          </a>
          <span v-else-if="detailRow" class="drawer-sonar-disabled">未配置 Sonar</span>
        </div>
      </template>
      <div v-if="detailRow" class="detail-content">
        <!-- 基本信息卡片 -->
        <el-card class="detail-card detail-card-info" shadow="never">
          <template #header>
            <span class="card-header-text">基本信息</span>
          </template>
          <el-descriptions :column="1" border size="default" class="detail-descriptions">
            <el-descriptions-item label="工程">{{ detailRow.project_name }}</el-descriptions-item>
            <el-descriptions-item label="分支">{{ detailRow.branch }}</el-descriptions-item>
            <el-descriptions-item label="Sonar Host">
              <span class="text-ellipsis">{{ detailRow.sonar_host || '-' }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="扫描结果">
              <el-tag v-if="detailRow.result === 'passed'" type="success" size="default" effect="light" round>通过</el-tag>
              <el-tag v-else-if="detailRow.result === 'failed'" type="danger" size="default" effect="light" round>不通过</el-tag>
              <el-tag v-else type="info" size="default" effect="light" round>未扫描</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="扫描时间">
              <span class="time-text">{{ detailRow.scan_time ? formatScanTime(detailRow.scan_time) : '-' }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 不通过信息卡片 -->
        <el-card
          v-if="detailRow.result === 'failed' && (detailRow.error_message || detailConditions.length)"
          class="detail-card detail-card-error"
          shadow="never"
        >
          <template #header>
            <span class="card-header-text">不通过信息</span>
          </template>
          <div v-if="detailRow.error_message" class="error-block">
            <div class="error-label">错误信息</div>
            <pre class="error-message">{{ detailRow.error_message }}</pre>
          </div>
          <div v-if="detailConditions.length" class="conditions-block">
            <div class="conditions-label">未通过条件</div>
            <ul class="conditions-list">
              <li v-for="(c, i) in detailConditions" :key="i">
                {{ c.metric_name }}: {{ c.actual_value }}（要求 {{ c.comparator }}{{ c.error_threshold }}）
              </li>
            </ul>
          </div>
        </el-card>

        <!-- 历史记录卡片（分页） -->
        <el-card class="detail-card detail-card-history" shadow="never">
          <template #header>
            <div class="history-card-header">
              <span class="card-header-text">历史记录</span>
              <span class="history-total" v-if="!historyLoading && detailHistories.length > 0">共 {{ detailHistories.length }} 条</span>
            </div>
          </template>
          <div v-if="historyLoading" class="history-loading">
            <el-skeleton :rows="4" animated />
          </div>
          <div v-else-if="detailHistories.length === 0" class="history-empty">
            <el-empty description="暂无历史记录" :image-size="80" />
          </div>
          <template v-else>
            <el-timeline class="history-timeline">
              <el-timeline-item
                v-for="h in paginatedHistories"
                :key="h.id"
                :type="h.status === 'completed' ? 'success' : (h.status === 'failed' ? 'danger' : 'info')"
              >
                <div class="history-item">
                  <div class="history-item-top">
                    <el-tag
                      :type="h.status === 'completed' ? 'success' : (h.status === 'failed' ? 'danger' : 'info')"
                      size="small"
                      effect="light"
                    >
                      {{ h.status === 'completed' ? '通过' : (h.status === 'failed' ? '不通过' : '待处理') }}
                    </el-tag>
                    <span class="history-time">{{ h.created_at ? formatScanTime(h.created_at) : '-' }}</span>
                  </div>
                  <div v-if="h.error_message" class="history-error">
                    {{ truncateText(h.error_message, 120) }}
                  </div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <div class="history-pagination">
              <el-pagination
                v-model:current-page="historyPage"
                :page-size="historyPageSize"
                :total="detailHistories.length"
                layout="prev, pager, next, total"
                small
              />
            </div>
          </template>
        </el-card>

      </div>
    </el-drawer>

    <!-- 新建/编辑扫描任务对话框 -->
    <el-dialog v-model="dialogVisible" width="700px" :close-on-click-modal="true">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建任务' ? '创建新的代码扫描任务配置，用于跳转到SonarQube查看扫描结果' : '修改代码扫描任务的配置信息' }}</span>
        </div>
      </template>
      <el-form :model="formData" label-width="120px">
        <el-form-item label="选择项目" required>
          <el-select 
            v-model="formData.project_id" 
            placeholder="选择项目" 
            style="width: 100%"
            @change="loadEnvironments(formData.project_id)"
            :disabled="hasProjectSelected"
            :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
          >
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="工程名称" required>
          <el-input v-model="formData.project_name" placeholder="请输入工程名称" />
        </el-form-item>
        <el-form-item label="分支" required>
          <el-input v-model="formData.branch" placeholder="例如：main、develop" />
        </el-form-item>
        <el-form-item label="扫描路径">
          <el-input v-model="formData.scan_path" placeholder="例如：/path/to/code（可选）" />
        </el-form-item>
        <el-form-item label="编程语言">
          <el-select v-model="formData.language" placeholder="请选择编程语言" clearable style="width: 100%">
            <el-option 
              v-for="lang in languageOptions" 
              :key="lang.value" 
              :label="lang.label" 
              :value="lang.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Sonar Project" class="form-item-no-wrap">
          <el-input v-model="formData.sonar_project_key" placeholder="Sonar中的项目Key，例如：my-project" />
        </el-form-item>
        <el-form-item label="Sonar Host" required>
          <el-select 
            v-model="formData.sonar_host" 
            placeholder="从环境列表选择或手动输入" 
            filterable
            allow-create
            default-first-option
            style="width: 100%"
          >
            <el-option 
              v-for="env in environments" 
              :key="env.id" 
              :label="`${env.name} (${env.base_url})${env.description ? ' - ' + env.description : ''}`" 
              :value="env.base_url" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Sonar Login">
          <el-input v-model="formData.sonar_login" type="password" show-password placeholder="Sonar登录Token（可选）" />
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
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, DocumentCopy, Link, VideoPlay, VideoPause, View } from '@element-plus/icons-vue'
import * as codeScanApi from '../api/codescan'
import type { ScanExecuteResult, CodeScanResultHistory } from '../api/codescan'
import * as projectApi from '../api/projects'
import * as apitestApi from '../api/apitest'
import { useProjectContext } from '../composables/useProjectContext'
import type { CodeScan, Project, ApiEnvironment } from '../api/types'


const scans = ref<CodeScan[]>([])
const projects = ref<Project[]>([])
const environments = ref<ApiEnvironment[]>([])
const scanningIds = ref<Set<number>>(new Set()) // 正在扫描中的任务ID
const filters = reactive({
  project_id: undefined as number | undefined,
  keyword: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增任务')
const editingId = ref<number>()

// 详情抽屉
const detailDrawerVisible = ref(false)
const detailRow = ref<CodeScan | null>(null)
// 最近一次执行结果（含 conditions），用于详情抽屉展示
const lastExecuteResultMap = ref<Record<number, ScanExecuteResult>>({})
// 历史记录
const detailHistories = ref<CodeScanResultHistory[]>([])
const historyLoading = ref(false)
const historyPage = ref(1)
const historyPageSize = 5

// 编程语言选项
// 截断文本
const truncateText = (text: string, maxLength: number): string => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 格式化扫描时间
const formatScanTime = (t: string): string => {
  if (!t) return '-'
  try {
    const d = new Date(t)
    return isNaN(d.getTime()) ? t : d.toLocaleString('zh-CN')
  } catch {
    return t
  }
}

// 详情抽屉中展示的不通过条件（优先用最近一次执行返回的 conditions）
const detailConditions = computed(() => {
  const row = detailRow.value
  if (!row) return []
  const last = lastExecuteResultMap.value[row.id]
  if (last?.conditions?.length) return last.conditions
  return []
})

// 历史记录分页（每页 10 条）
const paginatedHistories = computed(() => {
  const list = detailHistories.value
  const start = (historyPage.value - 1) * historyPageSize
  return list.slice(start, start + historyPageSize)
})

const languageOptions = [
  { label: 'Java', value: 'Java' },
  { label: 'Python', value: 'Python' },
  { label: 'Go', value: 'Go' },
  { label: 'PHP', value: 'PHP' },
  { label: 'JavaScript', value: 'JavaScript' },
  { label: 'TypeScript', value: 'TypeScript' },
  { label: 'C++', value: 'C++' },
  { label: 'C#', value: 'C#' },
  { label: 'Ruby', value: 'Ruby' },
  { label: 'Kotlin', value: 'Kotlin' }
]

const formData = reactive({
  project_id: 0,
  project_name: '',
  branch: '',
  scan_path: '',
  language: '',
  sonar_project_key: '',
  sonar_host: '',
  sonar_login: ''
})

const loadScans = async () => {
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
    
    scans.value = await codeScanApi.getCodeScans(params)
  } catch (error: any) {
    ElMessage.error(error.message || '加载扫描任务列表失败')
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

const loadEnvironments = async (projectId?: number) => {
  try {
    if (projectId) {
      environments.value = await apitestApi.getApiEnvironments({ project_id: projectId })
    } else {
      environments.value = []
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载环境列表失败')
    environments.value = []
  }
}

const handleReset = () => {
  filters.project_id = undefined
  filters.keyword = ''
  loadScans()
}

const handleCreate = async () => {
  await loadProjects()
  
  if (projects.value.length === 0) {
    ElMessage.warning('请先创建项目')
    return
  }
  
  editingId.value = undefined
  dialogTitle.value = '新增任务'
  const selectedProjectId = hasProjectSelected.value ? getCurrentProjectId.value : (filters.project_id || projects.value[0].id)
  await loadEnvironments(selectedProjectId)
  Object.assign(formData, {
    project_id: selectedProjectId,
    project_name: '',
    branch: '',
    scan_path: '',
    language: '',
    sonar_project_key: '',
    sonar_host: '',
    sonar_login: ''
  })
  dialogVisible.value = true
}

const handleEdit = async (row: CodeScan) => {
  editingId.value = row.id
  dialogTitle.value = '编辑任务'
  await loadEnvironments(row.project_id)
  Object.assign(formData, {
    project_id: row.project_id,
    project_name: row.project_name,
    branch: row.branch,
    scan_path: row.scan_path || '',
    language: row.language || '',
    sonar_project_key: row.sonar_project_key || '',
    sonar_host: row.sonar_host || '',
    sonar_login: row.sonar_login || ''
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.project_id || !formData.project_name || !formData.branch) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    if (editingId.value) {
      await codeScanApi.updateCodeScan(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await codeScanApi.createCodeScan(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadScans()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

const handleDelete = async (row: CodeScan) => {
  try {
    await ElMessageBox.confirm('确定删除该扫描任务吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await codeScanApi.deleteCodeScan(row.id)
    ElMessage.success('删除成功')
    loadScans()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 执行扫描
const handleScan = async (row: CodeScan) => {
  if (!row.sonar_host) {
    ElMessage.warning('请先配置 Sonar Host')
    return
  }
  
  scanningIds.value.add(row.id)
  ElMessage.info('正在查询 SonarQube 扫描状态...')
  
  try {
    const result = await codeScanApi.executeCodeScan(row.id)
    lastExecuteResultMap.value[row.id] = result

    if (result.result === 'passed') {
      ElMessage.success('扫描通过')
    } else if (result.result === 'failed') {
      const tip = result.error_message ? truncateText(result.error_message, 80) : '质量门未通过，请点「详情」或到 Sonar 控制台查看'
      ElMessage.warning('扫描不通过：' + tip)
    }

    // 刷新列表
    await loadScans()
  } catch (error: any) {
    ElMessage.error(error.message || '查询扫描状态失败')
    await loadScans()
  } finally {
    scanningIds.value.delete(row.id)
  }
}

// 停止扫描
const handleStopScan = (row: CodeScan) => {
  scanningIds.value.delete(row.id)
  ElMessage.info('已取消查询')
}

// 加载扫描历史记录
const loadScanHistory = async (scanId: number) => {
  historyLoading.value = true
  try {
    detailHistories.value = await codeScanApi.getCodeScanResults(scanId)
  } catch (error: any) {
    ElMessage.error(error.message || '加载扫描历史失败')
    detailHistories.value = []
  } finally {
    historyLoading.value = false
  }
}

// 查看详情（打开抽屉，可再点击转到 Sonar 页面）
const handleViewDetail = (row: CodeScan) => {
  detailRow.value = row
  historyPage.value = 1
  detailDrawerVisible.value = true
  if (row.id) {
    loadScanHistory(row.id)
  }
}

// 打开Sonar页面
const openSonarPage = (row: CodeScan) => {
  if (!row.sonar_host) {
    ElMessage.warning('请先配置 Sonar Host')
    return
  }
  
  const host = row.sonar_host.endsWith('/') ? row.sonar_host.slice(0, -1) : row.sonar_host
  const projectKey = row.sonar_project_key || `${row.project_name}:${row.branch}`
  const url = `${host}/dashboard?id=${encodeURIComponent(projectKey)}`
  window.open(url, '_blank')
}

const paginatedScans = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return scans.value.slice(start, start + pageSize.value)
})

onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 如果有选中的项目，自动设置过滤器
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    filters.project_id = getCurrentProjectId.value
  }
  loadProjects()
  loadScans()
  
  // 监听项目切换事件
  const cleanup = onProjectChanged(() => {
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.project_id = getCurrentProjectId.value
    }
    // 项目切换时重新加载项目列表和数据
  loadProjects()
  loadScans()
  })
  
  // 组件卸载时清理监听
  onUnmounted(() => {
    cleanup()
  })
})
</script>

<style scoped>
.code-scan-page {
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
  display: flex;
  align-items: center;
  gap: 8px;
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
}

.table-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.action-row {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
}

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

:deep(.el-table__body tr:hover) {
  background: #f8f9ff !important;
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

/* 统一表格行高 */
:deep(.el-table__body td) {
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
}

/* 防止Sonar ProjectKey标签换行 */
:deep(.form-item-no-wrap .el-form-item__label) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

/* 扫描详情抽屉 */
.scan-detail-drawer :deep(.el-drawer__header) {
  margin-bottom: 0;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.scan-detail-drawer :deep(.el-drawer__body) {
  overflow: hidden;
  display: flex;
  flex-direction: column;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.scan-detail-drawer :deep(.el-drawer__body)::-webkit-scrollbar {
  display: none;
}

.scan-detail-drawer .drawer-header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding-right: 8px;
}

.scan-detail-drawer .drawer-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.scan-detail-drawer .drawer-header-icon {
  font-size: 24px;
  color: #667eea;
  flex-shrink: 0;
}

.scan-detail-drawer .drawer-sonar-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 13px;
  color: #667eea;
  text-decoration: none;
  border-radius: 8px;
  transition: background 0.2s, color 0.2s;
  flex-shrink: 0;
}

.scan-detail-drawer .drawer-sonar-link:hover {
  background: rgba(102, 126, 234, 0.08);
  color: #5a6fd6;
}

.scan-detail-drawer .drawer-sonar-link .el-icon {
  font-size: 16px;
}

.scan-detail-drawer .drawer-sonar-disabled {
  font-size: 13px;
  color: #c0c4cc;
  flex-shrink: 0;
}

.scan-detail-drawer .drawer-title {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.scan-detail-drawer .drawer-subtitle {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.detail-content {
  padding: 0 4px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.detail-content::-webkit-scrollbar {
  display: none;
}

.detail-card {
  border-radius: 12px;
  border: 1px solid #ebeef5;
}

.detail-card :deep(.el-card__header) {
  padding: 14px 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #f8f9fc 0%, #f0f2f8 100%);
  border-bottom: 1px solid #ebeef5;
}

.detail-card :deep(.el-card__body) {
  padding: 20px;
}

.card-header-text {
  font-size: 15px;
  color: #303133;
}

.detail-descriptions {
  margin: 0;
}

.detail-descriptions :deep(.el-descriptions__label) {
  width: 100px;
  color: #606266;
  font-weight: 500;
}

.detail-content .text-ellipsis {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}

.time-text {
  font-size: 14px;
  color: #606266;
}

.error-block,
.conditions-block {
  margin-bottom: 16px;
}

.error-block:last-child,
.conditions-block:last-child {
  margin-bottom: 0;
}

.error-label,
.conditions-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
}

.error-message {
  margin: 0;
  padding: 12px;
  background: #fef0f0;
  border: 1px solid #fde2e2;
  border-radius: 8px;
  font-size: 13px;
  color: #c45656;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.conditions-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.history-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.history-total {
  font-size: 13px;
  font-weight: 400;
  color: #909399;
}

.history-loading {
  padding: 8px 0;
}

.history-empty {
  padding: 24px 0;
}

.history-timeline {
  margin: 0 0 16px;
  padding-left: 8px;
}

.history-timeline :deep(.el-timeline-item__timestamp) {
  display: none;
}

.history-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.history-time {
  font-size: 13px;
  color: #909399;
}

.history-error {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  padding-left: 0;
}

.history-pagination {
  display: flex;
  justify-content: center;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}
</style>
