<template>
  <div class="code-scan-result-page">
    <el-card class="result-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h2>扫描结果详情</h2>
          </div>
          <div class="header-right" v-if="result && result.scan">
            <el-button 
              type="primary" 
              @click="openSonarPage"
              :disabled="!sonarUrl"
            >
              <el-icon><Link /></el-icon>
              查看Sonar详情
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else-if="result">
        <!-- 扫描基本信息 -->
        <el-descriptions :column="2" border class="info-section">
          <el-descriptions-item label="项目">{{ result.scan?.project?.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工程">{{ result.scan?.project_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分支">{{ result.scan?.branch || '-' }}</el-descriptions-item>
          <el-descriptions-item label="扫描路径">{{ result.scan?.scan_path || '-' }}</el-descriptions-item>
          <el-descriptions-item label="扫描时间">{{ formatDate(result.scan?.scan_time) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(result.status)">
              {{ getStatusText(result.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 扫描指标 - SonarQube Overview 风格 -->
        <div v-if="result.metrics" class="metrics-section">
          <h3>扫描指标</h3>
          
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
                <div class="overview-metric-value" :class="getMetricClass(result.metrics.bugs, 'bugs')">
                  {{ result.metrics.bugs || 0 }}
                </div>
              </div>
              <div class="overview-metric">
                <div class="overview-metric-label">
                  <span class="overview-icon">🔒</span>
                  Vulnerabilities
                </div>
                <div class="overview-metric-value" :class="getMetricClass(result.metrics.vulnerabilities, 'vulnerabilities')">
                  {{ result.metrics.vulnerabilities || 0 }}
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
                <div class="overview-metric-value" :class="getMetricClass(result.metrics.code_smells, 'code_smells')">
                  {{ result.metrics.code_smells || 0 }}
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
                <div class="overview-metric-value" :class="getCoverageClass(result.metrics.coverage)">
                  {{ result.metrics.coverage ? `${result.metrics.coverage}%` : '0.0%' }}
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
                <div class="overview-metric-value" :class="getDuplicationClass(result.metrics.duplicated_lines_density)">
                  {{ result.metrics.duplicated_lines_density ? `${result.metrics.duplicated_lines_density}%` : '0.0%' }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 扫描详细过程 -->
        <div v-if="result.scan_output" class="scan-output-section">
          <h3>扫描详细过程</h3>
          <div class="scan-output-container">
            <pre class="scan-output-content">{{ result.scan_output }}</pre>
        </div>
        </div>
      </div>

      <div v-else class="no-result">
        <el-empty description="暂无扫描结果" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Link } from '@element-plus/icons-vue'
import * as codeScanApi from '../api/codescan'
import type { CodeScanResult } from '../api/types'

const route = useRoute()
const router = useRouter()

const result = ref<CodeScanResult | null>(null)
const loading = ref(false)

// 提取问题列表（issues可能是对象或数组）
const issuesList = computed(() => {
  if (!result.value || !result.value.issues) {
    return []
  }
  // 如果issues是对象，包含issues字段
  if (typeof result.value.issues === 'object' && !Array.isArray(result.value.issues)) {
    return result.value.issues.issues || []
  }
  // 如果issues是数组，直接返回
  if (Array.isArray(result.value.issues)) {
    return result.value.issues
  }
  return []
})

const loadResult = async () => {
  const scanId = parseInt(route.params.id as string)
  if (!scanId) {
    ElMessage.error('无效的扫描ID')
    router.back()
    return
  }

  loading.value = true
  try {
    result.value = await codeScanApi.getCodeScanResult(scanId)
  } catch (error: any) {
    ElMessage.error(error.message || '加载扫描结果失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status?: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    case 'running':
      return 'warning'
    default:
      return 'info'
  }
}

const getStatusText = (status?: string) => {
  switch (status) {
    case 'completed':
      return '已完成'
    case 'failed':
      return '失败'
    case 'running':
      return '运行中'
    default:
      return '未知'
  }
}

const getSeverityType = (severity: string) => {
  switch (severity?.toLowerCase()) {
    case 'blocker':
    case 'critical':
      return 'danger'
    case 'major':
      return 'warning'
    case 'minor':
    case 'info':
      return 'info'
    default:
      return ''
  }
}

// 获取指标样式类（根据数值大小）
const getMetricClass = (value: number | undefined, type: string) => {
  const numValue = value || 0
  if (numValue === 0) {
    return 'metric-good' // 绿色，表示良好
  } else if (numValue <= 5) {
    return 'metric-warning' // 黄色，表示警告
  } else {
    return 'metric-danger' // 红色，表示危险
  }
}

// 获取覆盖率样式类
const getCoverageClass = (coverage: number | undefined) => {
  const numValue = coverage || 0
  if (numValue >= 80) {
    return 'metric-good'
  } else if (numValue >= 50) {
    return 'metric-warning'
  } else {
    return 'metric-danger'
  }
}

// 获取重复度样式类
const getDuplicationClass = (duplication: number | undefined) => {
  const numValue = duplication || 0
  if (numValue <= 3) {
    return 'metric-good'
  } else if (numValue <= 5) {
    return 'metric-warning'
  } else {
    return 'metric-danger'
  }
}

// 计算Sonar页面URL
const sonarUrl = computed(() => {
  if (!result.value || !result.value.scan) {
    return null
  }
  const host = result.value.scan.sonar_host
  const projectKey = result.value.scan.sonar_project_key || `${result.value.scan.project_name}:${result.value.scan.branch}`
  
  if (!host) {
    return null
  }
  
  // 确保host以/结尾，然后拼接dashboard路径
  const baseUrl = host.endsWith('/') ? host.slice(0, -1) : host
  return `${baseUrl}/dashboard?id=${encodeURIComponent(projectKey)}`
})

const openSonarPage = () => {
  if (sonarUrl.value) {
    window.open(sonarUrl.value, '_blank')
  } else {
    ElMessage.warning('Sonar Host 或 ProjectKey 未配置，无法打开Sonar页面')
  }
}

onMounted(() => {
  loadResult()
})
</script>

<style scoped>
.code-scan-result-page {
  padding: 24px;
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

.result-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.loading-container {
  padding: 20px;
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

.no-result {
  padding: 40px;
  text-align: center;
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
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

.scan-output-container {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
}

.scan-output-content {
  color: #d4d4d4;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>

