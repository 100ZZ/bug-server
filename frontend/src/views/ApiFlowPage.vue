<template>
  <div class="api-flow-page">
    <!-- 顶部：标题 + 筛选 + 新建按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Share /></el-icon>
          流程测试
        </h2>
      </div>
      <div class="filter-row">
        <el-select 
          v-model="flowFilters.project_id" 
          placeholder="选择项目" 
          clearable 
          style="width: 200px" 
          @change="loadFlows"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
        >
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-input
          v-model="flowFilters.keyword"
          placeholder="搜索流程名称"
          clearable
          @keyup.enter="loadFlows"
          @clear="loadFlows"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadFlows">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button 
          :type="flowFilters.showFavorite ? 'primary' : 'default'"
          :icon="Star"
          @click="toggleFavoriteFilter"
        >
          收藏
        </el-button>
        <el-button type="primary" style="margin-left: auto" @click="handleCreateFlow">
          <el-icon><Plus /></el-icon>
          新建流程
        </el-button>
      </div>
    </el-card>

    <!-- 底部：流程列表 -->
    <el-card class="table-card">
      <el-table
        :data="paginatedFlows"
        v-loading="flowLoading"
        stripe
        style="width: 100%"
        table-layout="fixed"
        :max-height="600"
        row-key="id"
      >
        <el-table-column label="编号" width="80" align="center" type="index" :index="(index: number) => (currentPage - 1) * pageSize + index + 1" />
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
        <el-table-column label="接口数量" width="120" align="center">
          <template #default="{ row }">
            <span class="endpoint-count-text" @click="showFlowEndpoints(row)">
              {{ row.steps?.length || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="handleEditFlow(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button link type="danger" @click="handleDeleteFlow(row)">
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
          :total="filteredFlows.length"
        />
      </div>
    </el-card>

    <!-- 流程配置抽屉 -->
    <el-drawer v-model="flowDrawerVisible" :with-header="false" size="80%" :close-on-click-modal="true">
      <div class="flow-editor-container">
        <!-- 左侧：执行链 -->
        <div class="flow-execution-chain">
          <div class="chain-header">
            <h3>执行链 ({{ flowForm.steps.length }})</h3>
            <div class="chain-actions">
              <el-button type="danger" @click="handleExecuteFlowFromEditor" :loading="flowExecuting" class="execute-btn" :disabled="flowExecuting">
                <el-icon><VideoPlay /></el-icon>
                {{ flowExecuting ? '执行中...' : '执行' }}
              </el-button>
              <el-button type="success" @click="handleSaveFlow">
                <el-icon><Check /></el-icon>
                保存
              </el-button>
              <el-button type="warning" @click="handleClearSteps">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
              <el-button @click="showExportDialog" class="export-btn">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <el-button @click="handleImportFlow" class="import-btn">
                <el-icon><Upload /></el-icon>
                导入
              </el-button>
              <el-button @click="flowDrawerVisible = false" type="info" class="close-btn">
                <el-icon><Close /></el-icon>
                关闭
              </el-button>
            </div>
          </div>
          
          <!-- 搜索框 -->
          <div class="chain-search">
            <el-input
              v-model="flowEndpointKeyword"
              placeholder="搜索接口名称或路径"
              clearable
              @keyup.enter="searchEndpoints"
            >
              <template #append>
                <el-button :icon="Search" @click="searchEndpoints" />
              </template>
            </el-input>
          </div>

          <!-- 接口搜索结果列表 -->
          <div v-if="flowEndpointKeyword.trim()" class="endpoint-search-results">
            <div
              v-for="endpoint in filteredFlowEndpoints"
              :key="endpoint.id"
              class="endpoint-search-item"
              @click="quickAddStep(endpoint)"
            >
              <el-tag :type="getMethodTag(endpoint.method)" size="small">{{ endpoint.method }}</el-tag>
              <span class="endpoint-name">{{ endpoint.name }}</span>
              <span class="endpoint-path">{{ endpoint.path }}</span>
              <el-button type="primary" @click.stop="quickAddStep(endpoint)" class="add-to-chain-btn">加入执行链</el-button>
            </div>
          </div>

          <!-- 执行链接口卡片列表 -->
          <div class="chain-steps">
            <template v-for="(step, index) in flowForm.steps" :key="index">
              <!-- 接口卡片 -->
              <div
                class="step-card"
                :class="{ 'step-active': selectedStepIndex === index, 'step-disabled': step.enabled === false }"
                @click="handleEditStep(index)"
              >
                <div class="step-number" :class="{ 'step-number-disabled': step.enabled === false }">{{ index + 1 }}</div>
                <div class="step-content">
                <div class="step-header">
                  <el-tag :type="getMethodTag(getEndpointMethod(step.endpoint_id))" size="small" :effect="step.enabled === false ? 'plain' : 'plain'">
                    {{ getEndpointMethod(step.endpoint_id) }}
                  </el-tag>
                  <span class="step-path" :class="{ 'step-path-disabled': step.enabled === false }">{{ getEndpointPath(step.endpoint_id) }}</span>
                </div>
                <div class="step-description">
                  <el-tag 
                    v-for="tag in (getEndpointInfo(step.endpoint_id)?.tags || [])" 
                    :key="tag" 
                    size="small" 
                    style="margin-right: 4px"
                    :effect="step.enabled === false ? 'plain' : 'dark'"
                  >
                    {{ tag }}
                  </el-tag>
                  <span :class="{ 'step-description-disabled': step.enabled === false }">{{ getEndpointName(step.endpoint_id) || '-' }}</span>
                </div>
                <div class="step-status" :class="{ 'step-status-disabled': step.enabled === false }">
                  {{ step.enabled === false ? '已禁用，执行时将跳过' : '尚未执行,点击右上角开始' }}
                </div>
              </div>
              <div class="step-actions">
                <el-button 
                  link 
                  size="small" 
                  @click.stop="toggleStepEnabled(index)"
                  :type="step.enabled === false ? 'success' : 'warning'"
                  :title="step.enabled === false ? '启用此接口' : '禁用此接口'"
                  class="toggle-enable-btn"
                >
                  <el-icon><View v-if="step.enabled === false" /><Hide v-else /></el-icon>
                </el-button>
                <el-button link size="small" @click.stop="moveStepUp(index)" :disabled="index === 0">
                  <el-icon><ArrowUp /></el-icon>
                </el-button>
                <el-button link size="small" @click.stop="moveStepDown(index)" :disabled="index === flowForm.steps.length - 1">
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <el-button link size="small" @click.stop="duplicateStep(index)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
                <el-button link type="danger" size="small" @click.stop="removeStep(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              </div>
              <!-- 序号之间的连接线 -->
              <div v-if="index < flowForm.steps.length - 1" class="step-connector">
                <svg class="connector-svg" viewBox="0 0 30 32" preserveAspectRatio="xMidYMid meet">
                  <line
                    x1="15"
                    y1="0"
                    x2="15"
                    y2="32"
                    stroke="#d1d5db"
                    stroke-width="2"
                  />
                </svg>
              </div>
            </template>
            <div v-if="flowForm.steps.length === 0" class="empty-chain">
              <el-empty description="暂无接口，请搜索并添加到执行链" :image-size="100" />
            </div>
          </div>
        </div>

        <!-- 右侧：执行配置 -->
        <div class="flow-execution-config">
          <!-- 执行配置 -->
          <div class="config-section">
            <h3>执行配置</h3>
            <el-form :model="executionConfig" label-width="80px" size="default" class="execution-config-form">
              <el-form-item label="所属项目" required>
                <el-select 
                  v-model="flowForm.project_id" 
                  placeholder="选择项目" 
                  style="width: 100%" 
                  @change="onProjectChange"
                  :disabled="hasProjectSelected"
                  :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
                >
                  <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="流程名称" required>
                <el-input v-model="flowForm.name" placeholder="请输入流程名称" style="width: 100%" />
              </el-form-item>
              <el-form-item label="执行环境">
                <el-select v-model="executionConfig.environment_id" placeholder="选择环境" style="width: 100%">
                  <el-option
                    v-for="env in allEnvironments"
                    :key="env.id"
                    :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
                    :value="env.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="执行失败">
                <el-radio-group v-model="executionConfig.failAction">
                  <el-radio label="stop">停止执行</el-radio>
                  <el-radio label="continue">继续执行</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="延迟(ms)">
                <el-input-number
                  v-model="executionConfig.delay"
                  :min="0"
                  :max="10000"
                  :step="100"
                  style="width: 100%"
                />
              </el-form-item>
              <el-form-item label="当前时间">
                <div style="display: flex; gap: 8px;">
                  <el-button type="primary" @click="showGenerateDialog('timestamp')" class="generate-variable-btn">时间戳</el-button>
                  <el-button type="primary" @click="showGenerateDialog('timepoint')" class="generate-variable-btn">时间点</el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>

          <!-- 局部变量 -->
          <div class="config-section">
            <div class="section-header">
              <h3>
                局部变量
                <el-tooltip
                  effect="dark"
                  placement="top"
                  :show-after="200"
                >
                  <template #content>
                    <div style="font-size: 13px; line-height: 1.6; max-width: 450px;">
                      <div style="margin-bottom: 8px;"><strong>使用说明：</strong></div>
                      <div style="margin-bottom: 4px;">1. 定义变量名和变量值，点击"保存"保存</div>
                      <div style="margin-bottom: 4px;">2. 在接口参数中使用以下方式引用变量：</div>
                      <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">$变量名</code> - 传统方式</div>
                      <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">NUM($变量名)</code> - 数字类型，无需引号</div>
                      <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">STR($变量名)</code> - 字符串类型，自动添加引号</div>
                      <div style="margin-bottom: 4px;">3. <strong>使用示例：</strong></div>
                      <div style="margin-bottom: 4px;">   • 数字值：<code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"id": NUM($Tenant)}</code> 或 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"id": $userId}</code></div>
                      <div style="margin-bottom: 4px;">   • 字符串值：<code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"name": STR($Token)}</code> 或 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"name": "$Tenant"}</code></div>
                      <div>4. 变量可以在所有接口的参数中使用，支持引用前面接口返回的值（使用 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">$API[N].path</code>）</div>
                    </div>
                  </template>
                  <el-icon style="margin-left: 4px; cursor: pointer; color: #909399; font-size: 14px;">
                    <QuestionFilled />
                  </el-icon>
                </el-tooltip>
              </h3>
            </div>
            <div class="local-variables-list">
              <div
                v-for="(variable, index) in localVariables"
                :key="variable.id || index"
                class="variable-row"
              >
                <el-input v-model="variable.key" placeholder="变量名" class="variable-input" />
                <el-input v-model="variable.value" placeholder="变量值" class="variable-input" />
                <el-button link type="primary" size="small" @click="copyVariableReference(variable.key)" class="variable-copy-btn" title="复制变量引用">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
                <el-button type="danger" size="small" @click="removeLocalVariable(index)" class="variable-delete-btn" title="删除">
                  <el-icon><Delete /></el-icon>
                </el-button>
                <el-button link type="primary" size="small" @click="addLocalVariableAfter(index)" class="white-text-btn" title="新增">
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="variable-actions">
              <el-button v-if="localVariables.length === 0" type="primary" @click="addLocalVariable" class="white-text-btn">
                <el-icon><Plus /></el-icon>
                新增变量
              </el-button>
              <el-button type="success" @click="saveLocalVariables" class="white-text-btn">保存</el-button>
            </div>
          </div>

          <!-- 执行统计 -->
          <div class="config-section">
            <div class="section-header">
              <h3>执行统计</h3>
              <el-button type="primary" @click="showExecutionDetails = true" class="execution-details-btn">执行详情</el-button>
            </div>
            <div class="statistics-boxes">
              <div class="stat-box stat-total">
                <div class="stat-label">总数</div>
                <div class="stat-value">{{ executionStats.total }}</div>
              </div>
              <div class="stat-box stat-success">
                <div class="stat-label">成功</div>
                <div class="stat-value">{{ executionStats.success }}</div>
              </div>
              <div class="stat-box stat-failure">
                <div class="stat-label">失败</div>
                <div class="stat-value">{{ executionStats.failure }}</div>
              </div>
            </div>
            <div class="execution-progress">
              <el-progress
                :percentage="executionStats.total > 0 ? Math.round((executionStats.success + executionStats.failure) / executionStats.total * 100) : 0"
                :status="executionStats.failure > 0 ? 'exception' : 'success'"
              />
            </div>
          </div>
        </div>
      </div>
    </el-drawer>

      <!-- 生成变量对话框 -->
      <el-dialog v-model="showGenerateVariableDialog" width="500px">
        <template #header>
          <div class="dialog-header">
            <span class="dialog-title">{{ generateDialogTitle }}</span>
            <span class="dialog-description">{{ generateDialogTitle === '时间戳' ? '生成当前时间的Unix时间戳（毫秒），可用于接口参数中的时间字段' : '生成当前时间的格式化时间点（Asia/Shanghai时区），可用于接口参数中的时间字段' }}</span>
          </div>
        </template>
        <el-form label-width="100px">
          <el-form-item :label="generateDialogTitle">
            <el-input v-model="generatedValue" readonly />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button type="primary" @click="copyGeneratedValue" class="generate-dialog-btn">复制</el-button>
          <el-button @click="showGenerateVariableDialog = false" class="generate-dialog-close-btn">关闭</el-button>
        </template>
      </el-dialog>

      <!-- 执行详情对话框 -->
      <!-- 执行详情抽屉 -->
      <el-drawer v-model="showExecutionDetails" :with-header="false" size="75%" :close-on-click-modal="true">
        <div class="execution-details-wrapper">
          <div class="execution-details-header-section">
            <h3>执行详情</h3>
          </div>
          <div v-if="flowExecutionResult && flowExecutionResult.results && flowExecutionResult.results.length > 0" class="execution-details-container">
            <template v-for="(item, index) in flowExecutionResult.results" :key="index">
            <div class="execution-details-item">
              <div class="execution-details-header" @click="toggleResultDetail(index)">
                <div class="execution-details-header-number">
                  <div class="step-number">{{ item.index !== undefined ? item.index : index + 1 }}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
                  <el-tag :type="getMethodTag(item.method || getEndpointInfo(item.endpoint_id)?.method || 'GET')" size="small">
                    {{ item.method || getEndpointInfo(item.endpoint_id)?.method || '-' }}
                  </el-tag>
                  <span class="result-name">{{ getEndpointInfo(item.endpoint_id)?.name || item.url || `接口 #${index + 1}` }}</span>
                  <span class="result-path">{{ getEndpointInfo(item.endpoint_id)?.path || item.url || '-' }}</span>
                </div>
              <div style="display: flex; align-items: center; gap: 12px; cursor: pointer;">
                <el-tag :type="item.success ? 'success' : 'danger'" size="small">
                  {{ item.success ? '成功' : '失败' }}
                </el-tag>
                <el-tag size="small" type="info">
                  {{ item.response_time ? `${item.response_time}ms` : '-' }}
                </el-tag>
                <el-icon :class="['expand-icon', { 'expanded': expandedResultIndices.has(index) }]">
                  <ArrowDown />
                </el-icon>
              </div>
            </div>
            
            <div v-show="expandedResultIndices.has(index)" class="execution-details-content">
              <!-- 左侧：请求参数 -->
              <div class="execution-details-left">
                <!-- 顶部信息 -->
                <div style="margin-bottom: 16px;" v-if="getEndpointInfo(item.endpoint_id)">
                  <el-descriptions :column="3" border>
                    <el-descriptions-item label="标签">
                      <el-tag v-for="tag in (getEndpointInfo(item.endpoint_id)?.tags || [])" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="方法">
                      <el-tag :type="getMethodTag(item.method || getEndpointInfo(item.endpoint_id)?.method || 'GET')">
                        {{ item.method || getEndpointInfo(item.endpoint_id)?.method || '-' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="路径">{{ getEndpointInfo(item.endpoint_id)?.path || item.url || '-' }}</el-descriptions-item>
                  </el-descriptions>
                </div>
                
                <el-divider>请求参数</el-divider>
                <el-tabs v-model="executionDetailActiveTabs[index]" class="param-tabs">
                  <el-tab-pane label="Header" name="headers">
                    <el-input
                      :value="item.request_headers ? JSON.stringify(item.request_headers, null, 2) : '{\n\n}'"
                      type="textarea"
                      class="param-textarea param-textarea-fixed"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Query" name="query_params">
                    <el-input
                      :value="item.request_query_params ? JSON.stringify(item.request_query_params, null, 2) : '{\n\n}'"
                      type="textarea"
                      class="param-textarea param-textarea-fixed"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Body" name="body">
                    <el-input
                      :value="item.request_body ? formatResponseBody(item.request_body) : '{\n\n}'"
                      type="textarea"
                      class="param-textarea param-textarea-fixed"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Path" name="path_params">
                    <el-input
                      :value="item.request_path_params ? JSON.stringify(item.request_path_params, null, 2) : '{\n\n}'"
                      type="textarea"
                      class="param-textarea param-textarea-fixed"
                      readonly
                    />
                  </el-tab-pane>
                  <el-tab-pane label="Assertion" name="assertions">
                    <div v-if="item.request_assertions && item.request_assertions.length > 0" class="assertion-list">
                      <div
                        v-for="(assertion, idx) in item.request_assertions"
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
              <div class="execution-details-right">
                <el-divider>响应信息</el-divider>
                <div class="response-content">
                  <el-descriptions :column="1" border style="margin-bottom: 16px;">
                    <el-descriptions-item label="状态">
                      <el-tag :type="item.success ? 'success' : 'danger'">
                        {{ item.success ? '成功' : '失败' }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="响应状态码">
                      {{ item.status || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="响应时间">
                      {{ item.response_time ? `${item.response_time}ms` : '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="请求URL">
                      {{ item.url || '-' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="错误信息" v-if="item.error_message">
                      <el-text type="danger" style="white-space: pre-wrap;">{{ item.error_message }}</el-text>
                    </el-descriptions-item>
                  </el-descriptions>
                  
                  <el-tabs>
                    <el-tab-pane label="Header">
                      <pre class="response-pre">{{ formatJsonObject(item.request_headers || {}) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="Query">
                      <pre class="response-pre">{{ formatJsonObject(item.request_query_params || {}) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="Body">
                      <pre class="response-pre">{{ formatResponseBody(item.request_body) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="Path">
                      <pre class="response-pre">{{ formatJsonObject(item.request_path_params || {}) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="响应头">
                      <pre class="response-pre">{{ formatJsonObject(item.response_headers || {}) }}</pre>
                    </el-tab-pane>
                    <el-tab-pane label="响应体">
                      <pre class="response-pre">{{ formatResponseBody(item.response_body) }}</pre>
                    </el-tab-pane>
                  </el-tabs>
                </div>
              </div>
            </div>
            </div>
            <!-- 序号之间的连接线 -->
            <div v-if="index < flowExecutionResult.results.length - 1" class="step-connector">
              <svg class="connector-svg" viewBox="0 0 30 32" preserveAspectRatio="xMidYMid meet">
                <line
                  x1="15"
                  y1="0"
                  x2="15"
                  y2="32"
                  stroke="#d1d5db"
                  stroke-width="2"
                />
              </svg>
            </div>
            </template>
          </div>
          <div v-else class="execution-details-container">
            <el-empty description="暂无执行记录" />
          </div>
        </div>
      </el-drawer>

    <!-- 接口列表对话框 -->
    <el-dialog v-model="showEndpointsDialog" width="900px" align-center :show-close="true" :close-on-click-modal="true" class="endpoints-dialog-centered">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">接口列表</span>
          <span class="dialog-description">当前流程包含的所有接口，按执行顺序排列</span>
        </div>
      </template>
      <el-table :data="paginatedFlowEndpoints" border>
        <el-table-column label="编号" width="80" align="center">
          <template #default="{ $index }">
            {{ (endpointsDialogPage - 1) * endpointsDialogPageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column prop="method" label="方法" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getMethodTag(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" show-overflow-tooltip />
        <el-table-column prop="name" label="接口名称" show-overflow-tooltip />
      </el-table>
      <div v-if="selectedFlowEndpoints.length > 0" style="margin-top: 16px; text-align: right;">
        <el-pagination
          v-model:current-page="endpointsDialogPage"
          v-model:page-size="endpointsDialogPageSize"
          :page-sizes="[10]"
          layout="prev, pager, next, ->, total"
          :total="selectedFlowEndpoints.length"
          small
        />
      </div>
    </el-dialog>

    <!-- 导出流程对话框 -->
    <el-dialog v-model="showExportDialogVisible" width="500px" :close-on-click-modal="true">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">导出流程</span>
          <span class="dialog-description">选择导出方式：保存到本地或文件管理</span>
        </div>
      </template>
      <el-form :model="exportForm" label-width="100px">
        <el-form-item label="文件名称" required>
          <el-input v-model="exportForm.name" placeholder="请输入文件名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="exportForm.description" type="textarea" :rows="2" placeholder="请输入描述（可选）" />
        </el-form-item>
        <el-form-item label="保存方式">
          <el-radio-group v-model="exportForm.saveType">
            <el-radio label="local">保存到本地</el-radio>
            <el-radio label="fileManage">保存到文件管理</el-radio>
            <el-radio label="both">同时保存</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="showExportDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="exporting" @click="handleExportFlow">确认导出</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导入流程对话框 -->
    <el-dialog v-model="showImportDialog" width="1000px" :close-on-click-modal="true" @closed="clearImportData">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">导入流程</span>
          <span class="dialog-description">可以从文件或文件管理中导入流程数据</span>
        </div>
      </template>
      <el-tabs v-model="importTab">
        <el-tab-pane label="从文件导入" name="file">
          <el-upload
            :key="uploadKey"
            ref="fileUploadRef"
            :auto-upload="false"
            :on-change="handleFileImportChange"
            :on-exceed="handleFileExceed"
            :limit="1"
            accept=".json"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持导出的JSON格式文件
              </div>
            </template>
          </el-upload>
          <div v-if="importFileData" style="margin-top: 16px;">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="流程名称">{{ importFileData.flow?.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="描述">{{ importFileData.flow?.description || '-' }}</el-descriptions-item>
              <el-descriptions-item label="接口数量">{{ importFileData.flow?.steps?.length || 0 }}</el-descriptions-item>
              <el-descriptions-item label="局部变量数量">{{ importFileData.variables?.length || 0 }}</el-descriptions-item>
            </el-descriptions>
            <div style="margin-top: 16px; text-align: center;">
              <el-button type="primary" @click="doImportFromFile">导入为新流程</el-button>
              <el-button v-if="editingFlowId" @click="doImportFromFileToCurrent">导入到当前流程</el-button>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="从文件管理导入" name="fileManage">
          <div style="margin-bottom: 12px;">
            <el-input
              v-model="fileManageKeyword"
              placeholder="搜索文件名称"
              clearable
              style="width: 200px; margin-right: 12px;"
              @keyup.enter="loadTestFilesForImport"
            />
            <el-button @click="loadTestFilesForImport">搜索</el-button>
          </div>
          <div v-if="testFilesForImport.length === 0" style="text-align: center; padding: 40px;">
            <el-empty description="暂无可导入的文件" />
          </div>
          <div v-else>
            <el-table :data="paginatedTestFiles" style="width: 100%" table-layout="fixed" max-height="400" v-loading="loadingTestFiles">
              <el-table-column prop="name" label="文件名称" min-width="180" align="center" show-overflow-tooltip />
              <el-table-column prop="description" label="描述" min-width="200" align="center" show-overflow-tooltip>
                <template #default="{ row }">{{ row.description || '-' }}</template>
              </el-table-column>
              <el-table-column prop="file_type" label="类型" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.file_type === 'flow' ? 'success' : 'primary'" size="small">
                    {{ row.file_type === 'flow' ? '流程' : '本地' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="260" align="center" fixed="right">
                <template #default="{ row }">
                  <div class="table-actions">
                    <el-button link type="primary" @click="doImportFromFileManage(row.id, true)">导入为新流程</el-button>
                    <el-button v-if="editingFlowId" link type="primary" @click="doImportFromFileManage(row.id, false)">导入到当前流程</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            <div style="margin-top: 12px; text-align: right;">
              <el-pagination
                v-model:current-page="importFilePage"
                v-model:page-size="importFilePageSize"
                :page-sizes="[10]"
                layout="prev, pager, next, ->, total"
                :total="testFilesForImport.length"
                small
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showImportDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 执行进度对话框 -->
    <el-dialog v-model="flowExecuting" title="执行进度" width="600px" :close-on-click-modal="false" :show-close="false" :close-on-press-escape="false">
      <div class="execution-progress-dialog">
        <div class="progress-header">
          <el-icon class="progress-icon" :class="{ 'progress-icon-success': executionProgressStatus === 'success', 'progress-icon-error': executionProgressStatus === 'exception' }">
            <Loading v-if="executionProgressStatus === ''" />
            <CircleCheck v-else-if="executionProgressStatus === 'success'" />
            <CircleClose v-else-if="executionProgressStatus === 'exception'" />
          </el-icon>
          <div class="progress-title">
            <div class="progress-title-main">
              {{ executionProgressStatus === 'success' ? '执行完成' : executionProgressStatus === 'exception' ? '执行失败' : '正在执行流程' }}
            </div>
            <div class="progress-title-sub">
              {{ executionProgressStatus === '' ? (currentExecutingStep > 0 ? `正在执行第 ${currentExecutingStep} / ${enabledStepsCount} 个接口` : `准备执行，共 ${enabledStepsCount} 个接口`) : `共执行 ${enabledStepsCount} 个接口` }}
            </div>
          </div>
        </div>
        <div class="progress-bar-container">
          <el-progress 
            :percentage="executionProgress" 
            :status="executionProgressStatus" 
            :stroke-width="20" 
            :indeterminate="executionProgress === 0"
            :format="(percentage) => `${percentage}%`"
          />
        </div>
        <div v-if="currentExecutingStep > 0 && currentExecutingStep <= enabledStepsCount && executionProgressStatus === ''" class="progress-step-info">
          <el-tag type="info" size="large">步骤 {{ currentExecutingStep }}: {{ getStepName(currentExecutingStep - 1) }}</el-tag>
        </div>
        <div v-if="executionProgressStatus !== ''" class="progress-stats">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="总接口数">{{ enabledStepsCount }}</el-descriptions-item>
            <el-descriptions-item label="执行进度">{{ executionProgress }}%</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="flowResultDialogVisible" title="流程执行结果" width="800px" :close-on-click-modal="true">
      <div v-if="flowExecutionResult">
        <el-result :icon="flowExecutionResult.success ? 'success' : 'error'" :title="flowExecutionResult.success ? '执行成功' : '执行失败'" />
        <el-timeline style="margin-top: 12px;">
          <el-timeline-item v-for="item in flowExecutionResult.results" :key="item.index" :type="item.success ? 'success' : 'danger'" :timestamp="`#${item.index} ${item.response_time || 0}ms`">
            <div><strong>{{ item.endpoint_name || item.endpoint_id }}</strong> - {{ item.url }}</div>
            <div>状态码：{{ item.status || '-' }}</div>
            <div v-if="item.error_message" style="color: #f56c6c">{{ item.error_message }}</div>
            <div v-if="item.extracted && Object.keys(item.extracted).length">提取：{{ item.extracted }}</div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button @click="flowResultDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 编辑执行链接口抽屉 -->
    <el-drawer v-model="stepEditDrawerVisible" :title="`编辑接口 #${editingStepIndex + 1}${flowForm.steps.length > 0 ? ` / ${flowForm.steps.length}` : ''}`" size="75%" :close-on-click-modal="true">
      
      <div v-if="editingStepIndex >= 0 && editingStep" class="step-edit-container">
        <div class="step-edit-content">
          <!-- 左侧：请求参数 -->
          <div class="step-edit-left">
            <!-- 顶部信息 -->
            <div style="margin-bottom: 16px;" v-if="editingEndpoint">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="标签">
                  <el-tag v-for="tag in (editingEndpoint.tags || [])" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="方法">
                  <el-tag :type="getMethodTag(editingEndpoint.method)">
                    {{ editingEndpoint.method || '-' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="路径">{{ editingEndpoint.path || '-' }}</el-descriptions-item>
              </el-descriptions>
            </div>
            
            <el-divider>
              <span>请求参数</span>
              <el-tooltip
                effect="dark"
                placement="top"
                :show-after="200"
              >
                <template #content>
                  <div style="font-size: 13px; line-height: 1.6; max-width: 450px;">
                    <div style="margin-bottom: 8px;"><strong>引用前面接口的返回值：</strong></div>
                    <div style="margin-bottom: 4px;"><strong>使用 $ 关键字语法引用变量：</strong></div>
                    <div style="margin-bottom: 4px;">1. 引用前面接口的返回值：</div>
                    <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">$API[N].path</code> - 传统方式</div>
                    <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">NUM($API[N].path)</code> - 数字类型，无需引号</div>
                    <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">STR($API[N].path)</code> - 字符串类型，自动添加引号</div>
                    <div style="margin-bottom: 4px;">   例如：<code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">$API[1].data.code</code> 或 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">NUM($API[1].data.id)</code></div>
                    <div style="margin-bottom: 4px;">2. 引用局部变量：</div>
                    <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">$变量名</code> - 传统方式</div>
                    <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">NUM($变量名)</code> - 数字类型</div>
                    <div style="margin-bottom: 4px;">   • <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">STR($变量名)</code> - 字符串类型</div>
                    <div style="margin-bottom: 4px;">   例如：<code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">$Tenant</code> 或 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">STR($Token)</code></div>
                    <div style="margin-bottom: 4px;">3. <strong>JSON 中使用示例：</strong></div>
                    <div style="margin-bottom: 4px;">   • 数字值：<code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"id": NUM($API[1].data.id)}</code> 或 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"id": $API[1].data}</code></div>
                    <div>   • 字符串值：<code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"name": STR($API[1].data.name)}</code> 或 <code style="background: rgba(255,255,255,0.2); padding: 2px 4px; border-radius: 3px;">{"name": "$API[1].data.name"}</code></div>
                  </div>
                </template>
                <el-icon style="margin-left: 4px; cursor: pointer; color: #909399; font-size: 14px;">
                  <QuestionFilled />
                </el-icon>
              </el-tooltip>
            </el-divider>
            
            <!-- 局部变量快捷引用 -->
            <div v-if="localVariables.length > 0" class="variables-quick-ref">
              <div class="quick-ref-label">
                <el-icon><Tickets /></el-icon>
                <span>局部变量（点击复制）：</span>
              </div>
              <div class="quick-ref-buttons">
                <el-dropdown
                  v-for="variable in localVariables"
                  :key="variable.key"
                  trigger="click"
                  @command="(command) => copyVariableWithFormat(variable.key, command)"
                >
                  <el-button
                    size="small"
                    class="variable-quick-btn"
                  >
                    ${{ variable.key }}
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="STR">
                        <el-icon><DocumentCopy /></el-icon>
                        STR(${{ variable.key }})
                      </el-dropdown-item>
                      <el-dropdown-item command="NUM">
                        <el-icon><DocumentCopy /></el-icon>
                        NUM(${{ variable.key }})
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            
            <el-tabs v-model="activeParamTab" class="param-tabs">
              <el-tab-pane label="Header" name="headers">
                <el-input
                  v-model="stepHeadersText"
                  type="textarea"
                  class="param-textarea param-textarea-fixed"
                  placeholder='JSON格式，例如：{"Authorization": "Bearer token"}'
                />
              </el-tab-pane>
              <el-tab-pane label="Query" name="query_params">
                <el-input
                  v-model="stepQueryParamsText"
                  type="textarea"
                  class="param-textarea param-textarea-fixed"
                  placeholder='JSON格式，例如：{"page": 1, "size": 10}'
                />
              </el-tab-pane>
              <el-tab-pane label="Body" name="body">
                <el-input
                  v-model="stepBodyText"
                  type="textarea"
                  class="param-textarea param-textarea-fixed"
                  placeholder='JSON格式，例如：{"name": "test", "age": 18}'
                />
              </el-tab-pane>
              <el-tab-pane label="Path" name="path_params">
                <el-input
                  v-model="stepPathParamsText"
                  type="textarea"
                  class="param-textarea param-textarea-fixed"
                  placeholder='JSON格式，例如：{"id": 123}'
                />
              </el-tab-pane>
              <el-tab-pane label="Assertion" name="assertions">
                <div class="assertion-list">
                  <div
                    v-for="(item, index) in stepAssertions"
                    :key="index"
                    class="assertion-row"
                  >
                    <el-select v-model="item.type" class="assertion-type">
                      <el-option label="状态码" value="status_code" />
                      <el-option label="JSON路径" value="json_path" />
                      <el-option label="响应时间" value="response_time" />
                      <el-option label="包含" value="contains" />
                    </el-select>
                    <el-input
                      v-if="item.type === 'json_path'"
                      v-model="item.target"
                      class="assertion-target"
                      placeholder="例如：data.id"
                    />
                    <el-select v-model="item.operator" class="assertion-operator">
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
                      v-model="item.expected"
                      class="assertion-value"
                      placeholder="期望值，例如：200"
                    />
                    <el-button link type="danger" @click="removeStepAssertion(index)">删除</el-button>
                    <el-button link type="primary" @click="addStepAssertion(index)">新增</el-button>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
          
          <!-- 右侧：响应信息 -->
          <div class="step-edit-right">
            <el-divider>响应信息</el-divider>
            <div v-if="!stepExecutionResult" class="no-response">
              <el-empty description="执行接口后显示响应信息" :image-size="100" />
            </div>
            <div v-else class="response-content">
              <el-descriptions :column="1" border style="margin-bottom: 16px;">
                <el-descriptions-item label="状态">
                  <el-tag :type="stepExecutionResult.success ? 'success' : 'danger'">
                    {{ stepExecutionResult.success ? '成功' : '失败' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="响应状态码">
                  {{ stepExecutionResult.response_status || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="响应时间">
                  {{ stepExecutionResult.response_time ? `${stepExecutionResult.response_time}ms` : '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="执行时间">
                  {{ formatDate(stepExecutionResult.executed_at) }}
                </el-descriptions-item>
                <el-descriptions-item label="请求URL">
                  {{ stepExecutionResult.request_url || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="错误信息" v-if="stepExecutionResult.error_message">
                  <el-text type="danger" style="white-space: pre-wrap;">{{ stepExecutionResult.error_message }}</el-text>
                </el-descriptions-item>
              </el-descriptions>
              
              <el-tabs>
                <el-tab-pane label="Header">
                  <pre class="response-pre">{{ formatJsonObject(stepExecutionResult.request_headers || {}) }}</pre>
                </el-tab-pane>
                <el-tab-pane label="Query">
                  <pre class="response-pre">{{ formatJsonObject(stepExecutionResult.request_query_params || {}) }}</pre>
                </el-tab-pane>
                <el-tab-pane label="Body">
                  <pre class="response-pre">{{ formatResponseBody(stepExecutionResult.request_body) }}</pre>
                </el-tab-pane>
                <el-tab-pane label="Path">
                  <pre class="response-pre">{{ formatJsonObject(stepExecutionResult.request_path_params || {}) }}</pre>
                </el-tab-pane>
                <el-tab-pane label="响应头">
                  <pre class="response-pre">{{ formatJsonObject(stepExecutionResult.response_headers || {}) }}</pre>
                </el-tab-pane>
                <el-tab-pane label="响应体">
                  <pre class="response-pre">{{ formatResponseBody(stepExecutionResult.response_body) }}</pre>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: space-between; align-items: center;">
          <!-- 按钮区域 -->
          <div style="display: flex; gap: 10px;">
            <el-button type="primary" :loading="stepExecuting" @click="handleStepExecuteSubmit">执行</el-button>
            <el-button @click="handleStepSave">保存</el-button>
            <el-button 
              v-if="editingStepIndex < flowForm.steps.length - 1"
              type="primary" 
              @click="handleNextStep"
            >
              下一个
            </el-button>
            <el-button 
              v-else
              @click="stepEditDrawerVisible = false"
            >
              完成
            </el-button>
          </div>
          <!-- 序号显示 - 使用紫色圆形图标 -->
          <div class="step-number">{{ editingStepIndex + 1 }}</div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, EditPen, VideoPlay, Delete, Plus, ArrowUp, ArrowDown, CopyDocument, Upload, UploadFilled, Download, QuestionFilled, Check, Close, Loading, CircleCheck, CircleClose, View, Hide, Star, StarFilled, Share, Tickets, DocumentCopy, InfoFilled } from '@element-plus/icons-vue'
import * as apitestApi from '../api/apitest'
import * as projectApi from '../api/projects'
import { useProjectContext } from '../composables/useProjectContext'
import type { ApiEndpoint, ApiEnvironment, Project, ApiTestFlow, FlowStep, FlowExecuteResult } from '../api/types'

// 数据
const flows = ref<ApiTestFlow[]>([])
const projects = ref<Project[]>([])
const allEnvironments = ref<ApiEnvironment[]>([])
const endpoints = ref<ApiEndpoint[]>([])
const flowLoading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

const flowFilters = reactive({
  project_id: undefined as number | undefined,
  keyword: '',
  showFavorite: false
})

const filteredFlows = computed(() => {
  // 后端已经过滤了，这里直接返回
  return flows.value
})

// 分页后的数据
const paginatedFlows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFlows.value.slice(start, end)
})

// 流程相关
const flowDrawerVisible = ref(false)
const flowDrawerTitle = ref('新建流程')
const editingFlowId = ref<number>()
const flowResultDialogVisible = ref(false)
const flowExecutionResult = ref<FlowExecuteResult | null>(null)
const flowForm = reactive({
  project_id: undefined as number | undefined,
  name: '',
  description: '',
  environment_id: undefined as number | undefined,
  global_variables_text: '{\n}',
  steps: [] as FlowStep[]
})

const stepDraft = reactive({
  endpoint_id: undefined as number | undefined,
  environment_id: undefined as number | undefined,
  test_data_id: undefined as number | undefined,
  alias: '',
  path_params_text: '',
  query_params_text: '',
  headers_text: '',
  body_text: '',
})

const flowEndpointKeyword = ref('')
const flowEndpoints = ref<ApiEndpoint[]>([])
const selectedStepIndex = ref<number>(-1)

// 规范化步骤数据，确保enabled字段存在
const normalizeStep = (step: FlowStep): FlowStep => {
  return {
    ...step,
    enabled: step.enabled !== false  // 确保enabled字段存在，默认为true
  }
}

// 规范化步骤数组
const normalizeSteps = (steps: FlowStep[]): FlowStep[] => {
  return steps.map(normalizeStep)
}

// 计算启用的步骤数量
const enabledStepsCount = computed(() => {
  return flowForm.steps.filter(step => step.enabled !== false).length
})

// 执行配置
const executionConfig = reactive({
  environment_id: undefined as number | undefined,
  failAction: 'stop' as 'stop' | 'continue',
  delay: 1000
})

// 局部变量
const localVariables = ref<Array<{ id?: number; key: string; value: string }>>([])

// 生成变量对话框
const showGenerateVariableDialog = ref(false)
const generatedValue = ref('')
const generateDialogTitle = ref('')

// 执行统计
const executionStats = reactive({
  total: 0,
  success: 0,
  failure: 0
})

// 执行详情
const showExecutionDetails = ref(false)
const executionDetailActiveTabs = ref<Record<number, string>>({})
const expandedResultIndices = ref<Set<number>>(new Set())

// 接口列表对话框
const showEndpointsDialog = ref(false)
const selectedFlowEndpoints = ref<ApiEndpoint[]>([])
const endpointsDialogPage = ref(1)
const endpointsDialogPageSize = ref(10)

// 分页后的接口列表
const paginatedFlowEndpoints = computed(() => {
  const start = (endpointsDialogPage.value - 1) * endpointsDialogPageSize.value
  return selectedFlowEndpoints.value.slice(start, start + endpointsDialogPageSize.value)
})

// 导出对话框
const showExportDialogVisible = ref(false)
const exporting = ref(false)
const exportForm = reactive({
  name: '',
  description: '',
  saveType: 'local' as 'local' | 'fileManage' | 'both'
})

// 导入对话框
const showImportDialog = ref(false)
const importTab = ref('file')
const flowExports = ref<any[]>([])
const fileUploadRef = ref()
const importFileData = ref<any>(null)
const uploadKey = ref(0) // 用于强制重新渲染文件上传组件

// 文件管理导入
const testFilesForImport = ref<any[]>([])
const loadingTestFiles = ref(false)
const fileManageKeyword = ref('')
const importFilePage = ref(1)
const importFilePageSize = ref(10)

// 分页后的文件列表
const paginatedTestFiles = computed(() => {
  const start = (importFilePage.value - 1) * importFilePageSize.value
  return testFilesForImport.value.slice(start, start + importFilePageSize.value)
})

// 编辑执行链接口抽屉
const stepEditDrawerVisible = ref(false)
const availableVariablesCollapse = ref(['variables']) // 可用变量折叠面板状态
const editingStepIndex = ref<number>(-1)
const editingStep = computed(() => {
  if (editingStepIndex.value >= 0 && flowForm.steps[editingStepIndex.value]) {
    return flowForm.steps[editingStepIndex.value]
  }
  return null
})
const activeParamTab = ref('headers')
const stepPathParamsText = ref('')
const stepQueryParamsText = ref('')
const stepHeadersText = ref('')
const stepBodyText = ref('')
const stepExecuting = ref(false)
const stepExecutionResult = ref<any>(null)
const stepTestDataList = ref<any[]>([])
const editingEndpoint = ref<ApiEndpoint | null>(null)
const stepAssertions = ref<Array<{ type: string; operator: string; target?: string; expected?: string }>>([])

const filteredFlowEndpoints = computed(() => {
  const keyword = flowEndpointKeyword.value.trim().toLowerCase()
  if (!keyword) return []
  return flowEndpoints.value.filter(ep =>
    ep.name.toLowerCase().includes(keyword) ||
    ep.path.toLowerCase().includes(keyword)
  )
})

// 加载流程列表
const loadFlows = async () => {
  flowLoading.value = true
  try {
    const params: any = {
      keyword: flowFilters.keyword.trim() || undefined,
      is_favorite: flowFilters.showFavorite ? true : undefined
    }
    
    // 优先使用当前项目过滤
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
    } else if (flowFilters.project_id) {
      params.project_id = flowFilters.project_id
    }
    
    flows.value = await apitestApi.getApiFlows(params)
  } catch (error: any) {
    ElMessage.error({ message: error.message || '加载流程失败', duration: 2000 })
  } finally {
    flowLoading.value = false
  }
}

// 重置筛选
const handleReset = () => {
  flowFilters.project_id = undefined
  flowFilters.keyword = ''
  flowFilters.showFavorite = false
  loadFlows()
}

// 切换收藏筛选
const toggleFavoriteFilter = () => {
  flowFilters.showFavorite = !flowFilters.showFavorite
  loadFlows()
}

// 收藏/取消收藏流程
const handleToggleFavorite = async (row: ApiTestFlow) => {
  try {
    const newFavoriteStatus = !row.is_favorite
    await apitestApi.toggleFavoriteFlow(row.id, newFavoriteStatus)
    row.is_favorite = newFavoriteStatus
    ElMessage.success({ message: newFavoriteStatus ? '已收藏' : '已取消收藏', duration: 1000 })
    // 如果当前在收藏筛选模式下，取消收藏后需要重新加载列表
    if (flowFilters.showFavorite && !newFavoriteStatus) {
      loadFlows()
    }
  } catch (error: any) {
    ElMessage.error({ message: error.message || '操作失败', duration: 2000 })
  }
}

const { 
  getProjects: getFilteredProjects,
  getCurrentProjectId,
  hasProjectSelected,
  onProjectChanged,
  ensureInitialized
} = useProjectContext()

// 加载项目列表 - 使用 useProjectContext 的 getProjects，会自动根据选中的项目过滤
const loadProjects = async () => {
  try {
    projects.value = await getFilteredProjects()
    
    // 如果有选中的项目，自动设置过滤器
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      flowFilters.project_id = getCurrentProjectId.value
    }
  } catch (error: any) {
    ElMessage.error({ message: error.message || '加载项目列表失败', duration: 2000 })
  }
}

// 加载环境列表
const loadEnvironments = async () => {
  try {
    allEnvironments.value = await apitestApi.getApiEnvironments()
  } catch (error: any) {
    ElMessage.error({ message: error.message || '加载环境列表失败', duration: 2000 })
  }
}

// 加载流程变量
const loadFlowVariables = async (flowId: number) => {
  try {
    const variables = await apitestApi.getFlowVariables(flowId)
    localVariables.value = variables.map(v => ({
      id: v.id,
      key: v.key,
      value: v.value
    }))
    // 同时更新全局变量对象（用于向后兼容）
    const vars: Record<string, string> = {}
    variables.forEach(v => {
      vars[v.key] = v.value
    })
    flowForm.global_variables_text = JSON.stringify(vars, null, 2)
  } catch (error: any) {
    // 如果API不存在，使用旧的全局变量方式
    const row = flows.value.find(f => f.id === flowId)
    if (row?.global_variables) {
      localVariables.value = Object.entries(row.global_variables).map(([key, value]) => ({
        key,
        value: String(value)
      }))
    } else {
      // 默认显示一个空行
      localVariables.value = [{ key: '', value: '' }]
    }
  }
}

// 流程操作
const resetFlowForm = () => {
  Object.assign(flowForm, {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : (flowFilters.project_id || projects.value[0]?.id),
    name: '',
    description: '',
    environment_id: undefined,
    global_variables_text: '{\n}',
    steps: []
  })
  flowEndpointKeyword.value = ''
  flowEndpoints.value = []
  localVariables.value = [{ key: '', value: '' }]  // 默认显示一个空行
  Object.assign(stepDraft, {
    endpoint_id: undefined,
    environment_id: undefined,
    test_data_id: undefined,
    alias: '',
    path_params_text: '',
    query_params_text: '',
    headers_text: '',
    body_text: '',
  })
}

const handleCreateFlow = () => {
  editingFlowId.value = undefined
  flowDrawerTitle.value = '新建流程'
  resetFlowForm()
  // 加载当前项目下的接口列表，方便添加到执行链
  if (flowForm.project_id) {
    apitestApi
      .getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
      .then(data => {
        flowEndpoints.value = data
        endpoints.value = data
      })
      .catch(() => {
        flowEndpoints.value = []
        endpoints.value = []
      })
  }
  flowDrawerVisible.value = true
}

const handleEditFlow = async (row: ApiTestFlow) => {
  editingFlowId.value = row.id
  flowDrawerTitle.value = '编辑流程'
  
  // 从服务器重新加载流程数据，确保获取最新数据（包括已保存的参数）
  try {
    const freshFlow = await apitestApi.getApiFlow(row.id)
    flowForm.project_id = freshFlow.project_id
    flowForm.name = freshFlow.name
    flowForm.description = freshFlow.description || ''
    flowForm.environment_id = freshFlow.environment_id
    flowForm.global_variables_text = freshFlow.global_variables ? JSON.stringify(freshFlow.global_variables, null, 2) : '{\n}'
      flowForm.steps = freshFlow.steps ? normalizeSteps(freshFlow.steps) : []
  } catch (error: any) {
    // 如果获取失败，使用列表中的数据
    console.error('加载流程详情失败，使用列表数据:', error)
    flowForm.project_id = row.project_id
    flowForm.name = row.name
    flowForm.description = row.description || ''
    flowForm.environment_id = row.environment_id
    flowForm.global_variables_text = row.global_variables ? JSON.stringify(row.global_variables, null, 2) : '{\n}'
    flowForm.steps = row.steps ? normalizeSteps(row.steps) : []
  }
  
  // 加载局部变量
  loadFlowVariables(row.id)
  
  // 设置执行配置
  executionConfig.environment_id = flowForm.environment_id
  executionStats.total = flowForm.steps?.length || 0
  
  // 加载该项目下接口列表
  apitestApi
    .getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
    .then(data => {
      flowEndpoints.value = data
      endpoints.value = data
    })
    .catch(() => {
      flowEndpoints.value = []
      endpoints.value = []
    })
  flowDrawerVisible.value = true
}

const handleDeleteFlow = async (row: ApiTestFlow) => {
  try {
    await ElMessageBox.confirm('确定删除该流程吗？', '提示', { type: 'warning' })
    await apitestApi.deleteApiFlow(row.id)
    ElMessage.success({ message: '删除成功', duration: 1000 })
    loadFlows()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error({ message: error.message || '删除失败', duration: 2000 })
  }
}

const handleAddStep = () => {
  if (!stepDraft.endpoint_id) {
    ElMessage.warning({ message: '请选择接口', duration: 1500 })
    return
  }
  try {
    const newStep: FlowStep = {
      endpoint_id: stepDraft.endpoint_id,
      environment_id: stepDraft.environment_id,
      test_data_id: stepDraft.test_data_id,
      alias: stepDraft.alias || undefined,
      enabled: true,  // 默认启用
      path_params: stepDraft.path_params_text ? JSON.parse(stepDraft.path_params_text) : undefined,
      query_params: stepDraft.query_params_text ? JSON.parse(stepDraft.query_params_text) : undefined,
      headers: stepDraft.headers_text ? JSON.parse(stepDraft.headers_text) : undefined,
      body: stepDraft.body_text ? JSON.parse(stepDraft.body_text) : undefined
    }
    flowForm.steps.push(newStep)
    Object.assign(stepDraft, {
      endpoint_id: undefined,
      environment_id: undefined,
      test_data_id: undefined,
      alias: '',
      path_params_text: '',
      query_params_text: '',
      headers_text: '',
      body_text: ''
    })
  } catch (error) {
    ElMessage.error({ message: '步骤参数格式错误，请检查 JSON', duration: 2000 })
  }
}

const removeStep = (index: number) => {
  flowForm.steps.splice(index, 1)
}

const moveStepUp = (index: number) => {
  if (index <= 0) return
  const item = flowForm.steps[index]
  flowForm.steps.splice(index, 1)
  flowForm.steps.splice(index - 1, 0, item)
}

const moveStepDown = (index: number) => {
  if (index >= flowForm.steps.length - 1) return
  const item = flowForm.steps[index]
  flowForm.steps.splice(index, 1)
  flowForm.steps.splice(index + 1, 0, item)
}

const duplicateStep = (index: number) => {
  const item = flowForm.steps[index]
  const copy = JSON.parse(JSON.stringify(item)) as FlowStep
  // 确保复制的步骤默认启用
  copy.enabled = copy.enabled !== false
  flowForm.steps.splice(index + 1, 0, copy)
}

// 切换步骤的启用/禁用状态
const toggleStepEnabled = (index: number) => {
  if (index < 0 || index >= flowForm.steps.length) return
  const step = flowForm.steps[index]
  // 如果enabled为undefined，默认为true，所以需要显式设置为false
  // 如果enabled为false，设置为true
  step.enabled = step.enabled === false ? true : false
}

const quickAddStep = async (endpoint: ApiEndpoint) => {
  try {
    // 加载该接口的测试数据
    const testDataList = await apitestApi.getApiTestDataList(endpoint.id)
    let defaultTestData = testDataList.length > 0 ? testDataList[0] : null
    
    // 如果没有测试数据，创建一个默认的
    if (!defaultTestData) {
      defaultTestData = await apitestApi.createApiTestData({
        endpoint_id: endpoint.id,
        name: '测试数据#默认',
        expected_status: 200,
        path_params: {},
        query_params: {},
        headers: {},
        body: {}
      })
    }
    
    // 构建新的步骤，同步测试数据
    const newStep: FlowStep = {
      endpoint_id: endpoint.id,
      alias: endpoint.name,
      test_data_id: defaultTestData.id,
      enabled: true,  // 默认启用
      // 同步测试数据中的参数（单向同步，不会影响接口测试的数据）
      path_params: defaultTestData.path_params ? JSON.parse(JSON.stringify(defaultTestData.path_params)) : undefined,
      query_params: defaultTestData.query_params ? JSON.parse(JSON.stringify(defaultTestData.query_params)) : undefined,
      headers: defaultTestData.headers ? JSON.parse(JSON.stringify(defaultTestData.headers)) : undefined,
      body: defaultTestData.body ? JSON.parse(JSON.stringify(defaultTestData.body)) : undefined,
      // 同步断言（从测试数据的expected_status生成默认断言，如果有assertions则使用）
      assertions: defaultTestData.assertions && Array.isArray(defaultTestData.assertions) && defaultTestData.assertions.length > 0
        ? defaultTestData.assertions.map((a: any) => ({
            type: a.type || 'status_code',
            operator: a.operator || 'eq',
            target: a.target || undefined,
            expected: a.expected !== undefined && a.expected !== null ? String(a.expected) : undefined
          }))
        : [{ type: 'status_code', operator: 'eq', expected: String(defaultTestData.expected_status || 200) }]
    }
    
    flowForm.steps.push(newStep)
    executionStats.total = flowForm.steps.length
    // 不再清空搜索框，保持搜索结果下拉框显示，方便继续添加接口
    ElMessage.success({ message: '已添加到执行链', duration: 1000 })
  } catch (error: any) {
    console.error('添加步骤失败:', error)
    ElMessage.error({ message: error.message || '添加到执行链失败', duration: 2000 })
  }
}

const handleSaveFlow = async () => {
  if (!flowForm.project_id || !flowForm.name) {
    ElMessage.warning({ message: '请完善流程信息', duration: 1500 })
    return
  }
  
  // 使用局部变量构建全局变量对象
  const vars: Record<string, string> = {}
  localVariables.value.forEach(v => {
    if (v.key.trim() && v.value.trim()) {
      vars[v.key] = v.value
    }
  })
  const globalVars = Object.keys(vars).length > 0 ? vars : undefined
  
  // 同步执行配置到流程表单
  if (executionConfig.environment_id) {
    flowForm.environment_id = executionConfig.environment_id
  }
  
  const payload: Partial<ApiTestFlow> = {
    project_id: flowForm.project_id,
    name: flowForm.name,
    description: flowForm.description,
    environment_id: flowForm.environment_id,
    global_variables: globalVars,
    steps: flowForm.steps
  }
  try {
    if (editingFlowId.value) {
      await apitestApi.updateApiFlow(editingFlowId.value, payload)
      ElMessage.success({ message: '更新成功', duration: 1500 })
      loadFlows() // 只有更新成功才刷新列表
    } else {
      const result = await apitestApi.createApiFlow(payload)
      editingFlowId.value = result.id
      flowDrawerTitle.value = '编辑流程'
      ElMessage.success({ message: '创建成功', duration: 1500 })
      loadFlows() // 只有创建成功才刷新列表
    }
  } catch (error: any) {
    // 提取错误信息
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    
    // 如果是名称重复错误，弹出提示框
    if (errorMessage.includes('同名流程') || errorMessage.includes('已存在')) {
      await ElMessageBox.alert(errorMessage, '提示', {
        type: 'warning',
        confirmButtonText: '确定'
      })
    } else {
      ElMessage.error({ message: errorMessage, duration: 2000 })
    }
    // 保存失败时不刷新列表，避免显示未保存的流程
  }
}

const handleExecuteFlow = async (row: ApiTestFlow) => {
  try {
    const result = await apitestApi.executeApiFlow(row.id, { environment_id: row.environment_id, global_variables: row.global_variables })
    flowExecutionResult.value = result
    flowResultDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error({ message: error.message || '执行失败', duration: 2000 })
  }
}

// 从编辑器执行流程
const flowExecuting = ref(false)
const executionProgress = ref(0)
const executionProgressStatus = ref<'success' | 'exception' | 'warning' | ''>('')
const currentExecutingStep = ref(0) // 当前执行的步骤索引（从1开始）

const handleExecuteFlowFromEditor = async () => {
  if (flowForm.steps.length === 0) {
    ElMessage.warning({ message: '执行链为空，请先添加接口', duration: 1500 })
    return
  }
  if (!executionConfig.environment_id) {
    ElMessage.warning({ message: '请选择执行环境', duration: 1500 })
    return
  }
  
  // 初始化进度
  flowExecuting.value = true
  executionProgress.value = 0
  executionProgressStatus.value = ''
  currentExecutingStep.value = 0
  
  // 过滤掉被禁用的步骤
  const enabledSteps = flowForm.steps.filter(step => step.enabled !== false)
  if (enabledSteps.length === 0) {
    ElMessage.warning({ message: '没有启用的接口，请至少启用一个接口', duration: 1500 })
    flowExecuting.value = false
    return
  }
  
  // 进度更新定时器
  let progressTimer: NodeJS.Timeout | null = null
  let progressComplete = false
  let shouldStopProgress = false
  const totalSteps = enabledSteps.length
  const delayMs = executionConfig.delay || 1000
  
  // 启动进度条更新（模拟逐步执行）
  const startProgressUpdate = () => {
    let currentStep = 0
    progressTimer = setInterval(() => {
      // 如果应该停止，立即停止更新
      if (shouldStopProgress) {
        clearInterval(progressTimer!)
        progressTimer = null
        return
      }
      
      currentStep++
      if (currentStep <= totalSteps) {
        // 找到当前执行的是第几个启用的步骤
        let enabledIndex = 0
        for (let i = 0; i < flowForm.steps.length; i++) {
          if (flowForm.steps[i].enabled !== false) {
            enabledIndex++
            if (enabledIndex === currentStep) {
              currentExecutingStep.value = i + 1
              break
            }
          }
        }
        executionProgress.value = Math.round((currentStep / totalSteps) * 100)
      } else {
        // 进度条已到100%，停止更新
        clearInterval(progressTimer!)
        progressTimer = null
      }
    }, delayMs)
  }
  
  try {
    // 使用局部变量构建全局变量对象
    const vars: Record<string, string> = {}
    localVariables.value.forEach(v => {
      if (v.key.trim() && v.value.trim()) {
        vars[v.key] = v.value
      }
    })
    // 构建执行请求
    const executeData: any = {
      environment_id: executionConfig.environment_id,
      global_variables: Object.keys(vars).length > 0 ? vars : undefined,
      failAction: executionConfig.failAction || 'stop',
      delay: executionConfig.delay || 0  // 传递步骤间延迟到后端
    }
    
    // 启动进度条更新
    startProgressUpdate()
    
    let result: any = null
    
    // 如果有编辑中的流程ID，直接执行
    if (editingFlowId.value) {
      result = await apitestApi.executeApiFlow(editingFlowId.value, executeData)
    } else {
      // 否则先保存再执行
      await handleSaveFlow()
      if (editingFlowId.value) {
        result = await apitestApi.executeApiFlow(editingFlowId.value, executeData)
      }
    }
    
    // 标记进度完成
    progressComplete = true
    
    // 检查执行结果，如果失败且设置了停止执行，立即停止进度条
    if (result && result.results && result.results.length > 0) {
      const failedResults = result.results.filter((r: any) => !r.success)
      if (failedResults.length > 0 && executionConfig.failAction === 'stop') {
        // 找到第一个失败的步骤索引
        const firstFailedIndex = result.results.findIndex((r: any) => !r.success)
        const failedStepNumber = firstFailedIndex + 1
        // 计算失败步骤的进度
        const failedProgress = Math.round((failedStepNumber / totalSteps) * 100)
        shouldStopProgress = true
        // 立即停止进度条并设置为失败步骤的进度
        if (progressTimer) {
          clearInterval(progressTimer)
          progressTimer = null
        }
        executionProgress.value = failedProgress
      } else {
        // 继续执行或全部成功，等待进度条到100%
        if (executionProgress.value < 100 && progressTimer) {
          const currentProgress = executionProgress.value
          const remainingProgress = 100 - currentProgress
          const progressPerStep = 100 / totalSteps
          const remainingSteps = Math.ceil(remainingProgress / progressPerStep)
          await new Promise(resolve => setTimeout(resolve, remainingSteps * delayMs))
        }
        
        // 确保进度条到100%
        if (progressTimer) {
          clearInterval(progressTimer)
          progressTimer = null
        }
        executionProgress.value = 100
      }
    } else {
      // 如果没有结果，正常完成进度条
      if (executionProgress.value < 100 && progressTimer) {
        const currentProgress = executionProgress.value
        const remainingProgress = 100 - currentProgress
        const progressPerStep = 100 / totalSteps
        const remainingSteps = Math.ceil(remainingProgress / progressPerStep)
        await new Promise(resolve => setTimeout(resolve, remainingSteps * delayMs))
      }
      
      // 确保进度条到100%
      if (progressTimer) {
        clearInterval(progressTimer)
        progressTimer = null
      }
      executionProgress.value = 100
    }
    
    if (result) {
      flowExecutionResult.value = result
      updateExecutionStats(result)
      executionProgressStatus.value = result.success ? 'success' : 'exception'
      // 延迟一下再关闭进度对话框并打开执行详情抽屉
      setTimeout(() => {
        flowExecuting.value = false
        showExecutionDetails.value = true
      }, 800)
    }
  } catch (error: any) {
    // 清除定时器
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    ElMessage.error({ message: error.message || '执行失败', duration: 2000 })
    executionProgressStatus.value = 'exception'
    executionProgress.value = 100
  } finally {
    // 清除定时器
    if (progressTimer) {
      clearInterval(progressTimer)
      progressTimer = null
    }
    // 如果执行失败，延迟一下再隐藏进度
    if (executionProgressStatus.value === 'exception') {
      setTimeout(() => {
        flowExecuting.value = false
        executionProgress.value = 0
        executionProgressStatus.value = ''
        currentExecutingStep.value = 0
      }, 1500)
    } else {
      // 成功的情况已经在上面处理了，这里只需要重置状态
      executionProgress.value = 0
      executionProgressStatus.value = ''
      currentExecutingStep.value = 0
    }
  }
}

// 更新执行统计
const updateExecutionStats = (result: FlowExecuteResult) => {
  executionStats.total = result.results?.length || 0
  executionStats.success = result.results?.filter(r => r.success).length || 0
  executionStats.failure = result.results?.filter(r => !r.success).length || 0
}

// 清空执行链
const handleClearSteps = () => {
  ElMessageBox.confirm('确定清空执行链吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(() => {
    flowForm.steps = []
    executionStats.total = 0
    executionStats.success = 0
    executionStats.failure = 0
    ElMessage.success({ message: '已清空', duration: 1000 })
  }).catch(() => {})
}

// 显示导出对话框
const showExportDialog = () => {
  if (!editingFlowId.value) {
    ElMessage.warning({ message: '请先保存流程', duration: 1500 })
    return
  }
  exportForm.name = flowForm.name || '流程导出'
  exportForm.description = ''
  exportForm.saveType = 'local'
  showExportDialogVisible.value = true
}

// 导出流程
const handleExportFlow = async () => {
  if (!editingFlowId.value) {
    ElMessage.warning({ message: '请先保存流程', duration: 1500 })
    return
  }
  
  if (!exportForm.name) {
    ElMessage.warning({ message: '请输入文件名称', duration: 1500 })
    return
  }
  
  exporting.value = true
  
  try {
    // 构建完整的导出数据
    const exportData = {
      version: "1.0",
      exportTime: new Date().toISOString(),
      flow: {
        name: flowForm.name,
        description: flowForm.description,
        project_id: flowForm.project_id,
        environment_id: flowForm.environment_id || executionConfig.environment_id,
        global_variables: flowForm.global_variables_text ? JSON.parse(flowForm.global_variables_text) : {},
        steps: flowForm.steps || []
      },
      executionConfig: {
        environment_id: executionConfig.environment_id,
        failAction: executionConfig.failAction,
        delay: executionConfig.delay
      },
      variables: localVariables.value
        .filter(v => v.key.trim() && v.value.trim())
        .map(v => ({
          key: v.key.trim(),
          value: v.value.trim()
        }))
    }
    
    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').replace(/T/g, '_').slice(0, 19)
    const safeName = exportForm.name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5\s-_]/g, '').trim() || 'flow'
    const fileName = `${safeName}_${timestamp}.json`
    
    // 根据保存类型处理
    if (exportForm.saveType === 'local' || exportForm.saveType === 'both') {
      // 创建文件并下载
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    
    if (exportForm.saveType === 'fileManage' || exportForm.saveType === 'both') {
      // 保存到文件管理
      await apitestApi.createTestFile({
        name: exportForm.name,
        description: exportForm.description,
        file_type: 'flow',
        file_content: exportData,
        flow_id: editingFlowId.value
      })
    }
    
    // 同时保存到数据库导出记录
    try {
      await apitestApi.exportApiFlow(editingFlowId.value)
    } catch (dbError) {
      console.warn('保存到数据库失败:', dbError)
    }
    
    showExportDialogVisible.value = false
    
    if (exportForm.saveType === 'local') {
      ElMessage.success({ message: `导出成功，文件已下载：${fileName}`, duration: 1500 })
    } else if (exportForm.saveType === 'fileManage') {
      ElMessage.success({ message: '导出成功，已保存到文件管理', duration: 1500 })
    } else {
      ElMessage.success({ message: `导出成功，文件已下载并保存到文件管理`, duration: 1500 })
    }
  } catch (error: any) {
    ElMessage.error({ message: '导出失败: ' + (error.message || '未知错误'), duration: 2000 })
  } finally {
    exporting.value = false
  }
}

// 加载文件管理列表（用于导入）
const loadTestFilesForImport = async () => {
  loadingTestFiles.value = true
  try {
    const response = await apitestApi.getTestFiles({
      keyword: fileManageKeyword.value || undefined,
      page: 1,
      page_size: 50
    })
    testFilesForImport.value = response.items
  } catch (error: any) {
    ElMessage.error({ message: '加载文件列表失败: ' + (error.message || '未知错误'), duration: 2000 })
  } finally {
    loadingTestFiles.value = false
  }
}

// 从文件管理导入
const doImportFromFileManage = async (fileId: number, asNew: boolean) => {
  try {
    const content = await apitestApi.getTestFileContent(fileId)
    
    if (!content || !content.flow) {
      ElMessage.error({ message: '文件内容无效', duration: 2000 })
      return
    }
    
    if (asNew) {
      // 导入为新流程
      await ElMessageBox.confirm(
        '确定要将此文件导入为新流程吗？',
        '确认导入',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        }
      )
      
      // 使用导入数据创建新流程
      await doImportAsNewFlow(content)
    } else {
      // 导入到当前流程
      await ElMessageBox.confirm(
        '导入将覆盖当前流程的所有数据（接口、执行配置、局部变量），是否继续？',
        '确认导入',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      await doImportToCurrentFlow(content)
    }
    
    showImportDialog.value = false
    ElMessage.success({ message: '导入成功', duration: 1500 })
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error({ message: '导入失败: ' + (error.message || '未知错误'), duration: 2000 })
    }
  }
}

// 导入为新流程（辅助函数）
const doImportAsNewFlow = async (data: any) => {
  // 重置表单
  flowForm.project_id = data.flow?.project_id
  flowForm.name = '' // 流程名称留空，让用户自己输入
  flowForm.description = data.flow?.description || ''
  flowForm.environment_id = data.flow?.environment_id || data.executionConfig?.environment_id
  flowForm.global_variables_text = data.flow?.global_variables ? JSON.stringify(data.flow.global_variables, null, 2) : '{\n}'
  flowForm.steps = data.flow?.steps ? normalizeSteps(data.flow.steps) : []
  
  // 更新执行配置
  if (data.executionConfig) {
    executionConfig.environment_id = data.executionConfig.environment_id
    executionConfig.failAction = data.executionConfig.failAction || 'stop'
    executionConfig.delay = data.executionConfig.delay || 500
  }
  
  // 更新局部变量
  if (data.variables && Array.isArray(data.variables)) {
    localVariables.value = data.variables.map((v: any) => ({
      key: v.key || '',
      value: v.value || ''
    }))
  } else {
    localVariables.value = []
  }
  
  // 加载执行链中接口的详细信息
  await loadStepEndpoints()
  
  // 清空编辑ID，表示这是新流程
  editingFlowId.value = undefined
}

// 导入到当前流程（辅助函数）
const doImportToCurrentFlow = async (data: any) => {
  if (!editingFlowId.value) {
    throw new Error('请先保存流程')
  }
  
  // 更新流程数据（不修改流程名称，保持当前名称）
  const updateData: any = {
    description: data.flow?.description !== undefined ? data.flow.description : '',
    project_id: data.flow?.project_id || flowForm.project_id,
    environment_id: data.flow?.environment_id || data.executionConfig?.environment_id,
    global_variables: data.flow?.global_variables || {},
    steps: data.flow?.steps || []
  }
  
  const updatedFlow = await apitestApi.updateApiFlow(editingFlowId.value, updateData)
  
  // 更新表单（保持当前名称不变）
  flowForm.description = data.flow?.description || updatedFlow.description || ''
  flowForm.project_id = updatedFlow.project_id
  flowForm.environment_id = updatedFlow.environment_id
  flowForm.global_variables_text = updatedFlow.global_variables ? JSON.stringify(updatedFlow.global_variables, null, 2) : '{\n}'
  flowForm.steps = updatedFlow.steps ? normalizeSteps(updatedFlow.steps) : []
  
  // 加载执行链中接口的详细信息
  await loadStepEndpoints()
  
  // 更新执行配置
  if (data.executionConfig) {
    executionConfig.environment_id = data.executionConfig.environment_id
    executionConfig.failAction = data.executionConfig.failAction || 'stop'
    executionConfig.delay = data.executionConfig.delay || 500
  }
  
  // 更新局部变量
  if (data.variables && Array.isArray(data.variables)) {
    localVariables.value = data.variables.map((v: any) => ({
      key: v.key || '',
      value: v.value || ''
    }))
  }
}

// 加载执行链中接口的详细信息
const loadStepEndpoints = async () => {
  if (flowForm.steps.length > 0) {
    const stepEndpointIds = flowForm.steps.map(step => step.endpoint_id).filter(id => id) as number[]
    if (stepEndpointIds.length > 0) {
      try {
        if (flowForm.project_id) {
          try {
            const projectEndpoints = await apitestApi.getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
            flowEndpoints.value = projectEndpoints
            endpoints.value = projectEndpoints
          } catch (error) {
            // 忽略错误
          }
        }
        
        const allEndpoints = await apitestApi.getApiEndpoints({ limit: 1000 })
        const missingIds = stepEndpointIds.filter(id => !endpoints.value.find(ep => ep.id === id))
        if (missingIds.length > 0) {
          const missingEndpoints = allEndpoints.filter(ep => missingIds.includes(ep.id))
          endpoints.value = [...endpoints.value, ...missingEndpoints]
        }
      } catch (error) {
        console.error('加载接口信息失败:', error)
      }
    }
  }
}

// 清理导入相关的数据
const clearImportData = () => {
  importFileData.value = null
  if (fileUploadRef.value) {
    fileUploadRef.value.clearFiles()
  }
  // 增加 key 值，强制重新渲染文件上传组件
  uploadKey.value++
}

// 导入流程
const handleImportFlow = async () => {
  // 如果有编辑中的流程，加载数据库导出记录
  if (editingFlowId.value) {
    try {
      flowExports.value = await apitestApi.getFlowExports(editingFlowId.value)
    } catch (error: any) {
      console.warn('加载导出记录失败:', error)
      flowExports.value = []
    }
  } else {
    flowExports.value = []
  }
  
  // 加载文件管理列表
  fileManageKeyword.value = ''
  loadTestFilesForImport()
  
  // 重置导入数据
  clearImportData()
  importTab.value = 'file'
  
  // 显示导入对话框
  showImportDialog.value = true
}

// 处理文件超出限制（用户选择了新文件）
const handleFileExceed = (files: any) => {
  // 清除旧文件
  if (fileUploadRef.value) {
    fileUploadRef.value.clearFiles()
  }
  // 添加新文件
  const file = files[0]
  if (file) {
    fileUploadRef.value.handleStart(file)
    handleFileImportChange({ raw: file })
  }
}

// 处理文件导入
const handleFileImportChange = (file: any) => {
  // 先清除旧的文件数据，确保新文件的处理是干净的
  importFileData.value = null
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      const data = JSON.parse(content)
      importFileData.value = data
    } catch (error) {
      ElMessage.error({ message: '文件格式错误，请选择有效的JSON文件', duration: 2000 })
      importFileData.value = null
    }
  }
  reader.readAsText(file.raw)
}

// 从文件导入为新流程
const doImportFromFile = async () => {
  if (!importFileData.value) {
    ElMessage.warning({ message: '请先选择文件', duration: 1500 })
    return
  }
  
  try {
    const data = importFileData.value
    
    
    // 重置表单
    flowForm.project_id = data.flow?.project_id
    flowForm.name = '' // 流程名称留空，让用户自己输入
    flowForm.description = data.flow?.description || ''
    flowForm.environment_id = data.flow?.environment_id || data.executionConfig?.environment_id
    flowForm.global_variables_text = data.flow?.global_variables ? JSON.stringify(data.flow.global_variables, null, 2) : '{\n}'
    flowForm.steps = data.flow?.steps ? normalizeSteps(data.flow.steps) : []
    
    // 更新执行配置
    if (data.executionConfig) {
      executionConfig.environment_id = data.executionConfig.environment_id
      executionConfig.failAction = data.executionConfig.failAction || 'stop'
      executionConfig.delay = data.executionConfig.delay || 500
    }
    
    // 更新局部变量
    if (data.variables && Array.isArray(data.variables)) {
      localVariables.value = data.variables.map((v: any) => ({
        key: v.key || '',
        value: v.value || ''
      }))
    } else {
      localVariables.value = []
    }
    
    // 加载执行链中接口的详细信息，以便在执行链中显示接口名称、路径等
    if (flowForm.steps.length > 0) {
      const stepEndpointIds = flowForm.steps.map(step => step.endpoint_id).filter(id => id) as number[]
      if (stepEndpointIds.length > 0) {
        try {
          // 如果有项目ID，先加载项目下的接口
          if (flowForm.project_id) {
            try {
              const projectEndpoints = await apitestApi.getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
              flowEndpoints.value = projectEndpoints
              endpoints.value = projectEndpoints
            } catch (error) {
              // 忽略错误，继续加载所有接口
            }
          }
          
          // 加载所有接口，以便找到执行链中的接口
          const allEndpoints = await apitestApi.getApiEndpoints({ limit: 1000 })
          const missingIds = stepEndpointIds.filter(id => !endpoints.value.find(ep => ep.id === id))
          if (missingIds.length > 0) {
            const missingEndpoints = allEndpoints.filter(ep => missingIds.includes(ep.id))
            endpoints.value = [...endpoints.value, ...missingEndpoints]
          }
        } catch (error) {
          console.error('加载接口信息失败:', error)
          // 即使加载失败，也不阻止导入
        }
      }
    }
    
    // 清空编辑ID，表示这是新流程
    editingFlowId.value = undefined
    
    // 清理导入数据和文件列表
    clearImportData()
    
    showImportDialog.value = false
    ElMessage.success({ message: '导入成功，请保存流程', duration: 1500 })
  } catch (error: any) {
    // 如果是名称重复错误，弹出提示框
    const errorMsg = error.message || error.response?.data?.detail || '未知错误'
    if (errorMsg.includes('同名流程') || errorMsg.includes('已存在同名')) {
      await ElMessageBox.alert(errorMsg, '提示', {
        type: 'warning',
        confirmButtonText: '确定'
      })
    } else {
      ElMessage.error({ message: '导入失败: ' + errorMsg, duration: 2000 })
    }
  }
}

// 从文件导入到当前流程
const doImportFromFileToCurrent = async () => {
  if (!editingFlowId.value) {
    ElMessage.warning({ message: '请先保存流程', duration: 1500 })
    return
  }
  
  if (!importFileData.value) {
    ElMessage.warning({ message: '请先选择文件', duration: 1500 })
    return
  }
  
  try {
    const data = importFileData.value
    
    
    await ElMessageBox.confirm(
      '导入将覆盖当前流程的所有数据（接口、执行配置、局部变量），是否继续？',
      '确认导入',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 更新流程数据（不修改流程名称，保持当前名称）
    const updateData: any = {
      description: data.flow?.description !== undefined ? data.flow.description : '',
      project_id: data.flow?.project_id || flowForm.project_id,
      environment_id: data.flow?.environment_id || data.executionConfig?.environment_id,
      global_variables: data.flow?.global_variables || {},
      steps: data.flow?.steps || []
    }
    // 注意：不更新 name 字段，保持当前流程的名称不变
    
    const updatedFlow = await apitestApi.updateApiFlow(editingFlowId.value, updateData)
    
    // 更新表单（保持当前名称不变）
    flowForm.name = flowForm.name  // 保持原名称
    flowForm.description = data.flow?.description || updatedFlow.description || ''
    flowForm.project_id = updatedFlow.project_id
    flowForm.environment_id = updatedFlow.environment_id
    flowForm.global_variables_text = updatedFlow.global_variables ? JSON.stringify(updatedFlow.global_variables, null, 2) : '{\n}'
    flowForm.steps = updatedFlow.steps ? normalizeSteps(updatedFlow.steps) : []
    
    // 加载执行链中接口的详细信息，以便在执行链中显示接口名称、路径等
    if (flowForm.steps.length > 0) {
      const stepEndpointIds = flowForm.steps.map(step => step.endpoint_id).filter(id => id) as number[]
      if (stepEndpointIds.length > 0) {
        try {
          // 如果有项目ID，先加载项目下的接口
          if (flowForm.project_id) {
            try {
              const projectEndpoints = await apitestApi.getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
              flowEndpoints.value = projectEndpoints
              endpoints.value = projectEndpoints
            } catch (error) {
              // 忽略错误，继续加载所有接口
            }
          }
          
          // 加载所有接口，以便找到执行链中的接口
          const allEndpoints = await apitestApi.getApiEndpoints({ limit: 1000 })
          const missingIds = stepEndpointIds.filter(id => !endpoints.value.find(ep => ep.id === id))
          if (missingIds.length > 0) {
            const missingEndpoints = allEndpoints.filter(ep => missingIds.includes(ep.id))
            endpoints.value = [...endpoints.value, ...missingEndpoints]
          }
        } catch (error) {
          console.error('加载接口信息失败:', error)
          // 即使加载失败，也不阻止导入
        }
      }
    }
    
    // 更新执行配置
    if (data.executionConfig) {
      executionConfig.environment_id = data.executionConfig.environment_id
      executionConfig.failAction = data.executionConfig.failAction || 'stop'
      executionConfig.delay = data.executionConfig.delay || 500
    }
    
    // 更新局部变量
    if (data.variables && Array.isArray(data.variables)) {
      const variables = data.variables
        .filter((v: any) => v.key && v.value)
        .map((v: any) => ({
          key: v.key.trim(),
          value: v.value.trim()
        }))
      
      await apitestApi.saveFlowVariables(editingFlowId.value, variables)
      localVariables.value = variables.map((v: any) => ({ key: v.key, value: v.value }))
    }
    
    // 刷新流程列表，确保名称同步
    await loadFlows()
    
    // 清理导入数据和文件列表
    clearImportData()
    
    showImportDialog.value = false
    ElMessage.success('导入成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      // 如果是名称重复错误，弹出提示框
      const errorMsg = error.message || error.response?.data?.detail || '未知错误'
      if (errorMsg.includes('同名流程') || errorMsg.includes('已存在同名')) {
        await ElMessageBox.alert(errorMsg, '提示', {
          type: 'warning',
          confirmButtonText: '确定'
        })
      } else {
        ElMessage.error('导入失败: ' + errorMsg)
      }
    }
  }
}

// 从数据库导入
const doImportFlow = async (exportId: number, asNew: boolean = false) => {
  if (asNew) {
    // 导入为新流程
    try {
      if (!editingFlowId.value) {
        ElMessage.warning('请先选择一个流程以获取导出记录')
        return
      }
      const exportRecord = await apitestApi.getFlowExport(editingFlowId.value, exportId)
      const data = exportRecord.export_data
      
      // 重置表单
      flowForm.project_id = data.flow?.project_id
      flowForm.name = data.flow?.name || '导入的流程'
      flowForm.description = data.flow?.description || ''
      flowForm.environment_id = data.flow?.environment_id
      flowForm.global_variables_text = data.flow?.global_variables ? JSON.stringify(data.flow.global_variables, null, 2) : '{\n}'
      flowForm.steps = data.flow?.steps ? normalizeSteps(data.flow.steps) : []
      
      // 更新执行配置（如果有）
      if (data.executionConfig) {
        executionConfig.environment_id = data.executionConfig.environment_id
        executionConfig.failAction = data.executionConfig.failAction || 'stop'
        executionConfig.delay = data.executionConfig.delay || 1000
      }
      
      // 更新局部变量
      if (data.variables && Array.isArray(data.variables)) {
        localVariables.value = data.variables.map((v: any) => ({
          key: v.key || '',
          value: v.value || ''
        }))
      } else {
        localVariables.value = []
      }
      
      // 清空编辑ID，表示这是新流程
      editingFlowId.value = undefined
      
      // 清理导入数据和文件列表
      clearImportData()
      
      showImportDialog.value = false
      ElMessage.success('导入成功，请保存流程')
    } catch (error: any) {
      // 如果是名称重复错误，弹出提示框
      const errorMsg = error.message || error.response?.data?.detail || '未知错误'
      if (errorMsg.includes('同名流程') || errorMsg.includes('已存在同名')) {
        await ElMessageBox.alert(errorMsg, '提示', {
          type: 'warning',
          confirmButtonText: '确定'
        })
      } else {
        ElMessage.error('导入失败: ' + errorMsg)
      }
    }
  } else {
    // 导入到当前流程
    if (!editingFlowId.value) {
      ElMessage.warning({ message: '请先保存流程', duration: 1500 })
      return
    }
    
    try {
      // 先获取导出记录
      const exportRecord = await apitestApi.getFlowExport(editingFlowId.value, exportId)
      const data = exportRecord.export_data
      
      // 确认导入
      await ElMessageBox.confirm(
        '导入将覆盖当前流程的所有数据（接口、执行配置、局部变量），是否继续？',
        '确认导入',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 从数据库导入
      const importedFlow = await apitestApi.importApiFlow(editingFlowId.value, exportId)
      
      // 更新表单数据（保持当前流程名称不变，不更新为导入的名称）
      // flowForm.name 保持不变
      flowForm.description = importedFlow.description || ''
      flowForm.project_id = importedFlow.project_id
      flowForm.environment_id = importedFlow.environment_id
      flowForm.global_variables_text = importedFlow.global_variables ? JSON.stringify(importedFlow.global_variables, null, 2) : '{\n}'
      flowForm.steps = importedFlow.steps ? normalizeSteps(importedFlow.steps) : []
      
      // 重新加载局部变量
      await loadFlowVariables(editingFlowId.value)
      
      // 更新执行配置（从导入数据中获取，使用已经获取的 data）
      if (data?.executionConfig) {
        executionConfig.environment_id = data.executionConfig.environment_id
        executionConfig.failAction = data.executionConfig.failAction || 'stop'
        executionConfig.delay = data.executionConfig.delay || 1000
      } else {
        executionConfig.environment_id = importedFlow.environment_id
      }
      executionStats.total = flowForm.steps?.length || 0
      
      // 清理导入数据和文件列表
      clearImportData()
      
      showImportDialog.value = false
      ElMessage.success('导入成功')
    } catch (error: any) {
      if (error === 'cancel' || error === 'close') {
        return
      }
      // 如果是名称重复错误，弹出提示框
      const errorMsg = error.message || error.response?.data?.detail || '未知错误'
      if (errorMsg.includes('同名流程') || errorMsg.includes('已存在同名')) {
        await ElMessageBox.alert(errorMsg, '提示', {
          type: 'warning',
          confirmButtonText: '确定'
        })
      } else {
        ElMessage.error('导入失败: ' + errorMsg)
      }
    }
  }
}

// 删除导出记录
const doDeleteExport = async (exportId: number) => {
  if (!editingFlowId.value) {
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要删除该导出记录吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await apitestApi.deleteFlowExport(editingFlowId.value, exportId)
    
    // 重新加载导出记录列表
    flowExports.value = await apitestApi.getFlowExports(editingFlowId.value)
    
    ElMessage.success({ message: '删除成功', duration: 1000 })
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') {
      return
    }
    ElMessage.error({ message: '删除失败: ' + (error.message || '未知错误'), duration: 2000 })
  }
}

// 搜索接口
const searchEndpoints = () => {
  if (!flowForm.project_id) {
    ElMessage.warning({ message: '请先选择项目', duration: 1500 })
    return
  }
  if (!flowEndpointKeyword.value.trim()) {
    ElMessage.warning({ message: '请输入搜索关键词', duration: 1500 })
    return
  }
  // 如果还没有加载接口列表，先加载
  if (flowEndpoints.value.length === 0) {
    apitestApi
      .getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
      .then(data => {
        flowEndpoints.value = data
        endpoints.value = data
      })
      .catch(() => {
        flowEndpoints.value = []
        endpoints.value = []
      })
  }
}

// 显示生成变量对话框
const showGenerateDialog = (type: 'timestamp' | 'timepoint') => {
  if (type === 'timestamp') {
    // 时间戳使用 UTC 时间戳（标准做法）
    generatedValue.value = Date.now().toString()
    generateDialogTitle.value = '时间戳'
  } else {
    // 获取中国上海时区的时间点（UTC+8）
    const now = new Date()
    const formatter = new Intl.DateTimeFormat('zh-CN', {
      timeZone: 'Asia/Shanghai',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    })
    const parts = formatter.formatToParts(now)
    const year = parts.find(p => p.type === 'year')?.value
    const month = parts.find(p => p.type === 'month')?.value
    const day = parts.find(p => p.type === 'day')?.value
    const hour = parts.find(p => p.type === 'hour')?.value
    const minute = parts.find(p => p.type === 'minute')?.value
    const second = parts.find(p => p.type === 'second')?.value
    generatedValue.value = `${year}-${month}-${day} ${hour}:${minute}:${second}`
    generateDialogTitle.value = '时间点'
  }
  showGenerateVariableDialog.value = true
}

// 复制生成的值
const copyGeneratedValue = () => {
  navigator.clipboard.writeText(generatedValue.value).then(() => {
    ElMessage.success({ message: '已复制', duration: 1000 })
  }).catch(() => {
    ElMessage.error({ message: '复制失败', duration: 2000 })
  })
}

// 添加局部变量
const addLocalVariable = () => {
  localVariables.value.push({ key: '', value: '' })
}

// 在指定位置后添加局部变量
const addLocalVariableAfter = (index: number) => {
  localVariables.value.splice(index + 1, 0, { key: '', value: '' })
}

// 删除局部变量
const removeLocalVariable = async (index: number) => {
  const variable = localVariables.value[index]
  // 如果有ID，调用后端删除
  if (variable.id && editingFlowId.value) {
    try {
      await apitestApi.deleteFlowVariable(editingFlowId.value, variable.id)
      ElMessage.success({ message: '删除成功', duration: 1000 })
    } catch (error: any) {
      ElMessage.error({ message: error.message || '删除失败', duration: 2000 })
      return
    }
  }
  localVariables.value.splice(index, 1)
}

// 复制变量引用格式（如 STR($Tenant)）
// 复制变量引用（带格式选择）
const copyVariableWithFormat = async (key: string, format: string) => {
  if (!key || !key.trim()) {
    ElMessage.warning({ message: '变量名为空，无法复制', duration: 1500 })
    return
  }
  
  const varName = key.trim()
  const reference = `${format}($${varName})`
  await copyToClipboard(reference)
}

// 兼容旧的函数（用于执行配置中的复制按钮）
const copyVariableReference = async (key: string) => {
  if (!key || !key.trim()) {
    ElMessage.warning({ message: '变量名为空，无法复制', duration: 1500 })
    return
  }
  
  const varName = key.trim()
  
  try {
    // 弹出选择框
    await ElMessageBox.confirm(
      `请选择要复制的格式：`,
      `复制变量引用：${varName}`,
      {
        distinguishCancelAndClose: true,
        confirmButtonText: `STR($${varName})`,
        cancelButtonText: `NUM($${varName})`,
        type: 'info',
        center: true
      }
    )
    // 用户点击了确认按钮 - 复制 STR 格式
    await copyToClipboard(`STR($${varName})`)
  } catch (action) {
    // 用户点击了取消按钮 - 复制 NUM 格式
    if (action === 'cancel') {
      await copyToClipboard(`NUM($${varName})`)
    }
    // 如果是 'close'，则不做任何操作（用户关闭了对话框）
  }
}

// 复制到剪贴板的辅助函数
const copyToClipboard = async (text: string) => {
  // 尝试使用现代 Clipboard API
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success({ message: `已复制: ${text}`, duration: 1500 })
      return
    } catch (err) {
      console.warn('Clipboard API 失败，尝试备用方案', err)
    }
  }
  
  // 备用方案：使用 execCommand
  try {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-9999px'
    textArea.style.top = '-9999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    const success = document.execCommand('copy')
    document.body.removeChild(textArea)
    if (success) {
      ElMessage.success({ message: `已复制: ${text}`, duration: 1500 })
    } else {
      ElMessage.error({ message: '复制失败', duration: 2000 })
    }
  } catch (err) {
    console.error('复制失败:', err)
    ElMessage.error({ message: '复制失败', duration: 2000 })
  }
}

// 序列化对象，保持模板语法的原始格式（带引号或不带引号）
const stringifyWithTemplates = (obj: any, indent: number = 2): string => {
  const indentStr = ' '.repeat(indent)
  
  // 判断是否是模板语法
  const isTemplate = (val: any): boolean => {
    if (typeof val !== 'string') return false
    // 去除可能的引号
    const trimmed = val.replace(/^["']|["']$/g, '')
    return trimmed.startsWith('$') || (trimmed.startsWith('{{') && trimmed.endsWith('}}')) || 
           trimmed.startsWith('NUM(') || trimmed.startsWith('STR(')
  }
  
  // 获取模板语法的值（去除引号）
  const getTemplateValue = (val: string): string => {
    return val.replace(/^["']|["']$/g, '')
  }
  
  const stringifyValue = (val: any, level: number): string => {
    if (val === null) return 'null'
    if (val === undefined) return 'undefined'
    
    // 如果是模板语法字符串，保持原样（不带引号）
    if (isTemplate(val)) {
      return getTemplateValue(val)
    }
    
    // 普通字符串，加引号
    if (typeof val === 'string') {
      return JSON.stringify(val)
    }
    
    // 数字、布尔值，不加引号
    if (typeof val === 'number' || typeof val === 'boolean') {
      return String(val)
    }
    
    // 数组
    if (Array.isArray(val)) {
      if (val.length === 0) return '[]'
      const items = val.map(item => indentStr.repeat(level + 1) + stringifyValue(item, level + 1))
      return '[\n' + items.join(',\n') + '\n' + indentStr.repeat(level) + ']'
    }
    
    // 对象
    if (typeof val === 'object') {
      const keys = Object.keys(val)
      if (keys.length === 0) return '{}'
      const items = keys.map(key => {
        const value = stringifyValue(val[key], level + 1)
        return indentStr.repeat(level + 1) + JSON.stringify(key) + ': ' + value
      })
      return '{\n' + items.join(',\n') + '\n' + indentStr.repeat(level) + '}'
    }
    
    return JSON.stringify(val)
  }
  
  return stringifyValue(obj, 0)
}

// 编辑执行链接口
const handleEditStep = async (index: number) => {
  if (index < 0 || index >= flowForm.steps.length) return
  
  const step = flowForm.steps[index]
  if (!step.endpoint_id) return
  
  // 调试：记录打开步骤编辑前的所有步骤数据
  console.log(`[handleEditStep] 打开步骤 ${index} 编辑前，flowForm.steps 的状态:`, JSON.parse(JSON.stringify(flowForm.steps.map((s, i) => ({
    index: i,
    endpoint_id: s.endpoint_id,
    alias: s.alias,
    headers: s.headers,
    headersType: typeof s.headers,
    headersKeys: s.headers ? Object.keys(s.headers) : []
  })))))
  
  editingStepIndex.value = index
  activeParamTab.value = 'headers'
  stepExecutionResult.value = null
  
  // 加载接口详情
  try {
    // 获取接口详情
    const endpoint = flowEndpoints.value.find(ep => ep.id === step.endpoint_id)
    if (endpoint) {
      editingEndpoint.value = endpoint
    } else {
      editingEndpoint.value = await apitestApi.getApiEndpoint(step.endpoint_id)
      // 如果不在列表中，添加到列表以便后续使用
      flowEndpoints.value.push(editingEndpoint.value)
    }
    
    // 加载测试数据
    await loadStepTestData(step.endpoint_id)
    
    // 从 step 中恢复参数，如果 step 中有定义（包括空对象）就使用，否则从测试数据中加载
    // 使用 !== undefined && !== null 来判断是否保存过，而不是检查对象是否为空
    // 注意：步骤的参数优先级高于测试数据，一旦步骤保存过参数，就使用步骤的参数
    // 重要：流程测试的参数与接口测试的参数完全独立，不会自动同步
    if (step.path_params !== undefined && step.path_params !== null) {
      // 步骤已保存过参数（包括空对象 {}），使用步骤的参数
      stepPathParamsText.value = stringifyWithTemplates(step.path_params, 2)
    } else {
      // 步骤未保存过参数，从测试数据中加载（仅用于首次编辑时的初始值）
      prefillStepFromTestData('path_params')
    }
    
    if (step.query_params !== undefined && step.query_params !== null) {
      stepQueryParamsText.value = stringifyWithTemplates(step.query_params, 2)
    } else {
      prefillStepFromTestData('query_params')
    }
    
    if (step.headers !== undefined && step.headers !== null) {
      // 步骤已保存过headers（包括空对象 {}），使用步骤的headers
      stepHeadersText.value = stringifyWithTemplates(step.headers, 2)
    } else {
      // 步骤未保存过headers，从测试数据中加载（仅用于首次编辑时的初始值）
      prefillStepFromTestData('headers')
    }
    
    if (step.body !== undefined && step.body !== null) {
      stepBodyText.value = stringifyWithTemplates(step.body, 2)
    } else {
      prefillStepFromTestData('body')
    }
    
    // 恢复断言
    if (step.assertions && Array.isArray(step.assertions) && step.assertions.length > 0) {
      stepAssertions.value = step.assertions.map((a: any) => ({
        type: a.type || 'status_code',
        operator: a.operator || 'eq',
        target: a.target || undefined,
        expected: a.expected !== undefined && a.expected !== null ? String(a.expected) : undefined
      }))
    } else {
      // 如果没有断言，从测试数据中加载
      const defaultData = stepTestDataList.value[0]
      if (defaultData && defaultData.assertions && Array.isArray(defaultData.assertions) && defaultData.assertions.length > 0) {
        stepAssertions.value = defaultData.assertions.map((a: any) => ({
          type: a.type || 'status_code',
          operator: a.operator || 'eq',
          target: a.target || undefined,
          expected: a.expected !== undefined && a.expected !== null ? String(a.expected) : undefined
        }))
      } else {
        // 使用期望状态码创建默认断言
        const expectedStatus = defaultData?.expected_status || 200
        stepAssertions.value = [{ type: 'status_code', operator: 'eq', expected: String(expectedStatus) }]
      }
    }
    
    stepEditDrawerVisible.value = true
  } catch (error: any) {
    ElMessage.error({ message: error.message || '加载接口详情失败', duration: 2000 })
  }
}


// 切换到下一个步骤
// 截断变量值显示
const truncateVariableValue = (value: string, maxLength: number = 30): string => {
  if (!value) return ''
  if (value.length <= maxLength) return value
  return value.substring(0, maxLength) + '...'
}

const handleNextStep = async () => {
  // 先保存当前步骤
  // 重要：必须等待保存完成并同步服务器返回的数据，才能切换到下一步
  // 否则会导致前一个步骤的修改被覆盖
  try {
    await handleStepSave()
  } catch (error: any) {
    // 保存失败时提示用户，但不阻止切换
    console.error('保存步骤失败:', error)
  }
  
  // 切换到下一个步骤
  const nextIndex = editingStepIndex.value + 1
  if (nextIndex < flowForm.steps.length) {
    await handleEditStep(nextIndex)
  } else {
    // 如果是最后一个步骤，关闭抽屉
    stepEditDrawerVisible.value = false
  }
}

// 加载步骤测试数据
const loadStepTestData = async (endpointId: number) => {
  try {
    stepTestDataList.value = await apitestApi.getApiTestDataList(endpointId)
    if (stepTestDataList.value.length === 0) {
      // 如果没有测试数据，创建一个默认的
      const created = await apitestApi.createApiTestData({
        endpoint_id: endpointId,
        name: '测试数据#默认',
        expected_status: 200,
        path_params: {},
        query_params: {},
        headers: {},
        body: {}
      })
      stepTestDataList.value = [created]
    }
  } catch (error: any) {
    ElMessage.error({ message: error.message || '加载测试数据失败', duration: 2000 })
  }
}

// 从测试数据填充步骤参数
const prefillStepFromTestData = (type: 'path_params' | 'query_params' | 'headers' | 'body') => {
  try {
    const defaultData = stepTestDataList.value[0]
    if (!defaultData) {
      const empty = '{\n\n}'
      if (type === 'path_params') stepPathParamsText.value = empty
      else if (type === 'query_params') stepQueryParamsText.value = empty
      else if (type === 'headers') stepHeadersText.value = empty
      else if (type === 'body') stepBodyText.value = empty
      return
    }
    
    let data: any = {}
    if (type === 'path_params') data = defaultData.path_params || {}
    else if (type === 'query_params') data = defaultData.query_params || {}
    else if (type === 'headers') data = defaultData.headers || {}
    else if (type === 'body') data = defaultData.body || {}
    
    const text = (data && typeof data === 'object' && Object.keys(data).length > 0) 
      ? JSON.stringify(data, null, 2) 
      : '{\n\n}'
    
    if (type === 'path_params') stepPathParamsText.value = text
    else if (type === 'query_params') stepQueryParamsText.value = text
    else if (type === 'headers') stepHeadersText.value = text
    else if (type === 'body') stepBodyText.value = text
  } catch (error: any) {
    console.error('填充测试数据错误:', error)
    const empty = '{\n\n}'
    if (type === 'path_params') stepPathParamsText.value = empty
    else if (type === 'query_params') stepQueryParamsText.value = empty
    else if (type === 'headers') stepHeadersText.value = empty
    else if (type === 'body') stepBodyText.value = empty
  }
}

// 执行步骤接口
const handleStepExecuteSubmit = async () => {
  if (!editingStep.value || !editingStep.value.endpoint_id) {
    ElMessage.warning({ message: '接口信息不完整', duration: 1500 })
    return
  }
  
  if (!executionConfig.environment_id) {
    ElMessage.warning({ message: '请先选择执行环境', duration: 1500 })
    return
  }
  
  // 解析JSON参数
  let pathParams: Record<string, any> = {}
  let queryParams: Record<string, any> = {}
  let headers: Record<string, any> = {}
  let body: Record<string, any> | any = {}
  
  try {
    // 在执行接口时，也使用相同的解析逻辑
    const parseJsonWithTemplatesForExecute = (jsonText: string): any => {
      try {
        return JSON.parse(jsonText)
      } catch {
        // 如果包含模板语法，将模板语法替换为字符串占位符后再解析
        try {
          let placeholderJson = jsonText
          
          // 先找出所有 NUM() 和 STR() 的范围，以便在处理 $API 时跳过它们
          const numStrRanges: Array<[number, number]> = []
          let i = 0
          const len = placeholderJson.length
          
          while (i < len) {
            if ((i + 4 <= len && placeholderJson.substring(i, i + 4) === 'NUM(') ||
                (i + 4 <= len && placeholderJson.substring(i, i + 4) === 'STR(')) {
              let depth = 1
              let j = i + 4
              let found = false
              
              while (j < len) {
                if (placeholderJson[j] === '(') depth++
                else if (placeholderJson[j] === ')') {
                  depth--
                  if (depth === 0) {
                    numStrRanges.push([i, j + 1])
                    i = j + 1
                    found = true
                    break
                  }
                }
                j++
              }
              
              if (!found) {
                i++
              }
            } else {
              i++
            }
          }
          
          // 检查位置是否在 NUM/STR 范围内
          const isInNumStr = (pos: number): boolean => {
            return numStrRanges.some(([start, end]) => pos >= start && pos < end)
          }
          
          // 先处理 $API[N].path 和 $var（但跳过 NUM/STR 内部）
          const result: string[] = []
          i = 0
          
          while (i < len) {
            if (!isInNumStr(i)) {
              // 检查 $API[N].path
              if (i + 5 <= len && placeholderJson.substring(i, i + 5) === '$API[') {
                let j = i + 5
                while (j < len && !isInNumStr(j)) {
                  if (placeholderJson[j] === ']' && j + 1 < len && placeholderJson[j + 1] === '.') {
                    j += 2
                    while (j < len && !isInNumStr(j) && /[a-zA-Z0-9_.]/.test(placeholderJson[j])) {
                      j++
                    }
                    const match = placeholderJson.substring(i, j)
                    const apiMatch = match.match(/\$API\[(\d+)\]\.([a-zA-Z0-9_.]+)/)
                    if (apiMatch) {
                      result.push(`"__TEMPLATE__API[${apiMatch[1]}].${apiMatch[2]}__TEMPLATE__"`)
                      i = j
                      break
                    }
                  }
                  j++
                }
                if (i < len) {
                  result.push(placeholderJson[i])
                  i++
                }
              }
              // 检查 $var
              else if (placeholderJson[i] === '$' && i + 1 < len && /[a-zA-Z_]/.test(placeholderJson[i + 1])) {
                let j = i + 1
                while (j < len && !isInNumStr(j) && /[a-zA-Z0-9_]/.test(placeholderJson[j])) {
                  j++
                }
                const varName = placeholderJson.substring(i + 1, j)
                result.push(`"__TEMPLATE__${varName}__TEMPLATE__"`)
                i = j
              } else {
                result.push(placeholderJson[i])
                i++
              }
            } else {
              result.push(placeholderJson[i])
              i++
            }
          }
          
          placeholderJson = result.join('')
          
          // 兼容旧的 {{ ... }} 语法（不在 NUM/STR 内部）
          placeholderJson = placeholderJson.replace(/\{\{\s*([^}]+)\s*\}\}/g, (match, expr) => {
            return `"__TEMPLATE__${expr.trim().replace(/"/g, '\\"')}__TEMPLATE__"`
          })
          
          // 然后处理 NUM() 和 STR() 格式（将它们转换为字符串）
          const convertNumStrToPlaceholder = (str: string, prefix: string): string => {
            const result: string[] = []
            let i = 0
            const len = str.length
            
            while (i < len) {
              if (i + prefix.length + 1 <= len && str.substring(i, i + prefix.length + 1) === `${prefix}(`) {
                let depth = 1  // 从1开始，因为已经遇到了开括号
                let j = i + prefix.length + 1  // 从开括号后面开始
                let found = false
                
                while (j < len) {
                  if (str[j] === '(') depth++
                  else if (str[j] === ')') {
                    depth--
                    if (depth === 0) {
                      const fullMatch = str.substring(i, j + 1)
                      result.push(JSON.stringify(fullMatch)) // 转换为字符串占位符
                      i = j + 1
                      found = true
                      break
                    }
                  }
                  j++
                }
                
                if (!found) {
                  result.push(str[i])
                  i++
                }
              } else {
                result.push(str[i])
                i++
              }
            }
            
            return result.join('')
          }
          
          placeholderJson = convertNumStrToPlaceholder(placeholderJson, 'NUM')
          placeholderJson = convertNumStrToPlaceholder(placeholderJson, 'STR')
          const parsed = JSON.parse(placeholderJson)
          // 将占位符恢复为模板语法
          const restoreTemplates = (obj: any): any => {
            if (typeof obj === 'string') {
              // 检查是否是 NUM() 或 STR() 格式（已经是解析后的字符串，不包含引号）
              if (obj.startsWith('NUM(') || obj.startsWith('STR(')) {
                return obj
              }
              // 检查是否是 __TEMPLATE__ 占位符
              if (obj.startsWith('__TEMPLATE__') && obj.endsWith('__TEMPLATE__')) {
                const expr = obj.slice(13, -13).replace(/\\"/g, '"')
                // 判断是 API[N].path 格式还是变量名格式
                if (expr.startsWith('API[')) {
                  return `$${expr}`
                } else {
                  return `$${expr}`
                }
              }
            }
            if (Array.isArray(obj)) {
              return obj.map(restoreTemplates)
            }
            if (obj && typeof obj === 'object') {
              const result: any = {}
              for (const key in obj) {
                result[key] = restoreTemplates(obj[key])
              }
              return result
            }
            return obj
          }
          return restoreTemplates(parsed)
        } catch (e: any) {
          throw new Error(`JSON格式错误: ${e.message}`)
        }
      }
    }
    
    // 解析Path参数（使用支持模板语法的解析函数）
    if (stepPathParamsText.value.trim()) {
      try {
        pathParams = parseJsonWithTemplatesForExecute(stepPathParamsText.value.trim())
        if (!(pathParams && typeof pathParams === 'object' && !Array.isArray(pathParams))) {
          pathParams = {}
        }
      } catch (e: any) {
        ElMessage.error({ message: 'Path参数JSON格式错误: ' + (e.message || '请检查输入'), duration: 2000 })
        return
      }
    }
    
    if (stepQueryParamsText.value.trim()) {
      try {
        queryParams = parseJsonWithTemplatesForExecute(stepQueryParamsText.value.trim())
        if (!(queryParams && typeof queryParams === 'object' && !Array.isArray(queryParams))) {
          queryParams = {}
        }
      } catch (e: any) {
        ElMessage.error({ message: 'Query参数JSON格式错误: ' + (e.message || '请检查输入'), duration: 2000 })
        return
      }
    }
    
    if (stepHeadersText.value.trim()) {
      try {
        headers = parseJsonWithTemplatesForExecute(stepHeadersText.value.trim())
        if (!(headers && typeof headers === 'object' && !Array.isArray(headers))) {
          headers = {}
        }
      } catch (e: any) {
        ElMessage.error({ message: 'Header参数JSON格式错误: ' + (e.message || '请检查输入'), duration: 2000 })
        return
      }
    }
    
    if (stepBodyText.value.trim()) {
      try {
        body = parseJsonWithTemplatesForExecute(stepBodyText.value.trim())
      } catch (e: any) {
        ElMessage.error({ message: 'Body参数JSON格式错误: ' + (e.message || '请检查输入'), duration: 2000 })
        return
      }
    }
  } catch (error: any) {
    ElMessage.error({ message: '参数解析失败: ' + (error.message || '未知错误'), duration: 2000 })
    return
  }
  
  stepExecuting.value = true
  try {
    // 准备断言数据
    const assertions = stepAssertions.value.map(a => ({
      type: a.type,
      operator: a.operator,
      target: a.target,
      expected: a.expected
    }))
    
    // 构建全局变量对象（从局部变量中获取）
    const globalVariables: Record<string, any> = {}
    localVariables.value.forEach(v => {
      if (v.key && v.value !== undefined && v.value !== null) {
        globalVariables[v.key] = v.value
      }
    })
    console.log('🔍 前端 - 局部变量列表:', localVariables.value)
    console.log('🔍 前端 - 构建的全局变量:', globalVariables)
    console.log('🔍 前端 - 请求的 headers:', headers)
    
    const result = await apitestApi.executeApiEndpoint(editingStep.value.endpoint_id, {
      environment_id: executionConfig.environment_id,
      path_params: pathParams,
      query_params: queryParams,
      headers: headers,
      body: body,
      assertions: assertions,
      global_variables: Object.keys(globalVariables).length > 0 ? globalVariables : undefined
    })
    
    stepExecutionResult.value = result
    ElMessage.success({ message: '执行成功', duration: 1000 })
  } catch (error: any) {
    ElMessage.error({ message: error.message || '执行失败', duration: 2000 })
  } finally {
    stepExecuting.value = false
  }
}

// 保存步骤参数
const handleStepSave = async () => {
  if (editingStepIndex.value < 0 || !editingStep.value) {
    ElMessage.warning({ message: '请先选择要编辑的接口', duration: 1500 })
    return
  }
  
  try {
    // 调试：输出保存前的所有步骤数据
    console.log('=== 开始保存步骤 ===')
    console.log('当前编辑的步骤索引:', editingStepIndex.value)
    console.log('保存前的所有步骤:', JSON.parse(JSON.stringify(flowForm.steps)))
    
    // 解析并保存参数（保留原有值，只在有输入时才更新）
    const currentStep = flowForm.steps[editingStepIndex.value]
    console.log('当前步骤的原始数据:', JSON.parse(JSON.stringify(currentStep)))
    // 注意：初始值应该从 currentStep 获取，但如果用户修改了文本，应该使用文本中的值
    let pathParams: Record<string, any> | undefined = currentStep.path_params
    let queryParams: Record<string, any> | undefined = currentStep.query_params
    let headers: Record<string, any> | undefined = currentStep.headers
    let body: Record<string, any> | any | undefined = currentStep.body
    
    // 辅助函数：处理包含模板语法的 JSON
    // 解析包含模板语法的 JSON
    // 支持 $var, $API[N].path, {{ var }}, NUM(), STR() 语法
    // 带引号的表示字符串类型，不带引号的表示数字/布尔/null 类型
    const parseJsonWithTemplates = (jsonText: string): any => {
      // 先尝试直接解析（不包含模板语法的情况）
      try {
        return JSON.parse(jsonText)
      } catch {
        // 如果包含模板语法，使用占位符替换
        try {
          const placeholders: Map<string, string> = new Map()
          let index = 0
          let result = jsonText
          
          // 生成唯一占位符
          const getPlaceholder = () => `__TPL${index++}__`
          
          // 按顺序替换，避免冲突
          // 0. 先处理 NUM() 和 STR() 格式（优先级最高）
          // 使用栈来匹配括号，处理嵌套情况
          const numStrMarkers = new Set<string>() // 记录哪些占位符是 NUM() 或 STR() 格式
          const convertNumStrToPlaceholder = (str: string, prefix: string): string => {
            const result: string[] = []
            let i = 0
            const len = str.length
            
            while (i < len) {
              // 检查是否是 NUM( 或 STR( 开头
              if (i + prefix.length + 1 <= len && str.substring(i, i + prefix.length + 1) === `${prefix}(`) {
                // 找到匹配的右括号
                let depth = 0
                let j = i + prefix.length
                let found = false
                
                while (j < len) {
                  if (str[j] === '(') depth++
                  else if (str[j] === ')') {
                    depth--
                    if (depth === 0) {
                      // 找到匹配的右括号
                      const fullMatch = str.substring(i, j + 1)
                      const ph = getPlaceholder()
                      placeholders.set(ph, fullMatch)
                      numStrMarkers.add(ph) // 标记这是 NUM() 或 STR() 格式
                      // NUM() 和 STR() 格式作为值（不带引号），使用特殊对象作为占位符
                      // 使用 {"__TPL_MARKER__": "ph"} 格式，这样 JSON 可以解析
                      result.push(`{"__TPL_MARKER__":"${ph}"}`)
                      i = j + 1
                      found = true
                      break
                    }
                  }
                  j++
                }
                
                if (!found) {
                  // 没有找到匹配的右括号，保持原样
                  result.push(str[i])
                  i++
                }
              } else {
                result.push(str[i])
                i++
              }
            }
            
            return result.join('')
          }
          
          // 先处理 NUM()，再处理 STR()
          result = convertNumStrToPlaceholder(result, 'NUM')
          result = convertNumStrToPlaceholder(result, 'STR')
          
          // 1. 替换 $API[N].path（最复杂，优先处理）
          result = result.replace(/\$API\[\d+\]\.[a-zA-Z0-9_.]+/g, (match) => {
            const ph = getPlaceholder()
            placeholders.set(ph, match)
            // 检查是否在引号内
            const pos = result.indexOf(match)
            const before = pos > 0 ? result[pos - 1] : ''
            const after = pos + match.length < result.length ? result[pos + match.length] : ''
            if (before === '"' && after === '"') {
              return ph // 在引号内，保持为字符串
            }
            return `"${ph}"` // 不在引号内，添加引号使其成为有效的 JSON 字符串
          })
          
          // 2. 替换不在引号内的 $变量名（需要加引号使其成为有效的 JSON）
          result = result.replace(/([{:,]\s*)(\$[a-zA-Z_][a-zA-Z0-9_]*)(\s*[,}])/g, (match, p1, varExpr, p3) => {
            const ph = getPlaceholder()
            placeholders.set(ph, varExpr)
            return p1 + `"${ph}"` + p3
          })
          
          // 3. 替换在引号内的 $变量名
          result = result.replace(/"(\$[a-zA-Z_][a-zA-Z0-9_]*)"/g, (match, varExpr) => {
            const ph = getPlaceholder()
            placeholders.set(ph, varExpr)
            return `"${ph}"`
          })
          
          // 4. 兼容旧的 {{ ... }} 语法
          result = result.replace(/\{\{[^}]+\}\}/g, (match) => {
            const ph = getPlaceholder()
            placeholders.set(ph, match)
            return `"${ph}"`
          })
          
          // 解析 JSON
          const parsed = JSON.parse(result)
          
          // 恢复占位符为原始模板语法
          const restore = (obj: any): any => {
            // 检查是否是 NUM() 或 STR() 格式的特殊标记对象
            if (obj && typeof obj === 'object' && !Array.isArray(obj) && obj.__TPL_MARKER__) {
              const ph = obj.__TPL_MARKER__
              const original = placeholders.get(ph)
              if (original && numStrMarkers.has(ph)) {
                // NUM() 或 STR() 格式，返回不带引号的原始格式
                return original
              }
              return original || ph
            }
            if (typeof obj === 'string' && obj.startsWith('__TPL') && obj.endsWith('__')) {
              const original = placeholders.get(obj)
              return original || obj
            }
            if (Array.isArray(obj)) {
              return obj.map(restore)
            }
            if (obj && typeof obj === 'object') {
              const res: any = {}
              for (const k in obj) {
                res[k] = restore(obj[k])
              }
              return res
            }
            return obj
          }
          
          return restore(parsed)
        } catch (e: any) {
          throw new Error(`JSON格式错误: ${e.message}`)
        }
      }
    }
    
    // 验证 JSON 格式（允许模板语法）
    const validateJsonWithTemplates = (jsonText: string): boolean => {
      try {
        parseJsonWithTemplates(jsonText)
        return true
      } catch {
        return false
      }
    }
    
    // 解析参数：只要有输入就解析并保存，即使为空对象也要保存（表示用户明确设置了空值）
    // 这样下次编辑时，会使用步骤自己的参数，而不是从测试数据同步
    // 注意：即使文本为空，也要保存为空对象 {}，这样下次编辑时会使用步骤的参数而不是测试数据
    if (stepPathParamsText.value.trim()) {
      try {
        const parsed = parseJsonWithTemplates(stepPathParamsText.value.trim())
        pathParams = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : {}
      } catch (e: any) {
        ElMessage.error({ message: 'Path参数JSON格式错误，无法保存', duration: 2000 })
        return
      }
    } else {
      // 如果文本为空，设置为空对象，表示用户明确清空了参数
      pathParams = {}
    }
    
    if (stepQueryParamsText.value.trim()) {
      if (!validateJsonWithTemplates(stepQueryParamsText.value.trim())) {
        ElMessage.error({ message: 'Query参数JSON格式错误，无法保存', duration: 2000 })
        return
      }
      try {
        queryParams = parseJsonWithTemplates(stepQueryParamsText.value.trim())
        if (!(queryParams && typeof queryParams === 'object' && !Array.isArray(queryParams))) {
          queryParams = {}
        }
      } catch (e: any) {
        ElMessage.error({ message: 'Query参数JSON格式错误，无法保存: ' + (e.message || '请检查输入'), duration: 2000 })
        return
      }
    } else {
      // 如果文本为空，设置为空对象，表示用户明确清空了参数
      queryParams = {}
    }
    
    // 处理Header：如果有输入则解析，如果为空字符串则设置为空对象
    if (stepHeadersText.value.trim()) {
      if (!validateJsonWithTemplates(stepHeadersText.value.trim())) {
        ElMessage.error({ message: 'Header参数JSON格式错误，无法保存', duration: 2000 })
        return
      }
      try {
        const parsedHeaders = parseJsonWithTemplates(stepHeadersText.value.trim())
        // 确保解析结果是对象
        if (parsedHeaders && typeof parsedHeaders === 'object' && !Array.isArray(parsedHeaders)) {
          headers = parsedHeaders
          // 调试：输出解析后的headers
          console.log('解析后的headers:', headers, '类型:', typeof headers, '键:', Object.keys(headers))
        } else {
          headers = {}
        }
      } catch (e: any) {
        console.error('Header解析错误:', e, '输入:', stepHeadersText.value.trim())
        ElMessage.error({ message: 'Header参数JSON格式错误，无法保存: ' + (e.message || ''), duration: 2000 })
        return
      }
    } else {
      // 如果文本为空，设置为空对象，表示用户明确清空了参数
      headers = {}
    }
    
    if (stepBodyText.value.trim()) {
      if (!validateJsonWithTemplates(stepBodyText.value.trim())) {
        ElMessage.error({ message: 'Body参数JSON格式错误，无法保存', duration: 2000 })
        return
      }
      try {
        body = parseJsonWithTemplates(stepBodyText.value.trim())
      } catch (e: any) {
        ElMessage.error({ message: 'Body参数JSON格式错误，无法保存', duration: 2000 })
        return
      }
    } else {
      // 如果文本为空，设置为空对象，表示用户明确清空了参数
      body = {}
    }
    
    // 保存到 step（创建新对象以确保响应式更新）
    const stepIndex = editingStepIndex.value
    const updatedStep: FlowStep = {
      endpoint_id: flowForm.steps[stepIndex].endpoint_id,
      environment_id: flowForm.steps[stepIndex].environment_id,
      test_data_id: flowForm.steps[stepIndex].test_data_id,
      alias: flowForm.steps[stepIndex].alias,
      path_params: pathParams,
      query_params: queryParams,
      headers: headers,
      body: body,
      // 保存断言（始终保存，即使为空数组）
      assertions: stepAssertions.value.map(a => ({
        type: a.type,
        operator: a.operator,
        target: a.target,
        expected: a.expected
      })),
    }
    
    // 调试：输出保存的参数
    console.log('保存步骤参数:', {
      stepIndex,
      pathParams,
      queryParams,
      headers,
      body,
      headersType: typeof headers,
      headersKeys: headers ? Object.keys(headers) : []
    })
    
    // 更新 flowForm.steps 数组（使用 Vue 3 的响应式方式）
    // 使用 Vue.set 或直接赋值确保响应式更新
    flowForm.steps[stepIndex] = updatedStep
    
    // 调试：确认更新后的数据（包括所有步骤，确保没有意外修改其他步骤）
    console.log(`[handleStepSave] 更新步骤 ${stepIndex} 后，flowForm.steps 的完整状态:`, JSON.parse(JSON.stringify(flowForm.steps.map((s, i) => ({
      index: i,
      endpoint_id: s.endpoint_id,
      alias: s.alias,
      headers: s.headers,
      headersType: typeof s.headers,
      headersKeys: s.headers ? Object.keys(s.headers) : [],
      headersUndefined: s.headers === undefined,
      headersNull: s.headers === null
    })))))
    
    // 如果流程已存在，自动保存到后端
    if (editingFlowId.value) {
      try {
        // 使用局部变量构建全局变量对象
        const vars: Record<string, string> = {}
        localVariables.value.forEach(v => {
          if (v.key.trim() && v.value.trim()) {
            vars[v.key] = v.value
          }
        })
        const globalVars = Object.keys(vars).length > 0 ? vars : undefined
        
        // 同步执行配置到流程表单
        if (executionConfig.environment_id) {
          flowForm.environment_id = executionConfig.environment_id
        }
        
        // 确保 steps 中只包含正确的字段，不包含调试字段
        // 注意：如果 headers/path_params/query_params/body 是空对象 {}，表示用户明确清空了参数
        // 如果它们是 undefined 或 null，表示从未设置过，应该保持为 undefined
        // 重要：保存时，必须包含所有步骤的完整数据，不能丢失任何步骤的参数
        console.log(`[handleStepSave] 保存步骤 ${stepIndex} 前，flowForm.steps 的完整状态:`, JSON.parse(JSON.stringify(flowForm.steps.map((s, i) => ({
          index: i,
          endpoint_id: s.endpoint_id,
          alias: s.alias,
          path_params: s.path_params,
          query_params: s.query_params,
          headers: s.headers,
          body: s.body,
          headersType: typeof s.headers,
          headersKeys: s.headers ? Object.keys(s.headers) : [],
          headersUndefined: s.headers === undefined,
          headersNull: s.headers === null
        })))))
        const cleanSteps = flowForm.steps.map((step, index) => {
          // 确保每个步骤都有完整的字段
          const cleanStep: any = {
            endpoint_id: step.endpoint_id,
            environment_id: step.environment_id,
            test_data_id: step.test_data_id,
            alias: step.alias,
            assertions: step.assertions || [],
          }
          
          // 只有当参数不是 undefined 时才设置（包括空对象 {}）
          // 注意：空对象 {} 表示用户明确设置了空值，必须保存
          if (step.path_params !== undefined) {
            cleanStep.path_params = step.path_params
          }
          if (step.query_params !== undefined) {
            cleanStep.query_params = step.query_params
          }
          if (step.headers !== undefined) {
            cleanStep.headers = step.headers
          }
          if (step.body !== undefined) {
            cleanStep.body = step.body
          }
          
          console.log(`步骤 ${index} (endpoint_id=${step.endpoint_id}, alias=${step.alias}) 清理后的数据:`, JSON.parse(JSON.stringify(cleanStep)))
          return cleanStep
        })
        console.log('清理后的所有步骤:', JSON.parse(JSON.stringify(cleanSteps)))
        
        const payload: Partial<ApiTestFlow> = {
          project_id: flowForm.project_id,
          name: flowForm.name,
          description: flowForm.description,
          environment_id: flowForm.environment_id,
          global_variables: globalVars,
          steps: cleanSteps
        }
        
        // 调试：输出发送到服务器的数据
        console.log('发送到服务器的payload:', JSON.parse(JSON.stringify(payload)))
        
        console.log('开始保存到服务器，flowId:', editingFlowId.value, 'stepIndex:', stepIndex)
        const updatedFlow = await apitestApi.updateApiFlow(editingFlowId.value, payload)
        console.log('服务器返回的数据:', JSON.parse(JSON.stringify(updatedFlow)))
        
        // 更新本地数据，确保与服务器同步（使用服务器返回的数据）
        // 重要：必须使用服务器返回的完整 steps 数组，确保所有步骤的数据都正确
        if (updatedFlow && updatedFlow.steps && updatedFlow.steps.length === flowForm.steps.length) {
          // 使用服务器返回的完整 steps 数组，确保所有步骤的数据都正确
          // 这样可以避免只更新当前步骤而丢失其他步骤的数据
          flowForm.steps = updatedFlow.steps.map((serverStep: any) => normalizeStep({
            endpoint_id: serverStep.endpoint_id,
            environment_id: serverStep.environment_id,
            test_data_id: serverStep.test_data_id,
            alias: serverStep.alias,
            enabled: serverStep.enabled,
            path_params: serverStep.path_params,
            query_params: serverStep.query_params,
            headers: serverStep.headers,
            body: serverStep.body,
            assertions: serverStep.assertions || [],
          }))
          console.log('更新后的所有步骤数据:', JSON.parse(JSON.stringify(flowForm.steps)))
          
          // 同时更新流程列表中的数据，确保下次打开时数据正确
          const flowInList = flows.value.find(f => f.id === editingFlowId.value)
          if (flowInList) {
            flowInList.steps = JSON.parse(JSON.stringify(flowForm.steps))
            console.log('已更新流程列表中的所有步骤数据')
          }
        } else {
          console.error('服务器返回的数据不完整:', { 
            updatedFlow, 
            stepIndex, 
            stepsLength: updatedFlow?.steps?.length,
            expectedLength: flowForm.steps.length
          })
          // 即使数据不完整，也尝试更新当前步骤
          if (updatedFlow && updatedFlow.steps && updatedFlow.steps.length > stepIndex) {
            const serverStep = updatedFlow.steps[stepIndex]
            flowForm.steps[stepIndex] = {
              endpoint_id: serverStep.endpoint_id,
              environment_id: serverStep.environment_id,
              test_data_id: serverStep.test_data_id,
              alias: serverStep.alias,
              path_params: serverStep.path_params,
              query_params: serverStep.query_params,
              headers: serverStep.headers,
              body: serverStep.body,
              assertions: serverStep.assertions || [],
            }
          }
          ElMessage.warning({ message: '保存成功，但服务器返回的数据不完整，请刷新页面确认', duration: 2000 })
        }
        ElMessage.success({ message: '保存成功', duration: 1000 })
        
        // 保存成功后，重新格式化显示（2空格缩进）
        if (pathParams !== undefined) {
          stepPathParamsText.value = stringifyWithTemplates(pathParams, 2)
        }
        if (queryParams !== undefined) {
          stepQueryParamsText.value = stringifyWithTemplates(queryParams, 2)
        }
        if (headers !== undefined) {
          stepHeadersText.value = stringifyWithTemplates(headers, 2)
        }
        if (body !== undefined) {
          stepBodyText.value = stringifyWithTemplates(body, 2)
        }
      } catch (saveError: any) {
        console.error('保存到服务器失败:', saveError)
        ElMessage.error({ message: '保存到服务器失败: ' + (saveError.message || '未知错误'), duration: 2000 })
        // 保存失败时，不抛出错误，让用户知道保存失败但本地数据已更新
        throw saveError // 重新抛出错误，让调用者知道保存失败
      }
    } else {
      ElMessage.success({ message: '保存成功（请保存流程以持久化）', duration: 1000 })
      
      // 即使未保存到服务器，也格式化显示
      if (pathParams !== undefined) {
        stepPathParamsText.value = stringifyWithTemplates(pathParams, 2)
      }
      if (queryParams !== undefined) {
        stepQueryParamsText.value = stringifyWithTemplates(queryParams, 2)
      }
      if (headers !== undefined) {
        stepHeadersText.value = stringifyWithTemplates(headers, 2)
      }
      if (body !== undefined) {
        stepBodyText.value = stringifyWithTemplates(body, 2)
      }
    }
  } catch (error: any) {
    ElMessage.error({ message: '保存失败: ' + (error.message || '未知错误'), duration: 2000 })
  }
}

// 添加步骤断言
const addStepAssertion = (index: number) => {
  stepAssertions.value.splice(index + 1, 0, { type: 'status_code', operator: 'eq', expected: '200' })
}

// 删除步骤断言
const removeStepAssertion = (index: number) => {
  if (stepAssertions.value.length > 1) {
    stepAssertions.value.splice(index, 1)
  } else {
    ElMessage.warning({ message: '至少需要保留一个断言', duration: 1500 })
  }
}


// 格式化响应体为JSON
// 格式化空对象的辅助函数
const formatEmptyObject = () => '{\n\n}'

// 格式化JSON对象，空对象返回格式化字符串
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

// 切换执行详情折叠/展开
const toggleResultDetail = (index: number) => {
  if (expandedResultIndices.value.has(index)) {
    expandedResultIndices.value.delete(index)
  } else {
    expandedResultIndices.value.add(index)
    // 初始化该结果的标签页
    if (!executionDetailActiveTabs.value[index]) {
      executionDetailActiveTabs.value[index] = 'headers'
    }
  }
}

// 保存局部变量
const saveLocalVariables = async () => {
  if (!editingFlowId.value) {
    ElMessage.warning({ message: '请先保存流程', duration: 1500 })
    return
  }
  
  try {
    // 构建变量列表
    const variables = localVariables.value
      .filter(v => v.key.trim() && v.value.trim())
      .map(v => ({
        id: v.id,
        key: v.key.trim(),
        value: v.value.trim()
      }))
    
    // 调用后端API保存
    const savedVariables = await apitestApi.saveFlowVariables(editingFlowId.value, variables)
    
    // 更新本地数据，使用后端返回的数据（包含正确的 id）
    localVariables.value = savedVariables.map(v => ({
      id: v.id,
      key: v.key,
      value: v.value
    }))
    
    // 同时更新全局变量对象（用于向后兼容）
    const vars: Record<string, string> = {}
    savedVariables.forEach(v => {
      vars[v.key] = v.value
    })
    flowForm.global_variables_text = JSON.stringify(vars, null, 2)
    
    ElMessage.success({ message: '保存成功', duration: 1000 })
  } catch (error: any) {
    ElMessage.error({ message: error.message || '保存失败', duration: 2000 })
  }
}

// 项目变更处理
const onProjectChange = async () => {
  // 如果执行链中有接口，需要加载这些接口的信息（可能来自旧项目）
  const stepEndpointIds = flowForm.steps.map(step => step.endpoint_id).filter(id => id) as number[]
  
  // 重新加载新项目下的接口列表
  if (flowForm.project_id) {
    try {
      const data = await apitestApi.getApiEndpoints({ project_id: flowForm.project_id, limit: 500 })
      flowEndpoints.value = data
      endpoints.value = data
      
      // 如果执行链中有接口，但新项目下的接口列表中没有这些接口，需要从所有接口中加载
      if (stepEndpointIds.length > 0) {
        const missingIds = stepEndpointIds.filter(id => !endpoints.value.find(ep => ep.id === id))
        if (missingIds.length > 0) {
          try {
            const allEndpoints = await apitestApi.getApiEndpoints({ limit: 1000 })
            const missingEndpoints = allEndpoints.filter(ep => missingIds.includes(ep.id))
            // 将缺失的接口添加到 endpoints 中，以便显示
            endpoints.value = [...endpoints.value, ...missingEndpoints]
          } catch (error) {
            // 忽略错误，至少新项目的接口已经加载了
          }
        }
      }
    } catch (error) {
      flowEndpoints.value = []
      endpoints.value = []
    }
  } else {
    // 如果清空项目，但执行链中有接口，需要从所有接口中加载这些接口的信息
    if (stepEndpointIds.length > 0) {
      try {
        const allEndpoints = await apitestApi.getApiEndpoints({ limit: 1000 })
        const neededEndpoints = allEndpoints.filter(ep => stepEndpointIds.includes(ep.id))
        endpoints.value = neededEndpoints
      } catch (error) {
        endpoints.value = []
      }
    } else {
      endpoints.value = []
    }
    flowEndpoints.value = []
  }
  flowEndpointKeyword.value = ''
}

const getEndpointName = (id?: number) => {
  if (!id) return '-'
  return endpoints.value.find(ep => ep.id === id)?.name || `ID ${id}`
}

const getEndpointMethod = (id?: number) => {
  if (!id) return '-'
  return endpoints.value.find(ep => ep.id === id)?.method || '-'
}

const getEndpointPath = (id?: number) => {
  if (!id) return '-'
  return endpoints.value.find(ep => ep.id === id)?.path || '-'
}

const getEndpointDescription = (id?: number) => {
  if (!id) return '-'
  return endpoints.value.find(ep => ep.id === id)?.description || '-'
}

// 显示流程接口列表
const showFlowEndpoints = async (flow: ApiTestFlow) => {
  if (!flow.steps || flow.steps.length === 0) {
    ElMessage.info({ message: '该流程暂无接口', duration: 1500 })
    return
  }
  
  // 获取所有接口ID
  const endpointIds = flow.steps.map(step => step.endpoint_id)
  
  // 如果当前项目下的接口列表已加载，直接使用
  let endpointList: ApiEndpoint[] = []
  if (flow.project_id && flowEndpoints.value.length > 0) {
    endpointList = flowEndpoints.value.filter(ep => endpointIds.includes(ep.id))
  }
  
  // 如果接口列表不完整，需要加载所有接口
  if (endpointList.length < endpointIds.length) {
    try {
      const allEndpoints = await apitestApi.getApiEndpoints({ limit: 1000 })
      endpointList = allEndpoints.filter(ep => endpointIds.includes(ep.id))
    } catch (error: any) {
      ElMessage.error({ message: '加载接口列表失败', duration: 2000 })
      return
    }
  }
  
  // 按照步骤顺序排序
  const sortedEndpoints: ApiEndpoint[] = []
  endpointIds.forEach(id => {
    const endpoint = endpointList.find(ep => ep.id === id)
    if (endpoint) {
      sortedEndpoints.push(endpoint)
    }
  })
  
  selectedFlowEndpoints.value = sortedEndpoints
  endpointsDialogPage.value = 1  // 重置分页到第一页
  showEndpointsDialog.value = true
}

const getEnvironmentName = (id?: number) => {
  if (!id) return '-'
  return allEnvironments.value.find(env => env.id === id)?.name || `环境#${id}`
}

// 获取接口信息
const getEndpointInfo = (endpointId?: number): ApiEndpoint | null => {
  if (!endpointId) return null
  return flowEndpoints.value.find(ep => ep.id === endpointId) || 
         endpoints.value.find(ep => ep.id === endpointId) || 
         null
}

// 获取步骤名称
const getStepName = (stepIndex: number): string => {
  if (stepIndex < 0 || stepIndex >= flowForm.steps.length) return '未知步骤'
  const step = flowForm.steps[stepIndex]
  // 优先使用别名，其次使用接口名称
  if (step.alias) return step.alias
  const endpointInfo = getEndpointInfo(step.endpoint_id)
  return endpointInfo?.name || `接口 #${step.endpoint_id}`
}

// 工具函数
const getMethodTag = (method: string) => {
  const map: Record<string, string> = {
    GET: 'success',
    POST: 'warning',  // 使用warning类型（橙色）
    PUT: 'warning',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return map[method] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 初始化
onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 如果有选中的项目，自动设置过滤器
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    flowFilters.project_id = getCurrentProjectId.value
  }
  loadProjects()
  loadEnvironments()
  loadFlows()
  
  // 监听项目切换事件
  const cleanup = onProjectChanged(() => {
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      flowFilters.project_id = getCurrentProjectId.value
    }
    loadProjects()
    loadFlows()
  })
  
  // 组件卸载时清理监听
  onUnmounted(() => {
    cleanup()
  })
})
</script>

<style scoped>
.api-flow-page {
  height: 100%;
  animation: fadeIn 0.5s ease-in;
  padding: 0;
  box-sizing: border-box;
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

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.filter-header h2 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
}

.flow-endpoints {
  margin-bottom: 20px;
}

.flow-step-editor {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

.table-card :deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

.table-card :deep(.el-table__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 30px;
}

/* 接口列表弹框关闭按钮样式 - 白色背景显示深色关闭按钮 */
.endpoints-dialog-centered :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #909399;
  font-size: 20px;
}

.endpoints-dialog-centered :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #409eff;
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

.table-card :deep(.el-table__header th) {
  background: transparent;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
  padding: 16px 8px;
  white-space: nowrap;
  overflow: visible;
}

:deep(.el-table__body tr:hover) {
  background-color: rgba(102, 126, 234, 0.05);
}

:deep(.el-table__body td) {
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
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

:deep(.el-card) {
  border: none;
  transition: box-shadow 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

:deep(.el-drawer) {
  border-radius: 12px 0 0 12px;
  overflow: hidden;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  height: 100vh !important;
}

:deep(.el-drawer__body) {
  height: calc(100vh - 60px) !important;
  overflow-y: auto;
  padding: 20px;
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

.filter-row :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  font-weight: 500;
  transition: all 0.3s ease;
}

.filter-row :deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

/* 流程基本信息 */
.flow-basic-info {
  background: #f5f7fa;
  padding: 16px;
  margin-bottom: 20px;
  border-radius: 8px;
}

/* 流程编辑器两列布局 */
.flow-editor-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 100px);
  min-height: 600px;
}

.flow-execution-chain {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #ebeef5;
  padding-right: 20px;
}

.chain-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #ebeef5;
}

.chain-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.chain-actions {
  display: flex;
  gap: 8px;
}

.execution-progress-dialog {
  padding: 30px 20px;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 30px;
}

.progress-icon {
  font-size: 48px;
  color: #409eff;
  animation: rotate 2s linear infinite;
}

.progress-icon-success {
  color: #67c23a;
  animation: none;
}

.progress-icon-error {
  color: #f56c6c;
  animation: none;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.progress-title {
  flex: 1;
  text-align: left;
}

.progress-title-main {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.progress-title-sub {
  font-size: 14px;
  color: #909399;
}

.progress-bar-container {
  margin-bottom: 24px;
}

.progress-step-info {
  text-align: center;
  margin-bottom: 20px;
}

.progress-stats {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.chain-search {
  margin-bottom: 16px;
}

.endpoint-search-results {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 8px;
}

.endpoint-search-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 4px;
}

.endpoint-search-item:hover {
  background: #f5f7fa;
}

.endpoint-name {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.endpoint-path {
  flex: 2;
  color: #666;
  font-size: 12px;
}

/* 加入执行链按钮样式 */
.add-to-chain-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
}

.add-to-chain-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.chain-steps {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

/* 执行链序号之间的连接线 - GitHub 风格 */
.step-connector {
  position: relative;
  height: 32px;
  margin: 0;
  padding: 0;
  pointer-events: none;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.connector-svg {
  width: 30px;
  height: 32px;
  display: block;
  margin-left: 16px;
}

.connector-svg line {
  transition: all 0.3s ease;
}

.connector-svg circle {
  transition: all 0.3s ease;
}

/* 编辑步骤抽屉样式 */
.step-edit-container {
  height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
}

.step-edit-content {
  display: flex;
  flex-direction: row !important;
  gap: 24px;
  flex: 1;
  overflow: hidden;
  min-height: 0;
  height: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 100%);
}

.step-edit-left {
  flex: 1;
  overflow-y: auto;
  padding-right: 16px;
  min-width: 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.step-edit-left :deep(.el-descriptions) {
  border: 1px solid #ebeef5;
  border-radius: 8px;
}

.step-edit-left :deep(.el-descriptions__label) {
  width: 80px;
}

.step-edit-left :deep(.el-descriptions__content) {
  color: #606266;
}

.step-edit-right {
  flex: 1;
  overflow-y: auto;
  padding-left: 16px;
  min-width: 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 自定义滚动条 */
.step-edit-left::-webkit-scrollbar,
.step-edit-right::-webkit-scrollbar {
  width: 6px;
}

.step-edit-left::-webkit-scrollbar-thumb,
.step-edit-right::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}


/* 局部变量快捷引用样式 */
.variables-quick-ref {
  margin: 16px 0;
  padding: 12px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border: 1px solid #b3d8ff;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.quick-ref-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  white-space: nowrap;
  padding-top: 4px;
}

.quick-ref-label .el-icon {
  font-size: 16px;
  color: #409eff;
}

.quick-ref-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.variable-quick-btn {
  font-size: 12px;
  padding: 5px 12px;
  height: auto;
  border-radius: 4px;
  font-family: inherit;
  transition: all 0.3s;
  background: #ecf5ff !important;
  border: 1px solid #d9ecff !important;
  color: #409eff !important;
  font-weight: normal;
}

.variable-quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.15);
  background: #d9ecff !important;
  border-color: #b3d8ff !important;
  color: #409eff !important;
}

.variable-quick-btn .el-icon--right {
  margin-left: 4px;
}

.param-tabs {
  margin-top: 16px;
}

.param-textarea {
  width: 100%;
}

.param-textarea-fixed :deep(textarea) {
  height: 400px !important;
  min-height: 400px !important;
  max-height: 400px !important;
}

.response-pre {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.no-response {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.response-content {
  height: 100%;
}

.step-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
  position: relative;
  cursor: pointer;
  margin-bottom: 0;
}

.step-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.step-card.step-active {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.step-card.step-disabled {
  opacity: 0.6;
  background: #f5f7fa;
  border-color: #dcdfe6;
}

.step-card.step-disabled:hover {
  border-color: #dcdfe6;
  box-shadow: none;
}

.step-number-disabled {
  background: #c0c4cc !important;
  color: #909399 !important;
}

.step-path-disabled {
  color: #909399 !important;
}

.step-description-disabled {
  color: #909399 !important;
}

.step-status-disabled {
  color: #909399 !important;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.step-content {
  flex: 1;
  min-width: 0;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.step-path {
  font-family: monospace;
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.step-description {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.step-status {
  font-size: 12px;
  color: #999;
}

.step-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

/* 执行链步骤操作按钮 - 去掉白色背景 */
.step-actions .el-button {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 4px !important;
  transition: transform 0.2s, opacity 0.2s;
}

.step-actions .el-button:hover {
  background: transparent !important;
  background-color: transparent !important;
  transform: scale(1.1);
}

.step-actions .el-button:focus {
  background: transparent !important;
  background-color: transparent !important;
}

/* 启用/禁用按钮 - 绿色(启用)/橙色(禁用) */
.step-actions .toggle-enable-btn.el-button--success {
  color: #67c23a !important;
}

.step-actions .toggle-enable-btn.el-button--warning {
  color: #e6a23c !important;
}

.step-actions .toggle-enable-btn:hover {
  opacity: 0.8;
}

/* 上移按钮 - 蓝色 */
.step-actions .el-button:nth-child(2) {
  color: #409eff !important;
}

.step-actions .el-button:nth-child(2):hover {
  color: #66b1ff !important;
}

/* 下移按钮 - 蓝色 */
.step-actions .el-button:nth-child(3) {
  color: #409eff !important;
}

.step-actions .el-button:nth-child(3):hover {
  color: #66b1ff !important;
}

/* 复制按钮 - 紫色 */
.step-actions .el-button:nth-child(4) {
  color: #9b59b6 !important;
}

.step-actions .el-button:nth-child(4):hover {
  color: #a569bd !important;
}

/* 删除按钮 - 红色 */
.step-actions .el-button:nth-child(5) {
  color: #f56c6c !important;
}

.step-actions .el-button:nth-child(5):hover {
  color: #f78989 !important;
}

/* 禁用状态的按钮变灰 */
.step-actions .el-button.is-disabled {
  color: #c0c4cc !important;
  opacity: 0.6;
}

.empty-chain {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
}

/* 右侧执行配置 */
.flow-execution-config {
  width: 380px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  padding-left: 20px;
}

.config-section {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.config-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

/* 执行配置表单左对齐 */
.execution-config-form {
  margin-left: 0 !important;
}

.execution-config-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.execution-config-form :deep(.el-form-item__label) {
  text-align: left;
  padding-right: 12px;
}

.execution-config-form :deep(.el-form-item__content) {
  margin-left: 0 !important;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.help-icon {
  color: #909399;
  cursor: help;
  font-size: 16px;
}

/* 全局变量列表 */
.global-variables-list {
  margin-bottom: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.variable-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

.variable-key {
  font-weight: 500;
  color: #333;
  min-width: 100px;
}

.variable-value {
  flex: 1;
  color: #666;
  font-size: 13px;
  word-break: break-all;
}

.empty-variables {
  text-align: center;
  color: #999;
  padding: 20px;
  font-size: 13px;
}

/* 局部变量列表 */
.local-variables-list {
  margin-bottom: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.variable-row {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.variable-input {
  flex-shrink: 0;
}

.variable-row .variable-input:first-child {
  width: 100px;
  flex: 0 0 100px;
}

.variable-row .variable-input:nth-child(2) {
  flex: 1;
  min-width: 0;
  max-width: 200px;
}

.variable-row .el-button {
  flex-shrink: 0;
  padding: 0 !important;
  margin: 0;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 32px;
  width: 32px;
  height: 32px;
}

.variable-row .el-button .el-icon {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  margin: 0 !important;
  width: 100% !important;
  height: 100% !important;
}

/* 局部变量复制按钮背景色 - 绿色 */
.variable-copy-btn {
  background: #67c23a !important;
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  color: white !important;
  box-shadow: none !important;
}

.variable-copy-btn:hover {
  background: #5daf34 !important;
  background-color: #5daf34 !important;
  border-color: #5daf34 !important;
  color: white !important;
}

.variable-row .variable-copy-btn {
  background: #67c23a !important;
  background-color: #67c23a !important;
  border-color: #67c23a !important;
  color: white !important;
}

.variable-row .variable-copy-btn:hover {
  background: #5daf34 !important;
  background-color: #5daf34 !important;
  border-color: #5daf34 !important;
  color: white !important;
}

/* 局部变量删除按钮背景色 */
.variable-delete-btn {
  background: #f56c6c !important;
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: white !important;
  box-shadow: none !important;
}

.variable-delete-btn:hover {
  background: #e55252 !important;
  background-color: #e55252 !important;
  border-color: #e55252 !important;
  color: white !important;
}

.variable-row .variable-delete-btn {
  background: #f56c6c !important;
  background-color: #f56c6c !important;
  border-color: #f56c6c !important;
  color: white !important;
}

.variable-row .variable-delete-btn:hover {
  background: #e55252 !important;
  background-color: #e55252 !important;
  border-color: #e55252 !important;
  color: white !important;
}

/* 生成变量按钮样式 */
.generate-variable-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  border-radius: 6px !important;
}

.generate-variable-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  color: white !important;
}

/* 生成变量对话框按钮样式 */
.generate-dialog-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  border-radius: 6px !important;
}

.generate-dialog-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  color: white !important;
}

.generate-dialog-close-btn {
  background: #909399 !important;
  border-color: #909399 !important;
  color: white !important;
  border-radius: 6px !important;
}

.generate-dialog-close-btn:hover {
  background: #82848a !important;
  border-color: #82848a !important;
  color: white !important;
}

.variable-actions {
  display: flex;
  gap: 8px;
}

/* 执行统计 */
.statistics-boxes {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-box {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  border: 2px solid;
}

.stat-total {
  background: #fff;
  border-color: #dcdfe6;
}

.stat-success {
  background: #f0f9ff;
  border-color: #67c23a;
}

.stat-failure {
  background: #fef0f0;
  border-color: #f56c6c;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.execution-progress {
  margin-top: 12px;
}

/* 白色字体按钮 */
.white-text-btn {
  color: white !important;
}

.white-text-btn:hover {
  color: white !important;
}

:deep(.white-text-btn) {
  color: white !important;
}

:deep(.white-text-btn:hover) {
  color: white !important;
}

:deep(.el-button.white-text-btn) {
  color: white !important;
}

:deep(.el-button.white-text-btn:hover) {
  color: white !important;
}

:deep(.el-button.is-link.white-text-btn) {
  color: white !important;
}

:deep(.el-button.is-link.white-text-btn:hover) {
  color: white !important;
}

/* 导出按钮样式 - 使用青色，与其他按钮区分 */
.export-btn {
  background: #17a2b8 !important;
  border-color: #17a2b8 !important;
  color: white !important;
}

.export-btn:hover {
  background: #138496 !important;
  border-color: #138496 !important;
  color: white !important;
}

::deep(.export-btn) {
  background: #17a2b8 !important;
  border-color: #17a2b8 !important;
  color: white !important;
}

::deep(.export-btn:hover) {
  background: #138496 !important;
  border-color: #138496 !important;
  color: white !important;
}

/* 导入按钮样式 - 使用浅蓝色，与其他按钮区分 */
.import-btn {
  background: #5dade2 !important;
  border-color: #5dade2 !important;
  color: white !important;
}

.import-btn:hover {
  background: #3498db !important;
  border-color: #3498db !important;
  color: white !important;
}

::deep(.import-btn) {
  background: #5dade2 !important;
  border-color: #5dade2 !important;
  color: white !important;
}

::deep(.import-btn:hover) {
  background: #3498db !important;
  border-color: #3498db !important;
  color: white !important;
}

/* 接口数量文本样式 - 纯数字可点击 */
.endpoint-count-text {
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.2s;
}

.endpoint-count-text:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 执行按钮红色背景 */
.execute-btn {
  background: #f56c6c !important;
  border-color: #f56c6c !important;
  color: white !important;
}

.execute-btn:hover {
  background: #e55252 !important;
  border-color: #e55252 !important;
  color: white !important;
}

/* 关闭按钮背景色 */
.close-btn {
  background: #909399 !important;
  border-color: #909399 !important;
  color: white !important;
}

.close-btn:hover {
  background: #82848a !important;
  border-color: #82848a !important;
  color: white !important;
}

/* 执行详情容器样式 */
.execution-details-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.execution-details-header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #ebeef5;
  padding: 0 20px 12px 20px;
}

.execution-details-header-section h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.execution-details-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px 20px;
}

.execution-details-item {
  margin-bottom: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  position: relative;
}

.execution-details-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.execution-details-header-number {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 48px;
  flex-shrink: 0;
}

.execution-details-header:hover {
  background-color: #f5f7fa;
}

.result-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.result-path {
  font-size: 14px;
  color: #909399;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.expand-icon {
  transition: transform 0.3s;
  color: #909399;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.execution-details-content {
  display: flex;
  gap: 24px;
  min-height: 0;
  padding: 20px;
}

.execution-details-left,
.execution-details-right {
  flex: 1;
  overflow-y: auto;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  min-width: 0;
}

.execution-details-left {
  border-right: 1px solid #ebeef5;
}

.execution-item {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #ebeef5;
}

.execution-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.execution-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f2f5;
}

.execution-item-title {
  flex: 1;
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.execution-item-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-item-section {
  margin-bottom: 8px;
}

.section-label {
  font-weight: 500;
  color: #606266;
  font-size: 13px;
  margin-bottom: 6px;
}

.section-value {
  color: #303133;
  font-size: 13px;
  word-break: break-all;
}

.section-value.error-text {
  color: #f56c6c;
}

.section-pre {
  background: #f8fafc;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.6;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

/* 自定义滚动条 */
.execution-details-left::-webkit-scrollbar,
.execution-details-right::-webkit-scrollbar {
  width: 6px;
}

.execution-details-left::-webkit-scrollbar-thumb,
.execution-details-right::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.execution-details-left::-webkit-scrollbar-thumb:hover,
.execution-details-right::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}

/* 执行详情按钮样式 */
.execution-details-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: white !important;
  border-radius: 6px !important;
  padding: 8px 16px !important;
  font-size: 14px !important;
}

.execution-details-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
  color: white !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 抽屉高度占满屏幕 */
:deep(.el-drawer__body) {
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
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

/* 断言样式 - 参考接口测试页面 */
.assertion-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

.assertion-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.assertion-row:hover {
  background: #f0f5ff;
}

/* Assertion 链接按钮去掉背景和立体感 */
.assertion-row .el-button.is-link {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.assertion-row .el-button.is-link:hover,
.assertion-row .el-button.is-link:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.assertion-type {
  width: 120px;  /* 第一个下拉（类型选择） */
}

.assertion-operator {
  width: 120px;  /* 第二个下拉（操作符选择） */
}

/* JSON路径输入框：只在json_path类型时显示 */
.assertion-target {
  flex: 1;  /* 与期望值输入框平分剩余空间 */
  min-width: 0;  /* 允许缩小 */
}

/* 期望值输入框 */
.assertion-value {
  flex: 1;  /* 占据剩余空间，对于JSON路径行，与JSON路径输入框平分 */
  min-width: 0;  /* 允许缩小 */
}


/* 收藏图标样式 */
.favorite-icon {
  transition: all 0.3s ease;
}

.favorite-icon:hover {
  transform: scale(1.2);
}

.favorite-icon.is-favorite {
  color: #f7ba2a !important;
}

.favorite-icon:not(.is-favorite) {
  color: #dcdfe6 !important;
}

.favorite-icon:not(.is-favorite):hover {
  color: #f7ba2a !important;
}

</style>

