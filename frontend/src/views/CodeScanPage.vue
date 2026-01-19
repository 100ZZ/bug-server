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
        <el-select v-model="filters.result" placeholder="扫描结果" clearable @change="loadScans" style="width: 150px">
          <el-option label="通过" value="passed" />
          <el-option label="不通过" value="failed" />
        </el-select>
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
        <el-table-column label="编号" width="80" type="index" :index="(index: number) => index + 1" />
        <el-table-column prop="project" label="项目" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="工程" show-overflow-tooltip />
        <el-table-column prop="branch" label="分支" show-overflow-tooltip />
        <el-table-column prop="language" label="编程语言" width="120" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.language || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="scan_path" label="扫描路径" show-overflow-tooltip />
        <el-table-column prop="scan_time" label="扫描时间" width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatDate(row.scan_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="result" label="扫描结果" width="120" align="center">
          <template #default="{ row }">
            <el-popover
              placement="top"
              :width="400"
              trigger="hover"
              v-if="getScanStatus(row) === 'scanning' || (getScanStatus(row) === 'failed' && getScanErrorMessage(row))"
            >
              <template #reference>
                <el-tag :type="getResultTagType(row)">
                  {{ getResultText(row) }}
                </el-tag>
              </template>
              <div class="scan-detail-popover">
                <div class="detail-title">扫描详情</div>
                <div class="detail-content">
                  <div v-if="getScanStatus(row) === 'scanning'">
                    <div><strong>状态：</strong>扫描中</div>
                    <div style="margin-top: 8px; color: #909399;">请稍候，扫描完成后将显示结果...</div>
                  </div>
                  <div v-else-if="getScanStatus(row) === 'failed' && getScanErrorMessage(row)">
                    <div><strong>状态：</strong>扫描失败</div>
                    <div style="margin-top: 8px;"><strong>错误信息：</strong></div>
                    <div style="margin-top: 4px; color: #f56c6c; white-space: pre-wrap; font-size: 12px; max-height: 300px; overflow-y: auto;">
                      {{ getScanErrorMessage(row) }}
                    </div>
                  </div>
                </div>
              </div>
            </el-popover>
            <el-tag v-else :type="getResultTagType(row)">
              {{ getResultText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <div class="action-row">
              <el-button link type="primary" @click="handleScan(row)" :loading="row.scanning">
                <el-icon><VideoPlay /></el-icon>
                扫描
              </el-button>
              <el-button link type="primary" @click="handleViewDetail(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              </div>
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

    <!-- 新建/编辑扫描任务对话框 -->
    <el-dialog v-model="dialogVisible" width="700px" :close-on-click-modal="true">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建任务' ? '创建新的代码扫描任务，配置扫描参数和SonarQube连接信息' : '修改代码扫描任务的配置信息' }}</span>
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
        <el-form-item label="扫描路径" required>
          <el-input v-model="formData.scan_path" placeholder="例如：/path/to/code" />
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
          <el-input v-model="formData.sonar_project_key" placeholder="例如：Mysterious" />
        </el-form-item>
        <el-form-item label="Sonar Host">
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
          <el-input v-model="formData.sonar_login" type="password" show-password placeholder="Sonar登录Token" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-start;">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailDrawerVisible"
      title="扫描结果详情"
      :size="'80%'"
      :close-on-click-modal="true"
    >
      <div v-if="detailLoading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else-if="detailResult && currentDetailScan" class="result-detail-content">
        <!-- 顶部操作栏 -->
        <div class="detail-header-actions">
          <el-button 
            v-if="detailSonarUrl"
            type="primary" 
            @click="openDetailSonarPage"
          >
            <el-icon><Link /></el-icon>
            查看Sonar详情
          </el-button>
        </div>

        <!-- 扫描基本信息 -->
        <el-descriptions :column="2" border class="info-section">
          <el-descriptions-item label="项目">{{ currentDetailScan.project?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工程">{{ currentDetailScan.project_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分支">{{ currentDetailScan.branch || '-' }}</el-descriptions-item>
          <el-descriptions-item label="扫描路径">{{ currentDetailScan.scan_path || '-' }}</el-descriptions-item>
          <el-descriptions-item label="扫描时间">{{ formatDate(currentDetailScan.scan_time) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getDetailStatusType(detailResult.status)">
              {{ getDetailStatusText(detailResult.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 扫描指标 - SonarQube Overview 风格 -->
        <div v-if="detailResult.metrics" class="metrics-section">
          <h3>扫描指标</h3>
          
          <div class="metrics-overview-container">
            <!-- 左列：总体项目指标 -->
            <div class="metrics-column">
              <!-- Bugs & Vulnerabilities -->
              <div class="overview-row">
                <div class="overview-row-header">
                  <span class="overview-title">Bugs & Vulnerabilities</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">🐛</span>
                      Bugs
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.bugs, 'bugs')">
                      {{ detailResult.metrics.bugs || 0 }}
                    </div>
                  </div>
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">🔒</span>
                      Vulnerabilities
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.vulnerabilities, 'vulnerabilities')">
                      {{ detailResult.metrics.vulnerabilities || 0 }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Code Smells -->
              <div class="overview-row">
                <div class="overview-row-header">
                  <span class="overview-title">Code Smells</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">💀</span>
                      Code Smells
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.code_smells, 'code_smells')">
                      {{ detailResult.metrics.code_smells || 0 }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Coverage -->
              <div class="overview-row">
                <div class="overview-row-header">
                  <span class="overview-title">Coverage</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">📊</span>
                      Coverage
                    </div>
                    <div class="overview-metric-value" :class="getDetailCoverageClass(detailResult.metrics.coverage)">
                      {{ detailResult.metrics.coverage ? `${detailResult.metrics.coverage}%` : '0.0%' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Duplications -->
              <div class="overview-row">
                <div class="overview-row-header">
                  <span class="overview-title">Duplications</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">📋</span>
                      Duplications
                    </div>
                    <div class="overview-metric-value" :class="getDetailDuplicationClass(detailResult.metrics.duplicated_lines_density)">
                      {{ detailResult.metrics.duplicated_lines_density ? `${detailResult.metrics.duplicated_lines_density}%` : '0.0%' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 右列：新代码指标 -->
            <div class="metrics-column metrics-column-new">
              <!-- New Bugs & New Vulnerabilities -->
              <div class="overview-row overview-row-new">
                <div class="overview-row-header overview-row-header-new">
                  <span class="overview-title">Bugs & Vulnerabilities</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">🐛</span>
                      New Bugs
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.new_bugs, 'new_bugs')">
                      {{ detailResult.metrics.new_bugs ?? '-' }}
                    </div>
                  </div>
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">🔒</span>
                      New Vulnerabilities
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.new_vulnerabilities, 'new_vulnerabilities')">
                      {{ detailResult.metrics.new_vulnerabilities ?? '-' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- New Code Smells -->
              <div class="overview-row overview-row-new">
                <div class="overview-row-header overview-row-header-new">
                  <span class="overview-title">Code Smells</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">💀</span>
                      New Debt
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.new_technical_debt ? 1 : 0, 'new_debt')">
                      {{ detailResult.metrics.new_technical_debt ? formatTechnicalDebt(detailResult.metrics.new_technical_debt) : '0' }}
                    </div>
                  </div>
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">💀</span>
                      New Code Smells
                    </div>
                    <div class="overview-metric-value" :class="getDetailMetricClass(detailResult.metrics.new_code_smells, 'new_code_smells')">
                      {{ detailResult.metrics.new_code_smells ?? '-' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Coverage on New Code -->
              <div class="overview-row overview-row-new">
                <div class="overview-row-header overview-row-header-new">
                  <span class="overview-title">Coverage</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">📊</span>
                      Coverage on New Code
                    </div>
                    <div class="overview-metric-value" :class="getDetailCoverageClass(detailResult.metrics.new_coverage)">
                      {{ detailResult.metrics.new_coverage !== undefined && detailResult.metrics.new_coverage !== null ? `${detailResult.metrics.new_coverage}%` : '—' }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Duplications on New Code -->
              <div class="overview-row overview-row-new">
                <div class="overview-row-header overview-row-header-new">
                  <span class="overview-title">Duplications</span>
                </div>
                <div class="overview-row-content">
                  <div class="overview-metric">
                    <div class="overview-metric-label">
                      <span class="overview-icon">📋</span>
                      Duplications on New Code
                    </div>
                    <div class="overview-metric-value" :class="getDetailDuplicationClass(detailResult.metrics.new_duplicated_lines_density)">
                      {{ detailResult.metrics.new_duplicated_lines_density !== undefined && detailResult.metrics.new_duplicated_lines_density !== null ? `${detailResult.metrics.new_duplicated_lines_density}%` : '—' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 扫描详细过程 -->
        <div v-if="detailResult.scan_output" class="scan-output-section">
          <h3>扫描详细过程</h3>
          <pre class="scan-output-content">{{ detailResult.scan_output }}</pre>
        </div>

        <!-- 错误信息 -->
        <div v-if="detailResult.error_message" class="error-section">
          <h3>错误信息</h3>
          <el-alert type="error" :closable="false">
            <pre class="error-message-content">{{ detailResult.error_message }}</pre>
          </el-alert>
        </div>
      </div>
      <div v-else class="no-result">
        <el-empty description="暂无数据" />
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, DocumentCopy, VideoPlay, View, Link } from '@element-plus/icons-vue'
import * as codeScanApi from '../api/codescan'
import * as projectApi from '../api/projects'
import * as apitestApi from '../api/apitest'
import { useProjectContext } from '../composables/useProjectContext'
import type { CodeScan, Project, ApiEnvironment, CodeScanResult } from '../api/types'


const scans = ref<CodeScan[]>([])
const scanResults = ref<Record<number, CodeScanResult>>({}) // 存储每个扫描的结果
const projects = ref<Project[]>([])
const environments = ref<ApiEnvironment[]>([])
const filters = reactive({
  project_id: undefined as number | undefined,
  keyword: '',
  result: undefined as string | undefined
})
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增任务')
const editingId = ref<number>()

// 编程语言选项
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
      keyword: filters.keyword || undefined,
      result: filters.result
    }
    
    // 优先使用当前项目过滤
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
    } else if (filters.project_id) {
      params.project_id = filters.project_id
    }
    
    scans.value = await codeScanApi.getCodeScans(params)
    // 加载每个扫描的最新结果
    await Promise.all(
      scans.value.map(async (scan) => {
        try {
          const result = await codeScanApi.getCodeScanResult(scan.id)
          scanResults.value[scan.id] = result
        } catch (error) {
          // 如果还没有结果，忽略错误
          console.debug(`扫描 ${scan.id} 还没有结果`)
        }
      })
    )
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
  filters.result = undefined
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
    scan_path: row.scan_path,
    language: row.language || '',
    sonar_project_key: row.sonar_project_key || '',
    sonar_host: row.sonar_host || '',
    sonar_login: row.sonar_login || ''
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.project_id || !formData.project_name || !formData.branch || !formData.scan_path) {
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

const handleScan = async (row: CodeScan) => {
  try {
    row.scanning = true
    await codeScanApi.executeCodeScan(row.id)
    ElMessage.success('扫描任务已启动')
    // 重置结果为扫描中状态
    scanResults.value[row.id] = {
      id: 0,
      scan_id: row.id,
      status: 'running'
    } as CodeScanResult
    // 定时刷新列表以获取最新状态
    const refreshInterval = setInterval(async () => {
      try {
        const result = await codeScanApi.getCodeScanResult(row.id)
        scanResults.value[row.id] = result
        // 如果扫描完成，停止刷新
        if (result.status === 'completed' || result.status === 'failed') {
          clearInterval(refreshInterval)
          // 更新row的result字段
          const scan = scans.value.find(s => s.id === row.id)
          if (scan) {
            if (result.status === 'completed') {
              // 检查bugs，有bug就是failed
              const bugs = result.metrics?.bugs || 0
              scan.result = bugs > 0 ? 'failed' : 'passed'
            } else {
              scan.result = 'failed'
            }
          }
          loadScans() // 重新加载完整列表
        }
      } catch (error) {
        // 忽略错误
      }
    }, 3000) // 每3秒刷新一次
    
    // 10分钟后停止刷新
    setTimeout(() => {
      clearInterval(refreshInterval)
    }, 600000)
  } catch (error: any) {
    ElMessage.error(error.message || '启动扫描失败')
  } finally {
    row.scanning = false
  }
}

const detailDrawerVisible = ref(false)
const currentDetailScan = ref<CodeScan | null>(null)
const detailResult = ref<CodeScanResult | null>(null)
const detailLoading = ref(false)

const handleViewDetail = async (row: CodeScan) => {
  currentDetailScan.value = row
  detailDrawerVisible.value = true
  await loadDetailResult(row.id)
}

const loadDetailResult = async (scanId: number) => {
  detailLoading.value = true
  try {
    detailResult.value = await codeScanApi.getCodeScanResult(scanId)
  } catch (error: any) {
    ElMessage.error(error.message || '加载扫描结果失败')
  } finally {
    detailLoading.value = false
  }
}

// 计算Sonar页面URL（详情抽屉中使用）
const detailSonarUrl = computed(() => {
  if (!currentDetailScan.value) {
    return null
  }
  const host = currentDetailScan.value.sonar_host
  const projectKey = currentDetailScan.value.sonar_project_key || `${currentDetailScan.value.project_name}:${currentDetailScan.value.branch}`
  
  if (!host) {
    return null
  }
  
  const baseUrl = host.endsWith('/') ? host.slice(0, -1) : host
  return `${baseUrl}/dashboard?id=${encodeURIComponent(projectKey)}`
})

const openDetailSonarPage = () => {
  if (detailSonarUrl.value) {
    window.open(detailSonarUrl.value, '_blank')
  } else {
    ElMessage.warning('Sonar Host 或 ProjectKey 未配置，无法打开Sonar页面')
  }
}

// 详情页状态相关函数
const getDetailStatusText = (status: string) => {
  switch (status) {
    case 'running':
      return '扫描中'
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    default:
      return '-'
  }
}

const getDetailStatusType = (status: string) => {
  switch (status) {
    case 'running':
      return 'warning'
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    default:
      return 'info'
  }
}

// 详情页指标样式函数
const getDetailMetricClass = (value: number | undefined, type: string) => {
  const numValue = value || 0
  if (numValue === 0) {
    return 'metric-good'
  } else if (numValue <= 5) {
    return 'metric-warning'
  } else {
    return 'metric-danger'
  }
}

const getDetailCoverageClass = (coverage: number | undefined) => {
  const numValue = coverage || 0
  if (numValue >= 80) {
    return 'metric-good'
  } else if (numValue >= 50) {
    return 'metric-warning'
  } else {
    return 'metric-danger'
  }
}

const getDetailDuplicationClass = (duplication: number | undefined) => {
  const numValue = duplication || 0
  if (numValue <= 3) {
    return 'metric-good'
  } else if (numValue <= 5) {
    return 'metric-warning'
  } else {
    return 'metric-danger'
  }
}

// 格式化技术债务（分钟转为天、小时等）
const formatTechnicalDebt = (minutes: number | undefined) => {
  if (!minutes || minutes === 0) {
    return '0'
  }
  const days = Math.floor(minutes / (8 * 60))
  const hours = Math.floor((minutes % (8 * 60)) / 60)
  const mins = minutes % 60
  
  if (days > 0) {
    return `${days}d ${hours}h`
  } else if (hours > 0) {
    return `${hours}h ${mins}m`
  } else {
    return `${mins}m`
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取扫描状态
const getScanStatus = (row: CodeScan): 'scanning' | 'passed' | 'failed' | 'unknown' => {
  const result = scanResults.value[row.id]
  if (result) {
    if (result.status === 'running') {
      return 'scanning'
    } else if (result.status === 'completed') {
      // 检查是否有bug，有bug就返回failed
      const bugs = result.metrics?.bugs || 0
      if (bugs > 0) {
        return 'failed'
      }
      return 'passed'
    } else if (result.status === 'failed') {
      return 'failed'
    }
  }
  // 如果没有结果，根据 row.result 判断
  if (row.result === 'passed') {
    // 如果有结果数据，再检查一次bugs
    const result = scanResults.value[row.id]
    if (result?.metrics) {
      const bugs = result.metrics.bugs || 0
      if (bugs > 0) {
        return 'failed'
      }
    }
    return 'passed'
  } else if (row.result === 'failed') {
    return 'failed'
  }
  return 'unknown'
}

// 获取扫描错误信息
const getScanErrorMessage = (row: CodeScan): string | undefined => {
  const result = scanResults.value[row.id]
  return result?.error_message
}

// 获取结果文本
const getResultText = (row: CodeScan): string => {
  const status = getScanStatus(row)
  if (status === 'scanning') {
    return '扫描中'
  } else if (status === 'passed') {
    return '通过'
  } else if (status === 'failed') {
    return '不通过'
  }
  return '-'
}

// 获取标签类型
const getResultTagType = (row: CodeScan): 'success' | 'danger' | 'warning' | 'info' => {
  const status = getScanStatus(row)
  if (status === 'scanning') {
    return 'warning'
  } else if (status === 'passed') {
    return 'success'
  } else if (status === 'failed') {
    return 'danger'
  }
  return 'info'
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

/* 详情抽屉样式 */
.result-detail-content {
  padding: 20px;
}

.detail-header-actions {
  margin-bottom: 24px;
  display: flex;
  justify-content: flex-end;
}

.info-section {
  margin-bottom: 24px;
}

.metrics-section {
  margin: 24px 0;
}

.metrics-section h3 {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
  color: #495057;
}

/* 指标容器：左右两列布局 */
.metrics-overview-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

/* 确保左右两列对齐 */
.metrics-column,
.metrics-column-new {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metrics-column {
  flex: 1;
  min-width: 0;
}

.metrics-column-new {
  /* 移除黄色背景 */
}

.overview-row-new {
  background: #ffffff;
  border: 1px solid #e0e0e0;
}

.overview-row-header-new {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e0e0e0;
}

/* SonarQube Overview 风格 */
.overview-row {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.overview-row:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.overview-row-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
}

.overview-title {
  font-size: 15px;
  font-weight: 600;
  color: #495057;
}

.overview-row-content {
  display: flex;
  padding: 20px;
  gap: 40px;
  flex-wrap: wrap;
}

.overview-metric {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.overview-metric-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 8px;
}

.overview-icon {
  font-size: 18px;
}

.overview-metric-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.metric-good {
  color: #52c41a; /* 绿色 */
}

.metric-warning {
  color: #faad14; /* 黄色 */
}

.metric-danger {
  color: #f5222d; /* 红色 */
}

.scan-output-section {
  margin-top: 24px;
}

.scan-output-section h3 {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
  color: #495057;
}

.scan-output-content {
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 600px;
  overflow-y: auto;
}

.error-section {
  margin-top: 24px;
}

.error-section h3 {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
  color: #495057;
}

.error-message-content {
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.no-result {
  padding: 40px;
  text-align: center;
}

.loading-container {
  padding: 20px;
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

.scan-detail-popover {
  padding: 8px 0;
}

.detail-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  font-size: 14px;
}

.detail-content {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
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

