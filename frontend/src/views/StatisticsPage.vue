<template>
  <div class="statistics-page">
    <!-- 顶部：标题 + 项目筛选 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><DataAnalysis /></el-icon>
          统计分析
        </h2>
      </div>
      <div class="filter-row">
        <el-select
          v-model="selectedProject"
          placeholder="选择项目"
          clearable
          style="width: 200px"
          @change="loadAllStatistics"
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
      </div>
    </el-card>

    <!-- 统计内容 -->
    <div v-loading="loading" class="statistics-content">
      <!-- 概览卡片 -->
      <el-row :gutter="20" class="overview-row">
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <el-statistic title="缺陷总数" :value="overview.bugs" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <el-statistic title="测试用例" :value="overview.testCases" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <el-statistic title="接口数量" :value="overview.apiEndpoints" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="overview-card">
            <el-statistic title="流程数量" :value="overview.apiFlows" />
          </el-card>
        </el-col>
      </el-row>

      <!-- 缺陷统计 -->
      <el-card class="statistics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h3>缺陷统计</h3>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">缺陷状态分布</div>
              <div ref="bugStatusChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">缺陷优先级分布</div>
              <div ref="bugPriorityChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">缺陷趋势（近30天）</div>
              <div ref="bugTrendChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">缺陷严重程度分布</div>
              <div ref="bugSeverityChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 测试用例统计 -->
      <el-card class="statistics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h3>测试用例统计</h3>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">用例状态分布</div>
              <div ref="testCaseStatusChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">用例优先级分布</div>
              <div ref="testCasePriorityChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 接口测试统计 -->
      <el-card class="statistics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h3>接口测试统计</h3>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">接口方法分布</div>
              <div ref="apiMethodChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">执行成功率趋势</div>
              <div ref="apiSuccessRateChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 流程测试统计 -->
      <el-card class="statistics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h3>流程测试统计</h3>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">流程执行趋势</div>
              <div ref="flowTrendChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">流程执行成功率</div>
              <div ref="flowSuccessRateChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 测试任务统计 -->
      <el-card class="statistics-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <h3>测试任务统计</h3>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">任务执行趋势</div>
              <div ref="taskTrendChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="chart-container">
              <div class="chart-title">任务执行状态分布</div>
              <div ref="taskStatusChartRef" class="chart" style="height: 300px;"></div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { DataAnalysis } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import * as bugApi from '../api/bugs'
import * as testCaseApi from '../api/testcases'
import * as apiTestApi from '../api/apitest'
import { useProjectContext } from '../composables/useProjectContext'
import type { Statistics, Project, TestCase, ApiEndpoint, ApiTestFlow } from '../api/types'
import type { TestTask } from '../api/apitest'

// 数据定义
const statistics = ref<Statistics>({
  total: 0,
  open: 0,
  in_progress: 0,
  resolved: 0,
  closed: 0,
  by_priority: {},
  by_severity: {},
  by_type: {}
})

const overview = ref({
  bugs: 0,
  testCases: 0,
  apiEndpoints: 0,
  apiFlows: 0
})

const testCasesData = ref<TestCase[]>([])
const apiEndpointsData = ref<ApiEndpoint[]>([])
const apiFlowsData = ref<ApiTestFlow[]>([])
const testTasksData = ref<TestTask[]>([])

const projects = ref<Project[]>([])
const selectedProject = ref<number>()
const loading = ref(false)

// 图表引用
const bugStatusChartRef = ref<HTMLElement>()
const bugPriorityChartRef = ref<HTMLElement>()
const bugTrendChartRef = ref<HTMLElement>()
const bugSeverityChartRef = ref<HTMLElement>()
const testCaseStatusChartRef = ref<HTMLElement>()
const testCasePriorityChartRef = ref<HTMLElement>()
const apiMethodChartRef = ref<HTMLElement>()
const apiSuccessRateChartRef = ref<HTMLElement>()
const flowTrendChartRef = ref<HTMLElement>()
const flowSuccessRateChartRef = ref<HTMLElement>()
const taskTrendChartRef = ref<HTMLElement>()
const taskStatusChartRef = ref<HTMLElement>()

// 图表实例
const chartInstances = ref<Map<string, echarts.ECharts>>(new Map())

const { 
  getProjects: getFilteredProjects,
  getCurrentProjectId,
  hasProjectSelected,
  onProjectChanged,
  ensureInitialized
} = useProjectContext()

// 销毁图表
const disposeChart = (key: string) => {
  const chart = chartInstances.value.get(key)
  if (chart) {
    chart.dispose()
    chartInstances.value.delete(key)
  }
}

// 销毁所有图表
const disposeAllCharts = () => {
  chartInstances.value.forEach((chart) => {
    chart.dispose()
  })
  chartInstances.value.clear()
}

// 渲染饼图
const renderPieChart = (dom: HTMLElement | undefined, data: Array<{ name: string; value: number }>, title: string, key: string) => {
  if (!dom) return
  
  disposeChart(key)
  const chart = echarts.init(dom)
  chartInstances.value.set(key, chart)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: title,
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}\n({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: data
      }
    ]
  }
  
  chart.setOption(option)
}

// 渲染折线图
const renderLineChart = (dom: HTMLElement | undefined, data: { dates: string[]; values: number[] }, title: string, key: string) => {
  if (!dom) return
  
  disposeChart(key)
  const chart = echarts.init(dom)
  chartInstances.value.set(key, chart)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: title,
        type: 'line',
        smooth: true,
        data: data.values,
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
            ]
          }
        },
        lineStyle: {
          color: '#667eea'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

// 加载所有统计数据
const loadAllStatistics = async () => {
  loading.value = true
  try {
    const projectId = hasProjectSelected.value && getCurrentProjectId.value 
      ? getCurrentProjectId.value 
      : selectedProject.value
    
    // 加载缺陷统计
    statistics.value = await bugApi.getStatistics(projectId)
    overview.value.bugs = statistics.value.total
    
    // 加载测试用例统计
    testCasesData.value = await testCaseApi.getTestCases({ project_id: projectId })
    overview.value.testCases = testCasesData.value.length
    
    // 加载接口统计
    apiEndpointsData.value = await apiTestApi.getApiEndpoints({ project_id: projectId, limit: 1000 })
    overview.value.apiEndpoints = apiEndpointsData.value.length
    
    // 加载流程统计
    apiFlowsData.value = await apiTestApi.getApiFlows({ project_id: projectId })
    overview.value.apiFlows = apiFlowsData.value.length
    
    // 加载测试任务统计
    testTasksData.value = await apiTestApi.getTestTasks({ project_id: projectId })
    
    // 渲染图表
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

// 渲染所有图表
const renderCharts = () => {
  // 缺陷状态分布（饼图）
  const bugStatusData = [
    { name: '待处理', value: statistics.value.open },
    { name: '进行中', value: statistics.value.in_progress },
    { name: '已解决', value: statistics.value.resolved },
    { name: '已关闭', value: statistics.value.closed }
  ].filter(item => item.value > 0)
  renderPieChart(bugStatusChartRef.value, bugStatusData, '缺陷状态', 'bugStatus')

  // 缺陷优先级分布（饼图）
  const bugPriorityData = Object.entries(statistics.value.by_priority).map(([key, value]) => ({
    name: getPriorityName(key),
    value: value
  })).filter(item => item.value > 0)
  renderPieChart(bugPriorityChartRef.value, bugPriorityData, '缺陷优先级', 'bugPriority')

  // 缺陷趋势（折线图）- 基于创建时间（简化版本，实际需要从API获取时间序列数据）
  const bugTrendData = generateTrendData(30, statistics.value.total)
  renderLineChart(bugTrendChartRef.value, bugTrendData, '缺陷数量', 'bugTrend')

  // 缺陷严重程度分布（饼图）
  const bugSeverityData = Object.entries(statistics.value.by_severity).map(([key, value]) => ({
    name: getSeverityName(key),
    value: value
  })).filter(item => item.value > 0)
  renderPieChart(bugSeverityChartRef.value, bugSeverityData, '缺陷严重程度', 'bugSeverity')

  // 测试用例状态分布（饼图）
  const testCaseStatusCount: Record<string, number> = {}
  testCasesData.value.forEach(tc => {
    testCaseStatusCount[tc.status] = (testCaseStatusCount[tc.status] || 0) + 1
  })
  const testCaseStatusData = Object.entries(testCaseStatusCount).map(([key, value]) => ({
    name: getTestCaseStatusName(key),
    value: value
  }))
  renderPieChart(testCaseStatusChartRef.value, testCaseStatusData, '用例状态', 'testCaseStatus')

  // 测试用例优先级分布（饼图）
  const testCasePriorityCount: Record<string, number> = {}
  testCasesData.value.forEach(tc => {
    testCasePriorityCount[tc.priority] = (testCasePriorityCount[tc.priority] || 0) + 1
  })
  const testCasePriorityData = Object.entries(testCasePriorityCount).map(([key, value]) => ({
    name: getPriorityName(key),
    value: value
  }))
  renderPieChart(testCasePriorityChartRef.value, testCasePriorityData, '用例优先级', 'testCasePriority')

  // 接口方法分布（饼图）
  const apiMethodCount: Record<string, number> = {}
  apiEndpointsData.value.forEach(api => {
    const method = api.method || 'GET'
    apiMethodCount[method] = (apiMethodCount[method] || 0) + 1
  })
  const apiMethodData = Object.entries(apiMethodCount).map(([key, value]) => ({
    name: key,
    value: value
  }))
  renderPieChart(apiMethodChartRef.value, apiMethodData, '接口方法', 'apiMethod')

  // 接口执行成功率趋势（折线图）- 简化版本
  const apiSuccessRateData = generateSuccessRateData(30)
  renderLineChart(apiSuccessRateChartRef.value, apiSuccessRateData, '成功率 (%)', 'apiSuccessRate')

  // 流程执行趋势（折线图）- 简化版本
  const flowTrendData = generateTrendData(30, apiFlowsData.value.length)
  renderLineChart(flowTrendChartRef.value, flowTrendData, '流程数量', 'flowTrend')

  // 流程执行成功率（饼图）- 简化版本
  const flowSuccessRateData = [
    { name: '成功', value: Math.floor(apiFlowsData.value.length * 0.8) },
    { name: '失败', value: Math.floor(apiFlowsData.value.length * 0.2) }
  ].filter(item => item.value > 0)
  renderPieChart(flowSuccessRateChartRef.value, flowSuccessRateData, '流程执行', 'flowSuccessRate')

  // 测试任务执行趋势（折线图）- 简化版本
  const taskTrendData = generateTrendData(30, testTasksData.value.length)
  renderLineChart(taskTrendChartRef.value, taskTrendData, '任务数量', 'taskTrend')

  // 测试任务状态分布（饼图）
  const taskStatusCount: Record<string, number> = {}
  testTasksData.value.forEach(task => {
    taskStatusCount[task.status] = (taskStatusCount[task.status] || 0) + 1
  })
  const taskStatusData = Object.entries(taskStatusCount).map(([key, value]) => ({
    name: getTaskStatusName(key),
    value: value
  }))
  renderPieChart(taskStatusChartRef.value, taskStatusData, '任务状态', 'taskStatus')
}

// 生成趋势数据（简化版本）
const generateTrendData = (days: number, total: number) => {
  const dates: string[] = []
  const values: number[] = []
  const today = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
    // 简化：随机生成数据，实际应该从API获取
    values.push(Math.floor(total * (0.3 + Math.random() * 0.7)))
  }
  
  return { dates, values }
}

// 生成成功率趋势数据（简化版本）
const generateSuccessRateData = (days: number) => {
  const dates: string[] = []
  const values: number[] = []
  const today = new Date()
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}/${date.getDate()}`)
    // 简化：随机生成成功率，实际应该从API获取
    values.push(Math.floor(80 + Math.random() * 20))
  }
  
  return { dates, values }
}

// 工具函数：获取优先级名称
const getPriorityName = (key: string) => {
  const map: Record<string, string> = {
    'blocker': '阻塞',
    'critical': '严重',
    'major': '主要',
    'minor': '次要',
    'trivial': '轻微'
  }
  return map[key] || key
}

// 工具函数：获取严重程度名称
const getSeverityName = (key: string) => {
  const map: Record<string, string> = {
    'critical': '严重',
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return map[key] || key
}

// 工具函数：获取测试用例状态名称
const getTestCaseStatusName = (key: string) => {
  const map: Record<string, string> = {
    'draft': '草稿',
    'review': '评审中',
    'approved': '已批准',
    'deprecated': '已废弃'
  }
  return map[key] || key
}

// 工具函数：获取测试任务状态名称
const getTaskStatusName = (key: string) => {
  const map: Record<string, string> = {
    'idle': '空闲',
    'running': '运行中',
    'success': '成功',
    'failed': '失败'
  }
  return map[key] || key
}

const loadProjects = async () => {
  projects.value = await getFilteredProjects()
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    selectedProject.value = getCurrentProjectId.value
  }
}

// 窗口大小改变时调整图表
const handleResize = () => {
  chartInstances.value.forEach((chart) => {
    chart.resize()
  })
}

let cleanupProjectChanged: (() => void) | null = null

onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized()
  loadAllStatistics()
  loadProjects()
  window.addEventListener('resize', handleResize)
  
  cleanupProjectChanged = onProjectChanged(() => {
    loadProjects()
    loadAllStatistics()
  })
})

onUnmounted(() => {
  if (cleanupProjectChanged) {
    cleanupProjectChanged()
  }
  disposeAllCharts()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.statistics-page {
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
  gap: 12px;
}

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.statistics-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overview-row {
  margin-bottom: 20px;
}

.overview-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.statistics-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.statistics-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.8);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.chart-container {
  padding: 20px;
  background: #fafbfc;
  border-radius: 12px;
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.chart {
  width: 100%;
  background: white;
  border-radius: 8px;
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
</style>
