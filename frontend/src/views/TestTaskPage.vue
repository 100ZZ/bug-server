<template>
  <div class="test-task-page">
    <!-- 顶部：标题 + 筛选 + 新增按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><List /></el-icon>
          测试任务
        </h2>
      </div>
      <div class="filter-row">
        <!-- 左侧：搜索和筛选区域 -->
        <div class="filter-left">
          <el-select 
            v-model="filters.project_id" 
            placeholder="选择项目" 
            :clearable="!hasProjectSelected"
            :disabled="hasProjectSelected"
            style="width: 200px" 
            @change="loadTasks"
            :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
          >
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
          <el-select v-model="filters.status" placeholder="状态" clearable style="width: 150px" @change="loadTasks">
            <el-option label="空闲" value="idle" />
            <el-option label="运行中" value="running" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
          <el-input
            v-model="filters.keyword"
            placeholder="搜索任务名称"
            clearable
            @keyup.enter="loadTasks"
            style="width: 280px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="loadTasks">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button 
            :type="filters.is_favorite ? 'primary' : 'default'"
            :icon="Star"
            @click="toggleFavoriteFilter"
          >
            收藏
          </el-button>
        </div>
        
        <!-- 右侧：主要操作按钮区域 -->
        <div class="filter-right">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 底部：任务列表 -->
    <el-card class="table-card">
      <el-table
        :data="tasks"
        v-loading="loading"
        stripe
        style="width: 100%"
        table-layout="fixed"
        :max-height="600"
        row-key="id"
      >
        <el-table-column label="编号" width="80" align="center" type="index" :index="(index: number) => index + 1" />
        <el-table-column label="收藏" width="80" align="center">
          <template #default="{ row }">
            <el-icon 
              :class="['favorite-icon', { 'is-favorite': row.is_favorite }]"
              @click.stop="handleToggleFavorite(row)"
              style="cursor: pointer; font-size: 20px; color: #dcdfe6; transition: all 0.3s;"
            >
              <Star v-if="row.is_favorite" />
              <StarFilled v-else />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="200" align="center" show-overflow-tooltip />
        <el-table-column prop="project" label="项目" width="140" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="数量" width="100" align="center">
          <template #default="{ row }">
            <el-link type="primary" @click="showItemsDialog(row)" :underline="false">
              {{ getItemCount(row) }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="定时" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.cron_expression" type="warning" size="small">
              {{ row.cron_expression }}
            </el-tag>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <div class="action-row">
                <el-button link type="primary" size="small" @click="handleEdit(row)">
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button link type="danger" size="small" @click="handleDelete(row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
              <div class="action-row">
                <el-button link type="primary" size="small" @click="handleExecute(row)" :disabled="row.status === 'running'">
                  <el-icon><VideoPlay /></el-icon>
                  执行
                </el-button>
                <el-button link type="primary" size="small" @click="handleReport(row)">
                  <el-icon><Document /></el-icon>
                  报告
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      width="800px"
      :close-on-click-modal="false"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">创建或编辑测试任务，可以添加多个接口和流程，系统将按顺序执行</span>
        </div>
      </template>
      <el-form :model="formData" label-width="100px" ref="formRef">
        <el-form-item label="任务名称" required>
          <el-input v-model="formData.name" placeholder="请输入任务名称" />
        </el-form-item>
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
        <el-form-item label="任务描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入任务描述（可选）" />
        </el-form-item>
        <el-form-item label="定时执行">
          <el-input 
            v-model="formData.cron_expression" 
            placeholder="Cron表达式，例如：0 0 2 * * ? (每天凌晨2点执行)"
            style="width: 100%"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            Cron表达式格式：秒 分 时 日 月 周，例如：0 0 2 * * ? 表示每天凌晨2点执行
          </div>
        </el-form-item>
        <el-form-item label="执行环境" v-if="formData.cron_expression">
          <el-select v-model="formData.environment_id" placeholder="选择定时执行时使用的环境" style="width: 100%">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
              :value="env.id"
            />
          </el-select>
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            定时执行时将使用此环境
          </div>
        </el-form-item>
        <el-form-item label="任务项">
          <div style="margin-bottom: 10px;">
            <el-button size="small" @click="showAddItemDialog">添加接口/流程</el-button>
          </div>
          <el-table :data="formData.items" border style="width: 100%">
            <el-table-column label="类型" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.item_type === 'api' ? 'primary' : 'success'" size="small">
                  {{ row.item_type === 'api' ? '接口' : '流程' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="名称" min-width="200">
              <template #default="{ row }">
                {{ getItemName(row) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row, $index }">
                <el-button link type="danger" size="small" @click="removeItem($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加任务项对话框 -->
    <el-dialog
      v-model="addItemDialogVisible"
      width="700px"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">添加接口/流程</span>
          <span class="dialog-description">选择要添加到任务中的接口或流程，可以多选，系统将按添加顺序执行</span>
        </div>
      </template>
      <el-tabs v-model="addItemType">
        <el-tab-pane label="接口" name="api">
          <el-select
            v-model="selectedApiIds"
            multiple
            filterable
            placeholder="搜索或选择接口（支持按方法、路径、名称搜索）"
            style="width: 100%"
            :filter-method="filterApis"
          >
            <el-option
              v-for="api in filteredApis"
              :key="api.id"
              :label="`${api.method} ${api.path} - ${api.name}`"
              :value="api.id"
            />
          </el-select>
          <div style="margin-top: 10px; font-size: 12px; color: #909399;">
            共 {{ availableApis.length }} 个接口，已选择 {{ selectedApiIds.length }} 个
          </div>
        </el-tab-pane>
        <el-tab-pane label="流程" name="flow">
          <el-select
            v-model="selectedFlowIds"
            multiple
            filterable
            placeholder="搜索或选择流程（支持按名称搜索）"
            style="width: 100%"
            :filter-method="filterFlows"
          >
            <el-option
              v-for="flow in filteredFlows"
              :key="flow.id"
              :label="flow.name"
              :value="flow.id"
            />
          </el-select>
          <div style="margin-top: 10px; font-size: 12px; color: #909399;">
            共 {{ availableFlows.length }} 个流程，已选择 {{ selectedFlowIds.length }} 个
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="addItemDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAddItems">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 任务项列表对话框 -->
    <el-dialog
      v-model="itemsDialogVisible"
      width="800px"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">任务项列表</span>
          <span class="dialog-description">查看任务中包含的所有接口和流程</span>
        </div>
      </template>
      <el-table :data="currentTaskItems" border>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.item_type === 'api' ? 'primary' : 'success'" size="small">
              {{ row.item_type === 'api' ? '接口' : '流程' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="名称" min-width="200">
          <template #default="{ row }">
            {{ getItemName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="排序" width="100" align="center">
          <template #default="{ row }">
            {{ row.sort_order }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 执行对话框 -->
    <el-dialog
      v-model="executeDialogVisible"
      width="500px"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">执行测试任务</span>
          <span class="dialog-description">选择执行环境，按任务项顺序依次执行接口和流程测试</span>
        </div>
      </template>
      <el-form :model="executeForm" label-width="100px">
        <el-form-item label="选择环境" required>
          <el-select v-model="executeForm.environment_id" placeholder="选择环境" style="width: 100%">
            <el-option
              v-for="env in environments"
              :key="env.id"
              :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
              :value="env.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="executeDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="executing" @click="confirmExecute">开始执行</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailDialogVisible"
      title="任务详情"
      size="60%"
      :close-on-click-modal="true"
    >
      <template #header>
        <div class="drawer-header">
          <span class="drawer-title">任务详情</span>
          <span class="drawer-description">查看任务的详细信息，包括任务项列表和执行状态</span>
        </div>
      </template>
      <div v-if="currentTask" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务名称">{{ currentTask.name }}</el-descriptions-item>
          <el-descriptions-item label="项目">{{ currentTask.project?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(currentTask.status)" size="small">
              {{ getStatusText(currentTask.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数量">{{ getItemCount(currentTask) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentTask.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ formatDateTime(currentTask.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">{{ formatDateTime(currentTask.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        <el-divider>任务项列表</el-divider>
        <el-table :data="currentTask?.items || []" border>
          <el-table-column label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.item_type === 'api' ? 'primary' : 'success'" size="small">
                {{ row.item_type === 'api' ? '接口' : '流程' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="名称" min-width="200">
            <template #default="{ row }">
              {{ getItemName(row) }}
            </template>
          </el-table-column>
          <el-table-column label="排序" width="100" align="center">
            <template #default="{ row }">
              {{ row.sort_order }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-drawer>

    <!-- 报告抽屉 -->
    <el-drawer
      v-model="reportDialogVisible"
      :with-header="false"
      size="85%"
      :close-on-click-modal="true"
    >
      <div class="report-wrapper">
        <div class="report-header-section">
          <h3>执行报告</h3>
        </div>
        <div class="report-content">
        <div v-if="executions.length === 0" class="empty-state">
          <el-empty description="暂无执行记录" />
        </div>
        <div v-else class="executions-list">
          <div
            v-for="execution in executions"
            :key="execution.id"
            class="execution-card"
          >
            <div class="execution-card-header">
              <div class="execution-info">
                <div class="execution-time">
                  <el-icon><Clock /></el-icon>
                  <span>{{ formatDateTime(execution.started_at) }}</span>
                </div>
                <div class="execution-status">
                  <el-tag :type="getStatusTag(execution.status)" size="small" effect="dark">
                    {{ getStatusText(execution.status) }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="execution-stats">
              <div class="stat-item">
                <div class="stat-label">总数</div>
                <div class="stat-value">{{ execution.total_count || 0 }}</div>
              </div>
              <div class="stat-item success">
                <div class="stat-label">成功</div>
                <div class="stat-value">{{ execution.success_count || 0 }}</div>
              </div>
              <div class="stat-item failed">
                <div class="stat-label">失败</div>
                <div class="stat-value">{{ execution.failed_count || 0 }}</div>
              </div>
              <div class="stat-item" v-if="execution.completed_at">
                <div class="stat-label">完成时间</div>
                <div class="stat-value-small">{{ formatDateTime(execution.completed_at) }}</div>
              </div>
            </div>
            <div v-if="execution.error_message" class="execution-error">
              <el-icon><Warning /></el-icon>
              <span>{{ execution.error_message }}</span>
            </div>
            <div class="execution-card-footer">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewExecutionDetail(execution)"
                class="detail-button"
              >
                <el-icon><View /></el-icon>
                详情
              </el-button>
            </div>
          </div>
        </div>
        </div>
      </div>
    </el-drawer>

    <!-- 执行详情抽屉 -->
    <el-drawer
      v-model="executionDetailDrawerVisible"
      :with-header="false"
      size="75%"
      :close-on-click-modal="true"
    >
      <div class="execution-detail-wrapper">
        <div class="execution-detail-header-section">
          <h3>执行详情</h3>
        </div>
        <div v-if="currentExecution" class="execution-detail-container">
        <el-descriptions :column="2" border style="margin-bottom: 20px;">
          <el-descriptions-item label="执行时间">{{ formatDateTime(currentExecution.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ currentExecution.completed_at ? formatDateTime(currentExecution.completed_at) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTag(currentExecution.status)" size="small">
              {{ getStatusText(currentExecution.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总数">{{ currentExecution.total_count }}</el-descriptions-item>
          <el-descriptions-item label="成功">
            <span style="color: #67c23a">{{ currentExecution.success_count }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="失败">
            <span style="color: #f56c6c">{{ currentExecution.failed_count }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider>执行结果详情</el-divider>
        
        <div v-if="currentExecution && currentExecution.execution_results && currentExecution.execution_results.length > 0" class="execution-results-container">
          <div v-for="(result, index) in currentExecution.execution_results" :key="index" class="execution-result-item">
            <div class="execution-result-header" @click="toggleResultDetail(index)">
              <el-tag :type="result.item_type === 'api' ? 'primary' : 'success'" size="small">
                {{ result.item_type === 'api' ? '接口' : '流程' }}
              </el-tag>
              <span class="result-name">{{ result.item_name }}</span>
              <div style="margin-left: auto; display: flex; align-items: center; gap: 12px; cursor: pointer;">
                <el-tag :type="result.success ? 'success' : 'danger'" size="small">
                  {{ result.success ? '成功' : '失败' }}
                </el-tag>
                <el-icon :class="['expand-icon', { 'expanded': expandedResultIndices.has(index) }]">
                  <ArrowDown />
                </el-icon>
              </div>
            </div>
            
            <div v-show="expandedResultIndices.has(index)" class="execution-result-content">
              <!-- 左侧：请求参数 -->
              <div class="execution-result-left">
                <el-divider>请求参数</el-divider>
                <el-tabs v-model="resultDetailActiveTabs[index]" class="param-tabs">
                  <el-tab-pane label="URL" name="url">
                    <el-input
                      :value="getRequestUrl(result)"
                      type="textarea"
                      class="param-textarea"
                      :autosize="{ minRows: 3, maxRows: 5 }"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Header" name="headers">
                    <el-input
                      :value="formatJsonObject(getRequestHeaders(result))"
                      type="textarea"
                      class="param-textarea"
                      :autosize="{ minRows: 12, maxRows: 30 }"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Query" name="query_params">
                    <el-input
                      :value="formatJsonObject(getRequestQueryParams(result))"
                      type="textarea"
                      class="param-textarea"
                      :autosize="{ minRows: 12, maxRows: 30 }"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Body" name="body">
                    <el-input
                      :value="formatResponseBody(getRequestBody(result))"
                      type="textarea"
                      class="param-textarea"
                      :autosize="{ minRows: 15, maxRows: 35 }"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Path" name="path_params">
                    <el-input
                      :value="formatJsonObject(getRequestPathParams(result))"
                      type="textarea"
                      class="param-textarea"
                      :autosize="{ minRows: 12, maxRows: 30 }"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Assertion" name="assertions">
                    <div v-if="getRequestAssertions(result) && getRequestAssertions(result).length > 0" class="assertion-list">
                      <div
                        v-for="(assertion, idx) in getRequestAssertions(result)"
                        :key="idx"
                        class="assertion-row"
                      >
                        <el-select :model-value="assertion.type" class="assertion-type" disabled>
                          <el-option label="状态码" value="status_code" />
                          <el-option label="JSON路径" value="json_path" />
                          <el-option label="响应时间" value="response_time" />
                          <el-option label="包含" value="contains" />
                        </el-select>
                        <el-input
                          v-if="assertion.type === 'json_path'"
                          :model-value="assertion.target || ''"
                          class="assertion-target"
                          placeholder="例如：data.id"
                          readonly
                        />
                        <el-select :model-value="assertion.operator" class="assertion-operator" disabled>
                          <el-option label="等于" value="eq" />
                          <el-option label="不等于" value="ne" />
                          <el-option label="大于" value="gt" />
                          <el-option label="大于等于" value="gte" />
                          <el-option label="小于" value="lt" />
                          <el-option label="小于等于" value="lte" />
                          <el-option label="包含" value="contains" />
                          <el-option label="不包含" value="not_contains" />
                        </el-select>
                        <el-input
                          :model-value="assertion.expected !== undefined && assertion.expected !== null ? String(assertion.expected) : ''"
                          class="assertion-value"
                          placeholder="期望值"
                          readonly
                        />
                      </div>
                    </div>
                    <div v-else>
                      <el-empty description="暂无断言" :image-size="80" />
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
              
              <!-- 右侧：响应信息 -->
              <div class="execution-result-right">
                <el-divider>响应信息</el-divider>
                <div class="response-content">
                  <el-descriptions :column="1" border style="margin-bottom: 16px;">
                    <el-descriptions-item label="状态">
                      <el-tag :type="result.success ? 'success' : 'danger'">
                        {{ result.success ? '成功' : '失败' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="响应状态码">
                      {{ result.status_code || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="响应时间">
                      {{ result.execution_time ? `${result.execution_time}ms` : '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="请求URL">
                      {{ getRequestUrl(result) }}
                    </el-descriptions-item>
                    <el-descriptions-item label="错误信息" v-if="result.error_message">
                      <el-text type="danger" style="white-space: pre-wrap;">{{ result.error_message }}</el-text>
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <el-tabs>
                    <el-tab-pane label="Header">
                      <pre class="response-pre">{{ formatJsonObject(getRequestHeaders(result)) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="Query">
                      <pre class="response-pre">{{ formatJsonObject(getRequestQueryParams(result)) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="Body">
                      <pre class="response-pre">{{ formatResponseBody(getRequestBody(result)) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="Path">
                      <pre class="response-pre">{{ formatJsonObject(getRequestPathParams(result)) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="响应头">
                      <pre class="response-pre">{{ formatJsonObject(getResponseHeaders(result)) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="响应体">
                      <pre class="response-pre">{{ formatResponseBody(getResponseBody(result)) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="流程步骤" v-if="result.item_type === 'flow' && result.details?.steps">
                      <div v-for="(step, stepIdx) in result.details.steps" :key="stepIdx" class="flow-step-item">
                        <el-divider>
                          <el-tag :type="step.success ? 'success' : 'danger'" size="small">
                            {{ step.step_name || `步骤 ${step.step_index}` }} - {{ step.success ? '成功' : '失败' }}
                          </el-tag>
                        </el-divider>
                        <el-descriptions :column="1" border style="margin-bottom: 12px;">
                          <el-descriptions-item label="状态码">{{ step.status_code || '-' }}</el-descriptions-item>
                          <el-descriptions-item label="耗时">{{ step.execution_time ? `${step.execution_time}ms` : '-' }}</el-descriptions-item>
                          <el-descriptions-item label="错误信息" v-if="step.error_message">
                            <el-text type="danger">{{ step.error_message }}</el-text>
                          </el-descriptions-item>
                        </el-descriptions>
                        <el-tabs>
                          <el-tab-pane label="请求URL">
                            <pre class="response-pre">{{ step.details?.request_url || '-' }}</pre>
                          </el-tab-pane>
                          <el-tab-pane label="请求Header">
                            <pre class="response-pre">{{ formatJsonObject(step.details?.request_headers || {}) }}</pre>
                          </el-tab-pane>
                          <el-tab-pane label="请求Query">
                            <pre class="response-pre">{{ formatJsonObject(step.details?.request_query_params || {}) }}</pre>
                          </el-tab-pane>
                          <el-tab-pane label="请求Body">
                            <pre class="response-pre">{{ formatResponseBody(step.details?.request_body) }}</pre>
                          </el-tab-pane>
                          <el-tab-pane label="响应头">
                            <pre class="response-pre">{{ formatJsonObject(step.details?.response_headers || {}) }}</pre>
                          </el-tab-pane>
                          <el-tab-pane label="响应体">
                            <pre class="response-pre">{{ formatResponseBody(step.details?.response_body) }}</pre>
                          </el-tab-pane>
                        </el-tabs>
                      </div>
                    </el-tab-pane>
                  </el-tabs>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
        <div v-else class="execution-detail-container">
          <el-empty description="暂无执行结果" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Star, StarFilled, Plus, List, View, Delete, VideoPlay, Document, Clock, Warning, EditPen, ArrowDown } from '@element-plus/icons-vue'
import { useProjectContext } from '@/composables/useProjectContext'
import * as projectApi from '@/api/projects'
import { getApiEnvironments } from '@/api/apitest'
import { getApiEndpoints } from '@/api/apitest'
import { getApiFlows } from '@/api/apitest'
import {
  getTestTasks,
  getTestTask,
  createTestTask,
  updateTestTask,
  deleteTestTask,
  toggleTestTaskFavorite,
  executeTestTask,
  getTestTaskExecutions,
  type TestTask,
  type TestTaskItem,
  type TestTaskCreate,
  type TestTaskExecution
} from '@/api/apitest'
import type { ApiEndpoint, ApiTestFlow } from '@/api/types'

// 项目上下文
const {
  getCurrentProjectId,
  hasProjectSelected,
  ensureInitialized: ensureInitialized1
} = useProjectContext()

const loading = ref(false)
const saving = ref(false)
const executing = ref(false)
const tasks = ref<TestTask[]>([])
const projects = ref<any[]>([])
const environments = ref<any[]>([])
const availableApis = ref<ApiEndpoint[]>([])
const availableFlows = ref<ApiTestFlow[]>([])
const filteredApis = ref<ApiEndpoint[]>([])
const filteredFlows = ref<ApiTestFlow[]>([])

const filters = ref({
  project_id: undefined as number | undefined,
  keyword: '',
  status: undefined as string | undefined,
  is_favorite: undefined as boolean | undefined
})

const dialogVisible = ref(false)
const dialogTitle = ref('新建任务')
const formData = ref<TestTaskCreate>({
  name: '',
  project_id: 0,
  description: '',
  items: [],
  cron_expression: '',
  environment_id: undefined
})

const addItemDialogVisible = ref(false)
const addItemType = ref<'api' | 'flow'>('api')
const selectedApiIds = ref<number[]>([])
const selectedFlowIds = ref<number[]>([])

const itemsDialogVisible = ref(false)
const currentTaskItems = ref<TestTaskItem[]>([])

const executeDialogVisible = ref(false)
const executeForm = ref({
  environment_id: 0
})
const currentExecuteTask = ref<TestTask | null>(null)

const detailDialogVisible = ref(false)
const currentTask = ref<TestTask | null>(null)

const reportDialogVisible = ref(false)
const executions = ref<TestTaskExecution[]>([])
const currentExecution = ref<TestTaskExecution | null>(null)
const executionDetailDrawerVisible = ref(false)
const resultDetailActiveTabs = ref<Record<number, string>>({})
const expandedResultIndices = ref<Set<number>>(new Set())

const formRef = ref()

// 格式化工具函数
const formatEmptyObject = () => '{\n\n}'

const formatJsonObject = (obj: any) => {
  if (!obj || (typeof obj === 'object' && Object.keys(obj).length === 0)) {
    return formatEmptyObject()
  }
  return JSON.stringify(obj, null, 2)
}

const formatResponseBody = (body: any) => {
  if (!body) return '-'
  try {
    const parsed = typeof body === 'string' ? JSON.parse(body) : body
    // 如果是空对象，返回格式化的字符串
    if (typeof parsed === 'object' && !Array.isArray(parsed) && Object.keys(parsed).length === 0) {
      return formatEmptyObject()
    }
    return JSON.stringify(parsed, null, 2)
  } catch {
    return body
  }
}

// 从执行结果中提取请求和响应信息
const getRequestUrl = (result: any) => {
  if (result.details?.request_url) return result.details.request_url
  if (result.details?.environment?.base_url && result.item_name) {
    return `${result.details.environment.base_url}${result.item_name}`
  }
  return '-'
}

const getRequestHeaders = (result: any) => {
  return result.details?.request_headers || {}
}

const getRequestQueryParams = (result: any) => {
  return result.details?.request_query_params || {}
}

const getRequestBody = (result: any) => {
  return result.details?.request_body || null
}

const getRequestPathParams = (result: any) => {
  return result.details?.request_path_params || {}
}

const getRequestAssertions = (result: any) => {
  return result.details?.request_assertions || result.details?.assertions || []
}

const getResponseHeaders = (result: any) => {
  return result.details?.response_headers || {}
}

const getResponseBody = (result: any) => {
  return result.details?.response_body || null
}

// 切换执行结果详情的展开/折叠
const toggleResultDetail = (index: number) => {
  if (expandedResultIndices.value.has(index)) {
    expandedResultIndices.value.delete(index)
  } else {
    expandedResultIndices.value.add(index)
    // 初始化该结果的标签页
    if (!resultDetailActiveTabs.value[index]) {
      resultDetailActiveTabs.value[index] = 'url'
    }
  }
}

// 加载数据
const loadTasks = async () => {
  loading.value = true
  try {
    const params: any = {}
    // 如果已选择项目上下文，自动应用项目过滤（单选模式）
    const currentProjectId = getCurrentProjectId.value
    if (hasProjectSelected.value && currentProjectId) {
      // 使用当前选中的项目ID
      params.project_id = currentProjectId
    } else if (filters.value.project_id) {
      // 如果页面内选择了项目，使用单个项目ID
      params.project_id = filters.value.project_id
    }
    if (filters.value.keyword) params.keyword = filters.value.keyword
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.is_favorite !== undefined) params.is_favorite = filters.value.is_favorite
    
    console.log('加载任务参数:', params)
    const response = await getTestTasks(params)
    // 由于响应拦截器已经返回了 response.data，所以 response 本身就是数组
    tasks.value = Array.isArray(response) ? response : (response.data || [])
    console.log('加载的任务列表:', tasks.value)
  } catch (error: any) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const { 
  getProjects: getFilteredProjects,
  onProjectChanged,
  ensureInitialized: ensureInitialized2
} = useProjectContext()

const loadProjects = async () => {
  try {
    // 使用 useProjectContext 的 getProjects，会自动根据选中的项目过滤
    projects.value = await getFilteredProjects()
    if (projects.value.length === 0) {
      console.warn('项目列表为空')
    }
    
    // 如果有选中的项目，自动设置过滤器
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.value.project_id = getCurrentProjectId.value
    }
  } catch (error: any) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败: ' + (error.message || '未知错误'))
  }
}

const loadEnvironments = async () => {
  try {
    const response = await getApiEnvironments()
    // 处理响应格式：可能是数组或对象
    environments.value = Array.isArray(response) ? response : (response.data || [])
  } catch (error: any) {
    ElMessage.error('加载环境列表失败: ' + (error.message || '未知错误'))
  }
}

const loadAvailableApis = async () => {
  try {
    const response = await getApiEndpoints({ project_id: formData.value.project_id })
    availableApis.value = Array.isArray(response) ? response : (response.data || [])
    filteredApis.value = availableApis.value
  } catch (error: any) {
    ElMessage.error('加载接口列表失败')
  }
}

const loadAvailableFlows = async () => {
  try {
    const response = await getApiFlows({ project_id: formData.value.project_id })
    availableFlows.value = Array.isArray(response) ? response : (response.data || [])
    filteredFlows.value = availableFlows.value
  } catch (error: any) {
    ElMessage.error('加载流程列表失败')
  }
}

// 过滤接口
const filterApis = (keyword: string) => {
  if (!keyword) {
    filteredApis.value = availableApis.value
    return
  }
  const lowerKeyword = keyword.toLowerCase()
  filteredApis.value = availableApis.value.filter(api => {
    const method = (api.method || '').toLowerCase()
    const path = (api.path || '').toLowerCase()
    const name = (api.name || '').toLowerCase()
    return method.includes(lowerKeyword) || path.includes(lowerKeyword) || name.includes(lowerKeyword)
  })
}

// 过滤流程
const filterFlows = (keyword: string) => {
  if (!keyword) {
    filteredFlows.value = availableFlows.value
    return
  }
  const lowerKeyword = keyword.toLowerCase()
  filteredFlows.value = availableFlows.value.filter(flow => {
    const name = (flow.name || '').toLowerCase()
    const description = (flow.description || '').toLowerCase()
    return name.includes(lowerKeyword) || description.includes(lowerKeyword)
  })
}

// 工具函数
const getItemCount = (task: TestTask) => {
  return (task.items || []).length
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'idle': 'info',
    'running': 'warning',
    'success': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'idle': '空闲',
    'running': '运行中',
    'success': '成功',
    'failed': '失败'
  }
  return map[status] || status
}

const getItemName = (item: TestTaskItem) => {
  if (item.item_type === 'api') {
    const api = availableApis.value.find(a => a.id === item.item_id)
    return api ? `${api.method} ${api.path} - ${api.name}` : `接口 ${item.item_id}`
  } else {
    const flow = availableFlows.value.find(f => f.id === item.item_id)
    return flow ? flow.name : `流程 ${item.item_id}`
  }
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 操作函数
const handleReset = () => {
  filters.value = {
    project_id: undefined,
    keyword: '',
    status: undefined,
    is_favorite: undefined
  }
  loadTasks()
}

const toggleFavoriteFilter = () => {
  filters.value.is_favorite = filters.value.is_favorite === true ? undefined : true
  loadTasks()
}

const handleCreate = async () => {
  dialogTitle.value = '新建任务'
  // 确保项目列表已加载
  if (projects.value.length === 0) {
    await loadProjects()
  }
  
  // 如果已选择项目上下文，自动设置项目ID
  const currentProjectId = getCurrentProjectId.value
  const projectId = hasProjectSelected.value && currentProjectId
    ? currentProjectId
    : (projects.value[0]?.id || 0)
  
  formData.value = {
    name: '',
    project_id: projectId,
    description: '',
    items: [],
    cron_expression: '',
    environment_id: undefined
  }
  dialogVisible.value = true
  if (formData.value.project_id) {
    loadAvailableApis()
    loadAvailableFlows()
  }
}

const handleView = async (row: TestTask) => {
  try {
    const response = await getTestTask(row.id)
    // 处理响应格式：可能是数组或对象
    currentTask.value = Array.isArray(response) ? response[0] : (response.data || response)
    // 加载接口和流程名称
    if (currentTask.value?.project_id) {
      formData.value.project_id = currentTask.value.project_id
      await loadAvailableApis()
      await loadAvailableFlows()
    }
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error('加载任务详情失败: ' + (error.message || '未知错误'))
  }
}

const handleDelete = async (row: TestTask) => {
  try {
    await ElMessageBox.confirm('确定要删除这个测试任务吗？', '确认删除', {
      type: 'warning'
    })
    await deleteTestTask(row.id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

const handleToggleFavorite = async (row: TestTask) => {
  try {
    await toggleTestTaskFavorite(row.id)
    row.is_favorite = !row.is_favorite
    ElMessage.success(row.is_favorite ? '已收藏' : '已取消收藏')
  } catch (error: any) {
    ElMessage.error('操作失败')
  }
}

const handleExecute = async (row: TestTask) => {
  currentExecuteTask.value = row
  executeForm.value.environment_id = undefined
  // 确保环境列表已加载
  if (environments.value.length === 0) {
    await loadEnvironments()
  }
  executeDialogVisible.value = true
}

const confirmExecute = async () => {
  if (!executeForm.value.environment_id) {
    ElMessage.warning('请选择环境')
    return
  }
  executing.value = true
  try {
    await executeTestTask(currentExecuteTask.value!.id, {
      environment_id: executeForm.value.environment_id
    })
    ElMessage.success('任务已开始执行')
    executeDialogVisible.value = false
    loadTasks()
  } catch (error: any) {
    ElMessage.error('执行失败: ' + (error.message || '未知错误'))
  } finally {
    executing.value = false
  }
}

const handleReport = async (row: TestTask) => {
  try {
    const response = await getTestTaskExecutions(row.id)
    // 由于响应拦截器已经返回了 response.data，所以 response 本身就是数组
    executions.value = Array.isArray(response) ? response : (response.data || [])
    reportDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error('加载执行记录失败: ' + (error.message || '未知错误'))
    console.error('加载执行记录失败:', error)
  }
}

const viewExecutionDetail = (execution: TestTaskExecution) => {
  currentExecution.value = execution
  // 重置展开状态，默认所有项都折叠
  expandedResultIndices.value.clear()
  // 初始化每个结果的标签页状态
  if (execution.execution_results) {
    execution.execution_results.forEach((_, index) => {
      if (!resultDetailActiveTabs.value[index]) {
        resultDetailActiveTabs.value[index] = 'url'
      }
    })
  }
  executionDetailDrawerVisible.value = true
}

const showItemsDialog = (row: TestTask) => {
  currentTaskItems.value = row.items || []
  itemsDialogVisible.value = true
}

const showAddItemDialog = () => {
  if (!formData.value.project_id) {
    ElMessage.warning('请先选择项目')
    return
  }
  addItemDialogVisible.value = true
  selectedApiIds.value = []
  selectedFlowIds.value = []
  loadAvailableApis()
  loadAvailableFlows()
}

const confirmAddItems = () => {
  // 获取当前最大排序值
  const maxSortOrder = formData.value.items?.length ? Math.max(...formData.value.items.map(i => i.sort_order || 0)) : -1
  let nextSortOrder = maxSortOrder + 1
  
  // 同时处理接口和流程的选择
  // 添加接口
  selectedApiIds.value.forEach(id => {
    if (!formData.value.items?.find(item => item.item_type === 'api' && item.item_id === id)) {
      formData.value.items!.push({
        item_type: 'api',
        item_id: id,
        sort_order: nextSortOrder++
      })
    }
  })
  
  // 添加流程
  selectedFlowIds.value.forEach(id => {
    if (!formData.value.items?.find(item => item.item_type === 'flow' && item.item_id === id)) {
      formData.value.items!.push({
        item_type: 'flow',
        item_id: id,
        sort_order: nextSortOrder++
      })
    }
  })
  
  // 检查是否有选择
  if (selectedApiIds.value.length === 0 && selectedFlowIds.value.length === 0) {
    ElMessage.warning('请至少选择一个接口或流程')
    return
  }
  
  addItemDialogVisible.value = false
  ElMessage.success(`成功添加 ${selectedApiIds.value.length + selectedFlowIds.value.length} 个项目`)
  
  // 清空选择
  selectedApiIds.value = []
  selectedFlowIds.value = []
}

const removeItem = (index: number) => {
  formData.value.items?.splice(index, 1)
}

const handleEdit = async (row: TestTask) => {
  try {
    const response = await getTestTask(row.id)
    // 处理响应格式：可能是数组或对象
    currentTask.value = Array.isArray(response) ? response[0] : (response.data || response)
    dialogTitle.value = '编辑任务'
    formData.value = {
      name: currentTask.value.name,
      project_id: currentTask.value.project_id,
      description: currentTask.value.description || '',
      items: (currentTask.value.items || []).map(item => ({
        item_type: item.item_type,
        item_id: item.item_id,
        sort_order: item.sort_order
      })),
      cron_expression: currentTask.value.cron_expression || '',
      environment_id: currentTask.value.environment_id
    }
    dialogVisible.value = true
    if (formData.value.project_id) {
      await loadAvailableApis()
      await loadAvailableFlows()
    }
  } catch (error: any) {
    ElMessage.error('加载任务详情失败: ' + (error.message || '未知错误'))
    console.error('加载任务详情失败:', error)
  }
}

const handleSave = async () => {
  if (!formData.value.name) {
    ElMessage.warning('请输入任务名称')
    return
  }
  if (!formData.value.project_id) {
    ElMessage.warning('请选择项目')
    return
  }
  
  saving.value = true
  try {
    if (dialogTitle.value === '新建任务') {
      await createTestTask(formData.value)
      ElMessage.success('创建成功')
      // 如果是新建任务，将筛选条件设置为新任务的项目，确保新任务能显示
      filters.value.project_id = formData.value.project_id
    } else {
      if (!currentTask.value) {
        ElMessage.error('无法获取任务ID')
        return
      }
      await updateTestTask(currentTask.value.id, formData.value)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    // 延迟一下再加载，确保后端数据已保存
    await new Promise(resolve => setTimeout(resolve, 100))
    loadTasks()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// 监听项目变化
const watchProjectId = () => {
  if (formData.value.project_id) {
    loadAvailableApis()
    loadAvailableFlows()
  }
}

// 监听项目切换事件
const handleProjectChanged = () => {
  // 项目切换后，自动刷新数据
  loadTasks()
}

onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized1()
  await ensureInitialized2()
  loadProjects()
  loadEnvironments()
  loadTasks()
  
  // 监听项目切换事件
  window.addEventListener('project:changed', handleProjectChanged)
})

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('project:changed', handleProjectChanged)
})
</script>

<style scoped>
.test-task-page {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-header {
  margin-bottom: 16px;
}

.filter-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 500;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-left {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-left > * {
  margin: 0;
}

.filter-right {
  display: flex;
  gap: 10px;
}

.table-card {
  margin-bottom: 20px;
}

.favorite-icon {
  transition: all 0.3s;
}

.favorite-icon.is-favorite {
  color: #f7ba2a !important;
}

.favorite-icon:hover {
  color: #f7ba2a !important;
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

.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dialog-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.dialog-description {
  font-size: 14px;
  color: #909399;
  line-height: 1.5;
}

.drawer-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.drawer-description {
  font-size: 14px;
  color: #909399;
}

.detail-content {
  padding: 20px;
}

.report-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.report-header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 20px 12px 20px;
  border-bottom: 2px solid #ebeef5;
}

.report-header-section h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.report-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px 20px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}

.executions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.execution-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.execution-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.execution-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f2f5;
}

.execution-card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.detail-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  border-radius: 8px !important;
  padding: 8px 20px !important;
  font-weight: 500 !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.3s ease !important;
}

.detail-button:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.detail-button .el-icon {
  margin-right: 4px;
}

.execution-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.execution-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}

.execution-time .el-icon {
  color: #909399;
  font-size: 16px;
}

.execution-status {
  flex-shrink: 0;
}

.execution-stats {
  display: flex;
  gap: 24px;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 80px;
}

.stat-item.success .stat-value {
  color: #67c23a;
  font-weight: 600;
}

.stat-item.failed .stat-value {
  color: #f56c6c;
  font-weight: 600;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-value {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.stat-value-small {
  font-size: 14px;
  color: #606266;
}

.execution-error {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  background: #fef0f0;
  border-radius: 6px;
  border-left: 3px solid #f56c6c;
  color: #f56c6c;
  font-size: 14px;
}

.execution-error .el-icon {
  font-size: 16px;
}

.execution-card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
}

.detail-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  border-radius: 8px !important;
  padding: 8px 20px !important;
  font-weight: 500 !important;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.3s ease !important;
}

.detail-button:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.detail-button .el-icon {
  margin-right: 4px;
}

.execution-detail-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.execution-detail-header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 16px 20px 12px 20px;
  border-bottom: 2px solid #ebeef5;
}

.execution-detail-header-section h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.execution-detail-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px 20px;
}

.assertion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

.assertion-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.assertion-row:hover {
  background: #f0f5ff;
}

.assertion-type {
  width: 120px;
}

.assertion-operator {
  width: 120px;
}

.assertion-target {
  flex: 1;
  min-width: 0;
}

.assertion-value {
  flex: 1;
  min-width: 0;
}

.execution-results-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.execution-result-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.execution-result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 0;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px 8px 0 0;
}

.execution-result-header:hover {
  background-color: #f5f7fa;
}

.expand-icon {
  transition: transform 0.3s;
  color: #909399;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.result-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.execution-result-content {
  display: flex;
  gap: 24px;
  min-height: 0;
  padding: 16px;
  border-top: 1px solid #ebeef5;
}

.execution-result-left,
.execution-result-right {
  flex: 1;
  overflow-y: auto;
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  min-width: 0;
  max-height: 600px;
}

.execution-result-left {
  border-right: 1px solid #ebeef5;
}

.param-tabs {
  margin-top: 16px;
}

.param-textarea {
  width: 100%;
}

.param-textarea :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.response-content {
  height: 100%;
}

.response-pre {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  max-height: 500px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.flow-step-item {
  margin-bottom: 24px;
  padding: 16px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.flow-step-item:last-child {
  margin-bottom: 0;
}

/* 自定义滚动条 */
.execution-result-left::-webkit-scrollbar,
.execution-result-right::-webkit-scrollbar {
  width: 6px;
}

.execution-result-left::-webkit-scrollbar-thumb,
.execution-result-right::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.execution-result-left::-webkit-scrollbar-thumb:hover,
.execution-result-right::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

:deep(.el-drawer) {
  border-radius: 12px 0 0 12px;
  overflow: hidden;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  height: 100vh !important;
}

:deep(.el-drawer__body) {
  padding: 0;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

:deep(.el-drawer__header) {
  background: linear-gradient(90deg, #f5f9ff, #f0f7ff);
  padding: 16px 20px;
  margin-bottom: 0;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-drawer__title) {
  font-weight: 600;
  color: #333;
}
</style>

