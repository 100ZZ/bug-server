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
          <div style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <el-button size="small" @click="showAddItemDialog">添加接口/流程</el-button>
            <span v-if="formData.items && formData.items.length > 0" style="font-size: 12px; color: #909399;">
              共 {{ formData.items.length }} 项
            </span>
          </div>
          <el-table :data="paginatedFormItems" border style="width: 100%">
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
              <template #default="{ row }">
                <el-button link type="danger" size="small" class="delete-btn-no-bg" @click="removeItemById(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="formData.items && formData.items.length > formItemsPageSize" style="margin-top: 12px; display: flex; justify-content: center;">
            <el-pagination
              v-model:current-page="formItemsPage"
              :page-size="formItemsPageSize"
              :total="formData.items.length"
              layout="prev, pager, next"
              small
            />
          </div>
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
          <span class="dialog-description">
            <template v-if="existingItemType === 'api'">当前任务已添加接口，只能继续添加接口</template>
            <template v-else-if="existingItemType === 'flow'">当前任务已添加流程，只能继续添加流程</template>
            <template v-else>选择要添加的接口或流程，一个任务只能添加同一类型</template>
          </span>
        </div>
      </template>
      <el-tabs v-model="addItemType">
        <el-tab-pane label="接口" name="api" :disabled="!canAddApi">
          <div style="margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
            <el-checkbox 
              v-model="selectAllApis" 
              @change="handleSelectAllApis"
              :indeterminate="isIndeterminateApis"
            >
              全选所有接口
            </el-checkbox>
            <span style="font-size: 12px; color: #909399;">
              共 {{ filteredApis.length }} 个接口，已选择 {{ selectedApiIds.length }} 个
            </span>
          </div>
          <div v-if="selectAllApis && filteredApis.length > 0" style="padding: 12px; background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 4px; margin-bottom: 10px; text-align: center; color: #1890ff;">
            <el-icon style="margin-right: 4px; vertical-align: middle;"><InfoFilled /></el-icon>
            已全选 {{ filteredApis.length }} 个接口
          </div>
          <el-select
            v-model="selectedApiIds"
            multiple
            filterable
            collapse-tags
            :placeholder="selectAllApis ? `已选择 ${selectedApiIds.length} 个接口` : '搜索或选择接口（支持按方法、路径、名称搜索）'"
            style="width: 100%"
            :filter-method="filterApis"
            :max-collapse-tags="1"
            collapse-tags-tooltip
            popper-class="api-select-dropdown"
          >
            <el-option
              v-for="api in displayApisLimited"
              :key="api.id"
              :label="`${api.method} ${api.path} - ${api.name}`"
              :value="api.id"
            />
          </el-select>
          <div v-if="!selectAllApis && filteredApis.length > 10" style="margin-top: 10px; display: flex; justify-content: center;">
            <el-pagination
              v-model:current-page="apiPage"
              :page-size="10"
              :total="filteredApis.length"
              layout="prev, pager, next"
              small
              @current-change="handleApiPageChange"
            />
          </div>
        </el-tab-pane>
        <el-tab-pane label="流程" name="flow" :disabled="!canAddFlow">
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
      width="900px"
      align-center
      :show-close="true"
      class="items-dialog-centered"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">任务项列表</span>
          <span class="dialog-description">查看任务中包含的所有接口和流程，按执行顺序排列</span>
        </div>
      </template>
      <el-table :data="paginatedTaskItems" border>
        <el-table-column label="编号" width="80" align="center">
          <template #default="{ $index }">
            {{ (itemsDialogPage - 1) * itemsDialogPageSize + $index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.item_type === 'api' ? 'primary' : 'success'" size="small">
              {{ row.item_type === 'api' ? '接口' : '流程' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="名称" min-width="200" show-overflow-tooltip>
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
      <div v-if="currentTaskItems.length > 0" style="margin-top: 16px; text-align: right;">
        <el-pagination
          v-model:current-page="itemsDialogPage"
          v-model:page-size="itemsDialogPageSize"
          :page-sizes="[10]"
          layout="prev, pager, next, ->, total"
          :total="currentTaskItems.length"
          small
        />
      </div>
    </el-dialog>

    <!-- 执行对话框 -->
    <el-dialog
      v-model="executeDialogVisible"
      width="720px"
      class="execute-dialog"
    >
      <template #header>
        <div class="execute-dialog-header">
          <div class="execute-dialog-icon">
            <el-icon :size="24"><VideoPlay /></el-icon>
          </div>
          <div class="execute-dialog-title-wrap">
            <span class="execute-dialog-title">执行测试任务</span>
            <span class="execute-dialog-desc">选择执行环境，可设置 Header 和断言替换</span>
          </div>
        </div>
      </template>
      
      <div class="execute-dialog-content">
        <!-- 环境选择卡片 -->
        <div class="execute-section">
          <div class="execute-section-header">
            <el-icon class="section-icon" color="#409eff"><Connection /></el-icon>
            <span class="section-title">执行环境</span>
            <el-tag type="danger" size="small">必选</el-tag>
          </div>
          <div class="execute-section-body">
            <el-select 
              v-model="executeForm.environment_id" 
              placeholder="请选择执行环境" 
              style="width: 100%"
              size="large"
            >
              <el-option
                v-for="env in environments"
                :key="env.id"
                :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
                :value="env.id"
              />
            </el-select>
          </div>
        </div>
        
        <!-- 替换设置卡片 -->
        <div class="execute-section">
          <div class="execute-section-header">
            <el-icon class="section-icon" color="#e6a23c"><Setting /></el-icon>
            <span class="section-title">替换设置</span>
            <el-tag type="info" size="small">可选</el-tag>
          </div>
          <div class="execute-section-body">
            <!-- Header 替换 -->
            <div class="replacement-group">
              <div class="replacement-group-title">
                <span>Header 替换</span>
                <span class="replacement-hint">执行时将替换请求头中的指定 Key</span>
              </div>
              <div class="replacement-list">
                <div v-for="(item, index) in executeForm.header_replacements" :key="'header-' + index" class="replacement-row">
                  <el-input 
                    v-model="item.key" 
                    placeholder="Key"
                    class="replacement-key-input"
                  >
                    <template #prefix>
                      <el-icon><Key /></el-icon>
                    </template>
                  </el-input>
                  <el-input 
                    v-model="item.value" 
                    placeholder="Value"
                    class="replacement-value-input"
                  />
                  <div class="replacement-actions">
                    <el-button link type="danger" @click="removeHeaderReplacement(index)">删除</el-button>
                    <el-button link type="primary" @click="addHeaderReplacementAfter(index)">新增</el-button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Assertion 替换 -->
            <div class="replacement-group" style="margin-top: 16px;">
              <div class="replacement-group-title">
                <span>Assertion 替换</span>
                <span class="replacement-hint">执行时将使用以下断言替换原有断言</span>
              </div>
              <div class="replacement-list">
                <div v-for="(item, index) in executeForm.assertion_replacements" :key="'assertion-' + index" class="assertion-replacement-row">
                  <el-select v-model="item.type" placeholder="类型" class="assertion-type-select">
                    <el-option label="状态码" value="status_code" />
                    <el-option label="JSON路径" value="json_path" />
                    <el-option label="响应时间" value="response_time" />
                    <el-option label="包含" value="contains" />
                  </el-select>
                  <el-input 
                    v-if="item.type === 'json_path'"
                    v-model="item.target" 
                    placeholder="路径，如：data.id"
                    class="assertion-target-input"
                  />
                  <el-select v-model="item.operator" placeholder="操作符" class="assertion-operator-select">
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
                    placeholder="期望值"
                    class="replacement-value-input"
                  />
                  <div class="replacement-actions">
                    <el-button link type="danger" @click="removeAssertionReplacement(index)">删除</el-button>
                    <el-button link type="primary" @click="addAssertionReplacementAfter(index)">新增</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="execute-dialog-footer">
          <el-button @click="executeDialogVisible = false" size="large">取消</el-button>
          <el-button type="primary" :loading="executing" @click="confirmExecute" size="large">
            <el-icon v-if="!executing"><VideoPlay /></el-icon>
            开始执行
          </el-button>
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
        <div v-if="executionDetailLoading" class="execution-detail-container" style="display: flex; justify-content: center; align-items: center; min-height: 300px;">
          <el-icon class="is-loading" :size="40" style="color: #409EFF;"><Loading /></el-icon>
        </div>
        <div v-else-if="currentExecution" class="execution-detail-container">
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
        
        <!-- 分页控制 -->
        <div v-if="currentExecution && currentExecution.execution_results && currentExecution.execution_results.length > resultPageSize" 
             style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 13px; color: #909399;">
            共 {{ currentExecution.execution_results.length }} 条结果，当前显示第 {{ (resultCurrentPage - 1) * resultPageSize + 1 }} - {{ Math.min(resultCurrentPage * resultPageSize, currentExecution.execution_results.length) }} 条
          </span>
          <el-pagination
            v-model:current-page="resultCurrentPage"
            :page-size="resultPageSize"
            :total="currentExecution.execution_results.length"
            layout="prev, pager, next"
            small
          />
        </div>
        
        <div v-if="currentExecution && currentExecution.execution_results && currentExecution.execution_results.length > 0" class="execution-results-container">
          <div v-for="(result, index) in paginatedExecutionResults" :key="getResultRealIndex(index)" class="execution-result-item">
            <div class="execution-result-header" @click="toggleResultDetail(getResultRealIndex(index))">
              <el-tag :type="result.item_type === 'api' ? 'primary' : 'success'" size="small">
                {{ result.item_type === 'api' ? '接口' : '流程' }}
              </el-tag>
              <span class="result-name">{{ result.item_name }}</span>
              <div style="margin-left: auto; display: flex; align-items: center; gap: 12px; cursor: pointer;">
                <el-tag :type="result.success ? 'success' : 'danger'" size="small">
                  {{ result.success ? '成功' : '失败' }}
                </el-tag>
                <el-icon :class="['expand-icon', { 'expanded': expandedResultIndices.has(getResultRealIndex(index)) }]">
                  <ArrowDown />
                </el-icon>
              </div>
            </div>
            
            <!-- 使用 v-if 替代 v-show，只在展开时渲染详细内容 -->
            <div v-if="expandedResultIndices.has(getResultRealIndex(index))" class="execution-result-content">
              <!-- 左侧：请求参数 -->
              <div class="execution-result-left">
                <el-divider>请求参数</el-divider>
                <el-tabs v-model="resultDetailActiveTabs[getResultRealIndex(index)]" class="param-tabs">
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
import { Search, Star, StarFilled, Plus, List, View, Delete, VideoPlay, Document, Clock, Warning, EditPen, ArrowDown, InfoFilled, Loading, Setting, Connection, Key } from '@element-plus/icons-vue'
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
  getTestTaskExecution,
  type TestTask,
  type TestTaskItem,
  type TestTaskCreate,
  type TestTaskExecution,
  type HeaderReplacement,
  type AssertionReplacement
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
const selectAllApis = ref(false)
const apiPage = ref(1)
const apiPageSize = 10

// 获取当前任务已有的任务项类型（api 或 flow）
const existingItemType = computed(() => {
  if (!formData.value.items || formData.value.items.length === 0) {
    return null // 没有任务项，可以添加任何类型
  }
  // 返回第一个任务项的类型
  return formData.value.items[0].item_type as 'api' | 'flow'
})

// 是否可以添加接口
const canAddApi = computed(() => {
  return existingItemType.value === null || existingItemType.value === 'api'
})

// 是否可以添加流程
const canAddFlow = computed(() => {
  return existingItemType.value === null || existingItemType.value === 'flow'
})

// 任务项表格分页
const formItemsPage = ref(1)
const formItemsPageSize = 10

const itemsDialogVisible = ref(false)
const currentTaskItems = ref<TestTaskItem[]>([])
const itemsDialogPage = ref(1)
const itemsDialogPageSize = ref(10)

// 分页后的任务项列表
const paginatedTaskItems = computed(() => {
  const start = (itemsDialogPage.value - 1) * itemsDialogPageSize.value
  return currentTaskItems.value.slice(start, start + itemsDialogPageSize.value)
})

const executeDialogVisible = ref(false)
const executeForm = ref<{
  environment_id: number | undefined
  header_replacements: HeaderReplacement[]
  assertion_replacements: AssertionReplacement[]
}>({
  environment_id: undefined,
  header_replacements: [],
  assertion_replacements: []
})
const currentExecuteTask = ref<TestTask | null>(null)

const detailDialogVisible = ref(false)
const currentTask = ref<TestTask | null>(null)

const reportDialogVisible = ref(false)
const currentReportTaskId = ref<number | null>(null)
const executions = ref<TestTaskExecution[]>([])
const currentExecution = ref<TestTaskExecution | null>(null)
const executionDetailDrawerVisible = ref(false)
const executionDetailLoading = ref(false)
const resultDetailActiveTabs = ref<Record<number, string>>({})
const expandedResultIndices = ref<Set<number>>(new Set())

// 执行结果分页
const resultCurrentPage = ref(1)
const resultPageSize = 20

// 分页后的执行结果
const paginatedExecutionResults = computed(() => {
  if (!currentExecution.value?.execution_results) return []
  const start = (resultCurrentPage.value - 1) * resultPageSize
  const end = start + resultPageSize
  return currentExecution.value.execution_results.slice(start, end)
})

// 获取结果的真实索引（用于展开状态等）
const getResultRealIndex = (pageIndex: number) => {
  return (resultCurrentPage.value - 1) * resultPageSize + pageIndex
}

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
  } else {
    const lowerKeyword = keyword.toLowerCase()
    filteredApis.value = availableApis.value.filter(api => {
      const method = (api.method || '').toLowerCase()
      const path = (api.path || '').toLowerCase()
      const name = (api.name || '').toLowerCase()
      return method.includes(lowerKeyword) || path.includes(lowerKeyword) || name.includes(lowerKeyword)
    })
  }
  // 重置到第一页
  apiPage.value = 1
  // 更新全选状态
  updateSelectAllApisState()
}


// 计算全选复选框的半选状态
const isIndeterminateApis = computed(() => {
  const selectedCount = selectedApiIds.value.length
  const filteredCount = filteredApis.value.length
  return selectedCount > 0 && selectedCount < filteredCount
})

// 计算要显示的接口列表（包含已选中的接口和当前页的接口，确保已选中的接口能正确显示标签）
const displayApis = computed(() => {
  // 如果全选且接口数量超过10个，需要确保所有已选中的接口都在选项中（用于显示标签），但只显示前10条
  if (selectAllApis.value && filteredApis.value.length > 10) {
    // 返回所有已选中的接口（确保标签能正确显示），但el-select只会显示前10条在列表中
    const selectedApis = selectedApiIds.value
      .map(id => filteredApis.value.find(api => api.id === id))
      .filter(api => api !== undefined) as ApiEndpoint[]
    return selectedApis
  }
  
  // 当前页的接口
  const start = (apiPage.value - 1) * apiPageSize
  const end = start + apiPageSize
  const pageApis = filteredApis.value.slice(start, end)
  
  // 已选中的接口（确保它们始终在选项中，以便正确显示标签）
  const selectedApis = selectedApiIds.value
    .map(id => filteredApis.value.find(api => api.id === id))
    .filter(api => api !== undefined) as ApiEndpoint[]
  
  // 合并当前页接口和已选中接口
  const allApis = [...selectedApis, ...pageApis]
  
  // 去重（按ID），已选中的优先
  const uniqueMap = new Map<number, ApiEndpoint>()
  // 先添加已选中的
  selectedApis.forEach(api => uniqueMap.set(api.id, api))
  // 再添加当前页的（如果还没添加）
  pageApis.forEach(api => {
    if (!uniqueMap.has(api.id)) {
      uniqueMap.set(api.id, api)
    }
  })
  
  return Array.from(uniqueMap.values())
})

// 下拉列表只显示最多10条记录，避免下拉列表过长
const displayApisLimited = computed(() => {
  const apis = displayApis.value
  // 下拉列表最多显示10条
  return apis.slice(0, 10)
})

// 任务项表格分页显示
const paginatedFormItems = computed(() => {
  const items = formData.value.items || []
  const start = (formItemsPage.value - 1) * formItemsPageSize
  const end = start + formItemsPageSize
  return items.slice(start, end)
})

// 更新全选状态
const updateSelectAllApisState = () => {
  const filteredIds = filteredApis.value.map(api => api.id)
  const allSelected = filteredIds.length > 0 && filteredIds.every(id => selectedApiIds.value.includes(id))
  selectAllApis.value = allSelected
}

// 处理分页变化
const handleApiPageChange = (page: number) => {
  apiPage.value = page
}


// 处理全选接口
const handleSelectAllApis = (checked: boolean) => {
  if (checked) {
    // 全选：添加所有过滤后的接口ID（不重复）
    const filteredIds = filteredApis.value.map(api => api.id)
    filteredIds.forEach(id => {
      if (!selectedApiIds.value.includes(id)) {
        selectedApiIds.value.push(id)
      }
    })
  } else {
    // 取消全选：只移除当前过滤结果中的接口ID，保留其他接口
    const filteredIds = filteredApis.value.map(api => api.id)
    selectedApiIds.value = selectedApiIds.value.filter(id => !filteredIds.includes(id))
  }
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
  // 重置任务项分页
  formItemsPage.value = 1
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
  // 重置表单，默认各显示一行
  executeForm.value = {
    environment_id: undefined,
    header_replacements: [{ key: '', value: '' }],
    assertion_replacements: [{
      type: 'status_code',
      target: '',
      operator: 'eq',
      expected: ''
    } as AssertionReplacement]
  }
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
    // 过滤掉空的替换项
    const headerReplacements = executeForm.value.header_replacements.filter(
      h => h.key && h.value
    )
    const assertionReplacements = executeForm.value.assertion_replacements.filter(
      a => {
        // 基本字段必须存在
        if (!a.type || !a.operator || (a.expected === undefined || a.expected === '')) {
          return false
        }
        // json_path 类型需要 target
        if (a.type === 'json_path' && !a.target) {
          return false
        }
        return true
      }
    )
    
    await executeTestTask(currentExecuteTask.value!.id, {
      environment_id: executeForm.value.environment_id,
      header_replacements: headerReplacements.length > 0 ? headerReplacements : undefined,
      assertion_replacements: assertionReplacements.length > 0 ? assertionReplacements : undefined
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

// Header 替换操作
const addHeaderReplacement = () => {
  executeForm.value.header_replacements.push({ key: '', value: '' })
}

const addHeaderReplacementAfter = (index: number) => {
  executeForm.value.header_replacements.splice(index + 1, 0, { key: '', value: '' })
}

const removeHeaderReplacement = (index: number) => {
  if (executeForm.value.header_replacements.length > 1) {
    executeForm.value.header_replacements.splice(index, 1)
  } else {
    // 如果只剩一行，清空内容而不是删除
    executeForm.value.header_replacements[0] = { key: '', value: '' }
  }
}

// Assertion 替换操作
const addAssertionReplacement = () => {
  executeForm.value.assertion_replacements.push({
    type: 'status_code',
    target: '',
    operator: 'eq',
    expected: ''
  } as AssertionReplacement)
}

const addAssertionReplacementAfter = (index: number) => {
  executeForm.value.assertion_replacements.splice(index + 1, 0, {
    type: 'status_code',
    target: '',
    operator: 'eq',
    expected: ''
  } as AssertionReplacement)
}

const removeAssertionReplacement = (index: number) => {
  if (executeForm.value.assertion_replacements.length > 1) {
    executeForm.value.assertion_replacements.splice(index, 1)
  } else {
    // 如果只剩一行，清空内容而不是删除
    executeForm.value.assertion_replacements[0] = {
      type: 'status_code',
      target: '',
      operator: 'eq',
      expected: ''
    } as AssertionReplacement
  }
}

const handleReport = async (row: TestTask) => {
  try {
    currentReportTaskId.value = row.id
    const response = await getTestTaskExecutions(row.id)
    // 由于响应拦截器已经返回了 response.data，所以 response 本身就是数组
    executions.value = Array.isArray(response) ? response : (response.data || [])
    reportDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error('加载执行记录失败: ' + (error.message || '未知错误'))
    console.error('加载执行记录失败:', error)
  }
}

const viewExecutionDetail = async (execution: TestTaskExecution) => {
  if (!currentReportTaskId.value) {
    ElMessage.error('无法获取任务ID')
    return
  }
  
  executionDetailDrawerVisible.value = true
  executionDetailLoading.value = true
  
  try {
    // 调用 API 获取完整的执行结果（包含 execution_results）
    const response = await getTestTaskExecution(currentReportTaskId.value, execution.id)
    const fullExecution = Array.isArray(response) ? response[0] : (response.data || response)
    currentExecution.value = fullExecution
    
    // 重置展开状态和分页
    expandedResultIndices.value.clear()
    resultCurrentPage.value = 1
    resultDetailActiveTabs.value = {}
    
    // 初始化当前页结果的标签页状态（延迟初始化，展开时再设置）
  } catch (error: any) {
    ElMessage.error('加载执行详情失败: ' + (error.message || '未知错误'))
    console.error('加载执行详情失败:', error)
    executionDetailDrawerVisible.value = false
  } finally {
    executionDetailLoading.value = false
  }
}

const showItemsDialog = async (row: TestTask) => {
  currentTaskItems.value = row.items || []
  itemsDialogPage.value = 1  // 重置分页到第一页
  // 加载对应项目的接口和流程数据，以正确显示名称
  if (row.project_id) {
    formData.value.project_id = row.project_id
    await loadAvailableApis()
    await loadAvailableFlows()
  }
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
  selectAllApis.value = false
  apiPage.value = 1
  
  // 根据已有任务项类型设置默认 tab
  if (existingItemType.value === 'api') {
    addItemType.value = 'api'
  } else if (existingItemType.value === 'flow') {
    addItemType.value = 'flow'
  } else {
    addItemType.value = 'api' // 默认显示接口 tab
  }
  
  loadAvailableApis()
  loadAvailableFlows()
}

// 监听选中接口变化，更新全选状态
watch(selectedApiIds, () => {
  updateSelectAllApisState()
}, { deep: true })

// 监听过滤后的接口列表变化，更新全选状态
watch(filteredApis, () => {
  updateSelectAllApisState()
}, { deep: true })

const confirmAddItems = () => {
  // 检查是否有选择
  if (selectedApiIds.value.length === 0 && selectedFlowIds.value.length === 0) {
    ElMessage.warning('请至少选择一个接口或流程')
    return
  }
  
  // 检查是否同时选择了接口和流程
  if (selectedApiIds.value.length > 0 && selectedFlowIds.value.length > 0) {
    ElMessage.warning('一个任务只能添加接口或流程，不能混合')
    return
  }
  
  // 检查与已有任务项类型是否一致
  if (existingItemType.value) {
    if (selectedApiIds.value.length > 0 && existingItemType.value !== 'api') {
      ElMessage.warning('当前任务已添加流程，不能再添加接口')
      return
    }
    if (selectedFlowIds.value.length > 0 && existingItemType.value !== 'flow') {
      ElMessage.warning('当前任务已添加接口，不能再添加流程')
      return
    }
  }
  
  // 获取当前最大排序值
  const maxSortOrder = formData.value.items?.length ? Math.max(...formData.value.items.map(i => i.sort_order || 0)) : -1
  let nextSortOrder = maxSortOrder + 1
  
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
  
  addItemDialogVisible.value = false
  ElMessage.success(`成功添加 ${selectedApiIds.value.length + selectedFlowIds.value.length} 个项目`)
  
  // 清空选择
  selectedApiIds.value = []
  selectedFlowIds.value = []
}

const removeItem = (index: number) => {
  formData.value.items?.splice(index, 1)
  // 如果删除后当前页没有数据了，自动跳转到前一页
  if (formData.value.items && paginatedFormItems.value.length === 0 && formItemsPage.value > 1) {
    formItemsPage.value--
  }
}

// 通过行数据删除任务项（用于分页场景）
const removeItemById = (row: { item_type: string; item_id: number }) => {
  const index = formData.value.items?.findIndex(
    item => item.item_type === row.item_type && item.item_id === row.item_id
  )
  if (index !== undefined && index !== -1) {
    removeItem(index)
  }
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
    // 重置任务项分页
    formItemsPage.value = 1
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.filter-left > * {
  margin: 0;
}

.filter-right {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;
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
  padding-right: 30px;
}

/* 任务项列表弹框关闭按钮样式 - 白色背景显示深色关闭按钮 */
.items-dialog-centered :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #909399;
  font-size: 20px;
}

.items-dialog-centered :deep(.el-dialog__headerbtn:hover .el-dialog__close) {
  color: #409eff;
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

/* 限制下拉列表高度，每页显示约10条记录 */
:deep(.api-select-dropdown) {
  max-height: 300px;
}

:deep(.api-select-dropdown .el-select-dropdown__list) {
  max-height: 300px;
}

/* 全选且数量多时，隐藏下拉列表的选项 */
:deep(.api-select-dropdown-empty .el-select-dropdown__list) {
  max-height: 100px;
  padding: 0;
}

:deep(.api-select-dropdown-empty .el-select-dropdown__item) {
  display: none !important;
}

/* 删除按钮去掉白色背景和立体感 */
.delete-btn-no-bg {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 4px 8px !important;
}

.delete-btn-no-bg:hover,
.delete-btn-no-bg:focus,
.delete-btn-no-bg:active {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

:deep(.el-table) .delete-btn-no-bg {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.el-table) .delete-btn-no-bg:hover,
:deep(.el-table) .delete-btn-no-bg:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

/* 执行对话框样式 */
.execute-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  margin: 0;
  border-bottom: 1px solid #f0f0f0;
}

.execute-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.execute-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 20px;
  border-top: 1px solid #f0f0f0;
}

.execute-dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.execute-dialog-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.execute-dialog-title-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.execute-dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.execute-dialog-desc {
  font-size: 13px;
  color: #909399;
}

.execute-dialog-content {
  padding: 20px 24px;
}

.execute-section {
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
}

.execute-section:last-child {
  margin-bottom: 0;
}

.execute-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.execute-section-body {
  padding: 16px;
}

/* 替换设置组 */
.replacement-group {
  background: white;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #ebeef5;
}

.replacement-group-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e4e7ed;
}

.replacement-group-title > span:first-child {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.replacement-hint {
  font-size: 12px;
  color: #909399;
}

/* 替换设置样式 */
.replacement-list {
  width: 100%;
}

.replacement-row {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px 8px;
  background: #f9fafc;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.replacement-row:hover {
  background: #f0f5ff;
}

.assertion-replacement-row {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 10px;
  padding: 8px 8px;
  background: #f9fafc;
  border-radius: 6px;
  transition: background-color 0.2s;
  flex-wrap: nowrap;
}

.assertion-replacement-row:hover {
  background: #f0f5ff;
}

.replacement-row:last-child,
.assertion-replacement-row:last-child {
  margin-bottom: 0;
}

/* 输入框样式 */
.replacement-key-input {
  width: 160px;
  flex-shrink: 0;
}

.replacement-value-input {
  flex: 1;
  min-width: 80px;
}

.assertion-type-select {
  width: 110px;
  flex-shrink: 0;
}

/* JSON路径的路径输入框、操作符下拉框宽度一致 */
.assertion-target-input {
  width: 100px;
  flex-shrink: 0;
}

/* 操作符下拉框与路径输入框宽度一致 */
.assertion-operator-select {
  width: 100px;
  flex-shrink: 0;
}

/* 操作按钮容器 */
.replacement-actions {
  display: flex;
  gap: 0;
  width: 70px;
  flex-shrink: 0;
  justify-content: flex-end;
}

/* 替换设置中的链接按钮 */
.replacement-row .el-button.is-link,
.assertion-replacement-row .el-button.is-link,
.replacement-actions .el-button.is-link {
  background: transparent !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 4px 4px !important;
  font-size: 13px;
}

.replacement-row .el-button.is-link:hover,
.replacement-row .el-button.is-link:focus,
.assertion-replacement-row .el-button.is-link:hover,
.assertion-replacement-row .el-button.is-link:focus,
.replacement-actions .el-button.is-link:hover,
.replacement-actions .el-button.is-link:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.replacement-actions .el-button.is-link.el-button--primary {
  color: #409eff !important;
}

.replacement-actions .el-button.is-link.el-button--primary:hover {
  color: #66b1ff !important;
}

.replacement-actions .el-button.is-link.el-button--danger {
  color: #f56c6c !important;
}

.replacement-actions .el-button.is-link.el-button--danger:hover {
  color: #f78989 !important;
}

/* 底部按钮 */
.execute-dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.execute-dialog-footer .el-button {
  min-width: 100px;
}

</style>

