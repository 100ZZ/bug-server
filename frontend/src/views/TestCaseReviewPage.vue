<template>
  <div class="testcase-review-page">
    <!-- 搜索和操作栏 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Document /></el-icon>
          用例评审
        </h2>
      </div>
      <div class="filter-row">
        <el-select
          v-model="searchProjectId"
          placeholder="选择项目"
          clearable
          @change="loadReviews"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1, width: '200px' }"
          :loading="!projects || projects.length === 0"
        >
          <el-option
            v-for="project in (projects || [])"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <el-input
          v-model="searchKeyword"
          placeholder="搜索评审名称"
          clearable
          @keyup.enter="loadReviews"
          style="width: 280px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadReviews">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button 
          type="primary" 
          style="margin-left: auto"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新建评审
        </el-button>
      </div>
    </el-card>

    <!-- 评审列表 -->
    <el-card class="table-card">
      <el-table
        :data="paginatedReviews || []"
        v-loading="loading"
        style="width: 100%"
        stripe
      >
        <el-table-column label="编号" width="80" type="index" :index="(index) => (currentPage - 1) * pageSize + index + 1" />
        <el-table-column label="项目" min-width="150">
          <template #default="{ row }">
            {{ row.project?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="迭代" min-width="150">
          <template #default="{ row }">
            {{ row.sprint?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="180" />
        <el-table-column label="发起人" min-width="120">
          <template #default="{ row }">
            {{ row.initiator?.display_name || row.initiator?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="发起时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.start_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_date" label="截止时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.end_date) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row)" size="small">
              {{ getStatusLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <!-- 第一行：编辑和删除 -->
              <div class="action-row">
                <el-button 
                  link 
                  type="primary" 
                  size="small"
                  @click="handleEdit(row)"
                >
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button 
                  link 
                  type="danger" 
                  size="small"
                  @click="handleDelete(row)"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
              <!-- 第二行：用例和评审 -->
              <div class="action-row">
                <el-button 
                  link 
                  type="primary" 
                  size="small"
                  @click="handleSelectTestCases(row)"
                >
                  <el-icon><Document /></el-icon>
                  用例
                </el-button>
                <el-button 
                  link 
                  type="primary" 
                  size="small"
                  @click="handleReview(row)"
                >
                  <el-icon><DocumentChecked /></el-icon>
                  评审
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
          :total="filteredReviews.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" width="600px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建评审' ? '创建新用例评审，设置评审名称、项目、迭代和时间范围' : '修改用例评审的配置信息' }}</span>
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
            @change="loadSprintsForProject"
          >
            <el-option
              v-for="project in (projects || [])"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="迭代">
          <el-select
            v-model="formData.sprint_id"
            placeholder="选择迭代"
            filterable
            clearable
            style="width: 100%"
            :disabled="!formData.project_id"
          >
                  <el-option
                    v-for="sprint in (sprints || [])"
                    :key="sprint.id"
                    :label="sprint.name"
                    :value="sprint.id"
                  />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="formData.name" placeholder="请输入评审名称" />
        </el-form-item>
        <el-form-item label="发起人" required>
          <el-select
            v-model="formData.initiator_id"
            placeholder="选择发起人"
            filterable
            style="width: 100%"
          >
                  <el-option
                    v-for="user in (users || [])"
                    :key="user.id"
                    :label="user.display_name || user.username"
                    :value="user.id"
                  />
          </el-select>
        </el-form-item>
        <el-form-item label="发起时间" required>
          <el-date-picker
            v-model="formData.start_date"
            type="date"
            placeholder="选择发起时间"
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

    <!-- 评审详情抽屉 -->
    <el-drawer
      v-model="reviewDetailDrawerVisible"
      direction="rtl"
      size="85%"
      :close-on-click-modal="false"
      class="review-detail-drawer"
    >
      <template #header>
        <div class="review-detail-header" v-if="currentReview">
          <div>
            <h3 style="margin: 0; font-size: 18px; font-weight: 600;">{{ currentReview.name || '评审详情' }}</h3>
            <div style="font-size: 13px; color: #909399; margin-top: 4px;">
              {{ currentReview.project?.name || '' }} | {{ currentReview.sprint?.name || '无迭代' }}
            </div>
          </div>
        </div>
      </template>

      <div class="review-detail-content" v-if="currentReview">
        <!-- 评审基本信息 -->
        <el-card class="review-info-card" style="margin-bottom: 16px;">
          <el-descriptions :column="4" border>
            <el-descriptions-item label="发起人">
              {{ currentReview.initiator?.display_name || currentReview.initiator?.username || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="发起时间">{{ formatDate(currentReview.start_date) }}</el-descriptions-item>
            <el-descriptions-item label="截止时间">{{ formatDate(currentReview.end_date) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(currentReview)" size="small">
                {{ getStatusLabel(currentReview) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 用例管理区域 -->
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>评审用例列表</span>
              <div>
                <el-button 
                  type="primary" 
                  size="small"
                  @click="handleShowAddTestCaseDialog"
                >
                  <el-icon><Plus /></el-icon>
                  添加用例
                </el-button>
              </div>
            </div>
          </template>

          <!-- 评审用例列表 -->
          <el-table
            :data="reviewItems || []"
            v-loading="reviewItemsLoading"
            stripe
            style="width: 100%"
          >
            <el-table-column label="用例编号" width="120">
              <template #default="{ row }">
                {{ row.testcase?.case_key || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="testcase.title" label="用例标题" min-width="200" show-overflow-tooltip />
            <el-table-column label="优先级" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getPriorityTag(row.testcase?.priority)">
                  {{ row.testcase?.priority || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="评审状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getReviewItemStatusType(row.status)" size="small">
                  {{ getReviewItemStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="评审人" width="120">
              <template #default="{ row }">
                {{ row.reviewer?.display_name || row.reviewer?.username || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="评审时间" width="160">
              <template #default="{ row }">
                {{ row.reviewed_at ? formatDateTime(row.reviewed_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column label="评审意见" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.comments || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <div class="table-actions">
                  <el-button 
                    link 
                    type="primary" 
                    size="small"
                    @click="handleReviewTestCase(row)"
                  >
                    <el-icon><EditPen /></el-icon>
                    评审
                  </el-button>
                  <el-button 
                    link 
                    type="danger" 
                    size="small"
                    @click="handleRemoveTestCase(row)"
                  >
                    <el-icon><Delete /></el-icon>
                    移除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-drawer>

    <!-- 添加用例子抽屉 -->
    <el-drawer
      v-model="showAddTestCaseDialog"
      direction="rtl"
      size="70%"
      :close-on-click-modal="false"
      class="add-testcase-drawer"
      :append-to-body="true"
      :modal="true"
    >
      <template #header>
        <div style="display: flex; align-items: center; gap: 8px;">
          <h3 style="margin: 0; font-size: 18px; font-weight: 600;">添加用例到评审</h3>
        </div>
      </template>
      <div style="height: 100%; display: flex; flex-direction: column;">
        <div style="margin-bottom: 16px; flex-shrink: 0;">
          <el-input
            v-model="testCaseSearchKeyword"
            placeholder="搜索用例标题"
            clearable
            @keyup.enter="loadAvailableTestCases"
            style="width: 300px; margin-right: 10px;"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="loadAvailableTestCases">搜索</el-button>
          <el-button @click="testCaseSearchKeyword = ''; loadAvailableTestCases()">重置</el-button>
        </div>
        <div style="flex: 1; overflow: hidden;">
          <el-table
            :data="availableTestCases || []"
            v-loading="availableTestCasesLoading"
            @selection-change="handleTestCaseSelectionChange"
            style="width: 100%"
            height="100%"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="case_key" label="用例编号" width="120" />
            <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
            <el-table-column label="优先级" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getPriorityTag(row.priority)">
                  {{ row.priority || '-' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ getTestCaseStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建人" width="120">
              <template #default="{ row }">
                {{ row.creator?.display_name || row.creator?.username || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e4e7ed; flex-shrink: 0; display: flex; justify-content: flex-end; gap: 10px;">
          <el-button @click="showAddTestCaseDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="handleAddTestCases"
            :disabled="selectedTestCases.length === 0"
          >
            添加选中用例 ({{ selectedTestCases.length }})
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- 评审用例对话框 -->
    <el-dialog
      v-model="showReviewTestCaseDialog"
      :title="currentReviewItem?.testcase?.title || '评审用例'"
      width="90%"
      :close-on-click-modal="false"
      class="review-testcase-dialog"
    >
      <div v-if="currentReviewItem">
        <!-- 用例详情区域（可编辑） -->
        <el-card style="margin-bottom: 16px;">
          <template #header>
            <span>用例详情</span>
          </template>
          <el-row :gutter="24">
            <el-col :span="18">
              <el-form :model="reviewTestCaseFormData" label-width="100px">
                <el-form-item label="标题">
                  <el-input v-model="reviewTestCaseFormData.title" />
                </el-form-item>
                <el-form-item label="前置条件">
                  <el-input 
                    v-model="reviewTestCaseFormData.precondition" 
                    type="textarea"
                    :rows="3"
                  />
                </el-form-item>
                <el-form-item label="步骤描述">
                  <div class="steps-table" v-if="reviewTestCaseFormData.steps && reviewTestCaseFormData.steps.length > 0">
                    <div class="steps-table-header">
                      <div class="header-cell header-cell-number">#</div>
                      <div class="header-cell header-cell-step">步骤</div>
                      <div class="header-cell header-cell-expected">预期</div>
                    </div>
                    <div 
                      v-for="(step, index) in reviewTestCaseFormData.steps" 
                      :key="index" 
                      class="steps-table-row"
                    >
                      <div class="table-cell table-cell-number">
                        <div class="step-number">{{ index + 1 }}</div>
                      </div>
                      <div class="table-cell table-cell-step">
                        <el-input 
                          v-model="step.description" 
                          type="textarea"
                          :rows="1"
                          :autosize="{ minRows: 1, maxRows: 10 }"
                          placeholder="请输入操作步骤"
                          class="step-input"
                        />
                      </div>
                      <div class="table-cell table-cell-expected">
                        <el-input 
                          v-model="step.expected_result" 
                          type="textarea"
                          :rows="1"
                          :autosize="{ minRows: 1, maxRows: 10 }"
                          placeholder="请输入预期结果"
                          class="step-input"
                        />
                      </div>
                    </div>
                  </div>
                </el-form-item>
              </el-form>
            </el-col>
            <el-col :span="6">
              <el-form :model="reviewTestCaseFormData" label-width="80px">
                <el-form-item label="项目">
                  {{ currentReviewItem.testcase?.project?.name || '-' }}
                </el-form-item>
                <el-form-item label="类型">
                  <el-select v-model="reviewTestCaseFormData.type" style="width: 100%">
                    <el-option label="功能" value="functional" />
                    <el-option label="非功能" value="non-functional" />
                  </el-select>
                </el-form-item>
                <el-form-item label="等级">
                  <el-select v-model="reviewTestCaseFormData.priority" style="width: 100%">
                    <el-option label="P0" value="P0" />
                    <el-option label="P1" value="P1" />
                    <el-option label="P2" value="P2" />
                    <el-option label="P3" value="P3" />
                    <el-option label="P4" value="P4" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-col>
          </el-row>
        </el-card>

        <!-- 评审结果区域 -->
        <el-card>
          <template #header>
            <span>评审结果</span>
          </template>
          <el-form :model="reviewResultFormData" label-width="100px">
            <el-form-item label="评审状态" required>
              <el-radio-group v-model="reviewResultFormData.status">
                <el-radio value="pending">待评审</el-radio>
                <el-radio value="approved">通过</el-radio>
                <el-radio value="rejected">不通过</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="评审意见">
              <el-input 
                v-model="reviewResultFormData.comments" 
                type="textarea"
                :rows="4"
                placeholder="请输入评审意见"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </div>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <el-button @click="showReviewTestCaseDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveReviewTestCase" :loading="savingReview">
            保存评审结果并更新用例
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 筛选用例抽屉（用例按钮） -->
    <el-drawer
      v-model="selectTestCasesDrawerVisible"
      title="筛选用例"
      direction="rtl"
      size="70%"
      :close-on-click-modal="true"
      class="select-testcases-drawer"
    >
      <div class="select-testcases-content" v-if="selectTestCasesReview">
        <!-- 左右分栏布局 -->
        <div class="select-testcases-layout">
          <!-- 左侧：目录树 -->
          <div class="select-testcases-sidebar" :style="{ width: selectTestCasesSidebarWidth + 'px' }">
            <el-card class="select-testcases-directory-card">
              <template #header>
                <span>用例详情树</span>
              </template>
              <div class="select-testcases-directory-header">
                <el-input
                  v-model="selectTestCasesDirectorySearchKeyword"
                  placeholder="搜索分组"
                  clearable
                  size="default"
                  @input="handleSelectTestCasesDirectorySearch"
                  class="select-testcases-directory-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              
              <div class="select-testcases-directory-tree-container" v-loading="selectTestCasesLoading">
                <el-tree
                  ref="selectTestCasesDirectoryTreeRef"
                  :data="selectTestCasesDirectoryTreeData"
                  :props="directoryTreeProps"
                  :default-expand-all="false"
                  :expand-on-click-node="true"
                  node-key="id"
                  class="select-testcases-directory-tree"
                  :filter-node-method="filterSelectTestCasesDirectoryNode"
                  :highlight-current="true"
                  @node-click="handleSelectTestCasesDirectoryNodeClick"
                >
                  <template #default="{ node, data }">
                    <div class="select-testcases-directory-node-wrapper">
                      <div class="select-testcases-directory-node-content">
                        <el-icon class="select-testcases-directory-folder-icon" :class="{ 'is-expanded': node.expanded, 'is-leaf': !data.children || data.children.length === 0 }">
                          <FolderOpened v-if="node.expanded" />
                          <Folder v-else />
                        </el-icon>
                        <span class="select-testcases-directory-node-label">{{ data.label }}</span>
                        <span v-if="data.count !== undefined && data.count !== null" class="select-testcases-directory-node-count">{{ data.count }}</span>
                      </div>
                    </div>
                  </template>
                </el-tree>
              </div>
            </el-card>
            
            <!-- 分割条 -->
            <div 
              class="select-testcases-resize-handle" 
              @mousedown="handleSelectTestCasesResizeStart"
              @dblclick="handleSelectTestCasesResizeReset"
              title="拖拽调整宽度，双击重置"
            ></div>
          </div>

          <!-- 右侧：用例列表 -->
          <div class="select-testcases-main" :style="{ width: `calc(100% - ${selectTestCasesSidebarWidth + 20}px)` }">
            <el-card class="select-testcases-list-card">
              <!-- 搜索和筛选 -->
              <div class="select-testcases-filters" style="margin-bottom: 16px;">
                <el-select v-model="selectTestCasesPriorityFilter" placeholder="用例等级" clearable style="width: 150px; margin-right: 10px;">
                  <el-option label="全部" value="" />
                  <el-option label="P0" value="P0" />
                  <el-option label="P1" value="P1" />
                  <el-option label="P2" value="P2" />
                  <el-option label="P3" value="P3" />
                  <el-option label="P4" value="P4" />
                </el-select>
                <el-input
                  v-model="selectTestCasesSearchKeyword"
                  placeholder="搜索用例名称"
                  clearable
                  @keyup.enter="handleSelectTestCasesSearch"
                  style="width: 300px; margin-right: 10px;"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-button @click="handleSelectTestCasesSearch">搜索</el-button>
                <el-button @click="selectTestCasesSearchKeyword = ''; handleSelectTestCasesSearch()">重置</el-button>
              </div>
              
              <!-- 用例列表 -->
              <div style="flex: 1; overflow: hidden; display: flex; flex-direction: column;">
                <el-table
                  ref="selectTestCasesTableRef"
                  :data="selectTestCasesPaginatedTestCases"
                  v-loading="selectTestCasesLoading"
                  @selection-change="handleSelectTestCasesSelectionChange"
                  stripe
                  style="width: 100%"
                  height="100%"
                  row-key="id"
                  :reserve-selection="true"
                >
                <el-table-column type="selection" width="55" align="center" />
                <el-table-column prop="case_key" label="用例" width="180" />
                <el-table-column prop="title" label="用例名称" min-width="300" show-overflow-tooltip />
                <el-table-column label="优先级" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getPriorityTag(row.priority)">
                      {{ row.priority || '-' }}
                    </el-tag>
                  </template>
                </el-table-column>
                </el-table>
              </div>
              
              <!-- 分页 -->
              <div style="margin-top: 16px; text-align: right; flex-shrink: 0;">
                <el-pagination
                  v-model:current-page="selectTestCasesCurrentPage"
                  v-model:page-size="selectTestCasesPageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  layout="prev, pager, next, sizes, jumper, ->, total"
                  :total="selectTestCasesFilteredTestCases.length"
                />
              </div>
            </el-card>
          </div>
        </div>
        
        <!-- 底部操作栏 -->
        <div class="select-testcases-footer">
          <div class="select-testcases-footer-left">
            <span>{{ selectTestCasesSelectedTestCaseIds.size }} 条用例已选</span>
            <el-button link type="primary" @click="handleClearSelectedTestCases">清空已选</el-button>
          </div>
          <div class="select-testcases-footer-right">
            <el-button @click="selectTestCasesDrawerVisible = false">取消</el-button>
            <el-button 
              type="primary" 
              @click="handleConfirmSelectTestCases"
              :disabled="selectTestCasesSelectedTestCaseIds.size === 0"
            >
              确定
            </el-button>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 评审抽屉（评审按钮） -->
    <el-drawer
      v-model="reviewDrawerVisible"
      direction="rtl"
      size="75%"
      :close-on-click-modal="true"
      class="review-drawer"
    >
      <template #header>
        <div class="review-drawer-header" v-if="reviewDrawerReview">
          <div>
            <h3 style="margin: 0; font-size: 18px; font-weight: 600;">{{ reviewDrawerReview.name || '评审' }}</h3>
            <div style="font-size: 13px; color: #909399; margin-top: 4px;">
              {{ reviewDrawerReview.project?.name || '' }} | {{ reviewDrawerReview.sprint?.name || '无迭代' }}
            </div>
          </div>
        </div>
      </template>

      <div class="review-drawer-content" v-if="reviewDrawerReview">
        <!-- 进度信息 -->
        <el-card class="review-progress-card" style="margin-bottom: 16px;">
          <div class="review-progress-info">
            <div class="review-progress-item">
              <span class="review-progress-label">评审进度：</span>
              <el-progress 
                :percentage="reviewDrawerProgressPercentage" 
                :status="reviewDrawerProgressStatus"
                :stroke-width="20"
                style="flex: 1; margin: 0 20px;"
              />
              <span class="review-progress-text">{{ reviewDrawerProgressText }}</span>
            </div>
            <div class="review-progress-stats">
              <span>已评用例 {{ reviewDrawerReviewedCount }}/{{ reviewDrawerTotalCount }}</span>
              <span style="margin-left: 20px;">已评人员 {{ reviewDrawerReviewedReviewersCount }}/{{ reviewDrawerTotalReviewersCount }}</span>
            </div>
          </div>
        </el-card>

        <!-- 左右分栏：用例详情树和列表 -->
        <div class="review-drawer-layout">
          <!-- 左侧：用例详情树 -->
          <div class="review-drawer-sidebar" :style="{ width: reviewDrawerSidebarWidth + 'px' }">
            <el-card class="review-drawer-tree-card">
              <template #header>
                <span>用例详情树</span>
              </template>
              <div class="review-drawer-tree-container" v-loading="reviewDrawerReviewItemsLoading">
                <el-tree
                  :data="reviewDrawerTreeData"
                  :props="{ children: 'children', label: 'label' }"
                  :default-expand-all="false"
                  node-key="id"
                  class="review-drawer-tree"
                  :highlight-current="true"
                  :current-node-key="reviewDrawerSelectedGroupPath ? `group-${reviewDrawerSelectedGroupPath}` : ''"
                  @node-click="handleReviewDrawerTreeNodeClick"
                >
                  <template #default="{ node, data }">
                    <div class="review-drawer-tree-node">
                      <el-icon class="review-drawer-tree-icon" :class="{ 'is-leaf': data.isLeaf }">
                        <FolderOpened v-if="!data.isLeaf && node.expanded" />
                        <Folder v-else-if="!data.isLeaf" />
                        <Document v-else />
                      </el-icon>
                      <span class="review-drawer-tree-label">{{ data.label }}</span>
                      <el-tag 
                        v-if="data.reviewStatus" 
                        :type="getReviewItemStatusType(data.reviewStatus)" 
                        size="small"
                        style="margin-left: 8px;"
                      >
                        {{ getReviewItemStatusLabel(data.reviewStatus) }}
                      </el-tag>
                    </div>
                  </template>
                </el-tree>
              </div>
            </el-card>
            
            <!-- 分割条 -->
            <div 
              class="review-drawer-resize-handle" 
              @mousedown="handleReviewDrawerResizeStart"
              @dblclick="handleReviewDrawerResizeReset"
              title="拖拽调整宽度，双击重置"
            ></div>
          </div>

          <!-- 右侧：用例列表 -->
          <div class="review-drawer-main" :style="{ width: `calc(100% - ${reviewDrawerSidebarWidth + 20}px)` }">
            <el-card class="review-drawer-list-card">
              <!-- 搜索和筛选 -->
              <div class="review-drawer-list-filters" style="margin-bottom: 16px;">
                <el-select v-model="reviewDrawerPriorityFilter" placeholder="用例等级" clearable style="width: 150px; margin-right: 10px;">
                  <el-option label="全部" value="" />
                  <el-option label="P0" value="P0" />
                  <el-option label="P1" value="P1" />
                  <el-option label="P2" value="P2" />
                  <el-option label="P3" value="P3" />
                  <el-option label="P4" value="P4" />
                </el-select>
                <el-select v-model="reviewDrawerStatusFilter" placeholder="评审状态" clearable style="width: 120px; margin-right: 10px;">
                  <el-option label="全部" value="" />
                  <el-option label="待评审" value="pending" />
                  <el-option label="通过" value="approved" />
                  <el-option label="不通过" value="rejected" />
                </el-select>
                <el-input
                  v-model="reviewDrawerSearchKeyword"
                  placeholder="输入ID或标题..."
                  clearable
                  style="width: 200px; margin-right: 10px;"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
                <el-switch
                  v-model="reviewDrawerOnlyCommented"
                  active-text="只显示有评论用例"
                  style="margin-right: 10px;"
                />
              </div>
              
              <!-- 用例列表表格 -->
              <div style="flex: 1; overflow: hidden; display: flex; flex-direction: column;">
                <el-table
                  :data="reviewDrawerPaginatedItems"
                  v-loading="reviewDrawerReviewItemsLoading"
                  stripe
                  style="width: 100%"
                  height="100%"
                  @row-click="handleReviewDrawerTableRowClick"
                  :row-style="{ cursor: 'pointer' }"
                >
                <el-table-column label="编号" width="180">
                  <template #default="{ row }">
                    {{ row.testcase?.case_key || '-' }}
                  </template>
                </el-table-column>
                <el-table-column prop="testcase.title" label="用例名称" min-width="300" show-overflow-tooltip />
                <el-table-column label="等级" width="100">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getPriorityTag(row.testcase?.priority)">
                      {{ row.testcase?.priority || '-' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="评审状态" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getReviewItemStatusType(row.status)" size="small">
                      {{ getReviewItemStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                </el-table>
              </div>
              
              <!-- 分页 -->
              <div style="margin-top: 16px; text-align: right; flex-shrink: 0;">
                <el-pagination
                  v-model:current-page="reviewDrawerCurrentPage"
                  v-model:page-size="reviewDrawerPageSize"
                  :page-sizes="[10, 20, 50, 100]"
                  layout="prev, pager, next, sizes, jumper, ->, total"
                  :total="reviewDrawerFilteredItems.length"
                />
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </el-drawer>

    <!-- 评审用例详情子抽屉 -->
    <el-drawer
      v-model="reviewDrawerTestCaseDetailVisible"
      direction="rtl"
      size="60%"
      :close-on-click-modal="true"
      class="review-testcase-detail-drawer"
      :append-to-body="true"
    >
      <template #header>
        <div style="display: flex; align-items: center; gap: 8px;">
          <h3 style="margin: 0; font-size: 18px; font-weight: 600;">
            {{ reviewDrawerCurrentTestCaseItem?.testcase?.title || '用例详情' }}
          </h3>
        </div>
      </template>
      
      <div v-if="reviewDrawerCurrentTestCaseItem" class="review-testcase-detail-content">
        <el-row :gutter="24" class="testcase-drawer-row">
          <!-- 左侧：标题、前置条件和步骤 -->
          <el-col :span="18" class="drawer-left-col">
            <!-- 标题 -->
            <div class="section-block" style="margin-bottom: 24px;">
              <div class="section-title">标题</div>
              <el-input v-model="reviewDrawerTestCaseFormData.title" placeholder="请输入用例标题" />
            </div>
            
            <!-- 前置条件 -->
            <div class="section-block" style="margin-top: 0;">
              <div class="section-title">前置条件</div>
              <el-input 
                v-model="reviewDrawerTestCaseFormData.precondition" 
                type="textarea" 
                :rows="4" 
                placeholder="点击此处添加前置条件（可选）" 
                class="precondition-input"
              />
            </div>
            
            <!-- 步骤描述 -->
            <div class="section-block" style="margin-top: 24px;">
              <div class="section-title">步骤描述</div>
              
              <!-- 步骤列表 -->
              <div class="steps-table" v-if="reviewDrawerTestCaseFormData.steps && reviewDrawerTestCaseFormData.steps.length > 0">
                <!-- 表头 -->
                <div class="steps-table-header">
                  <div class="header-cell header-cell-number">#</div>
                  <div class="header-cell header-cell-step">步骤</div>
                  <div class="header-cell header-cell-expected">预期</div>
                </div>
                
                <!-- 表格内容 -->
                <div 
                  v-for="(step, index) in reviewDrawerTestCaseFormData.steps" 
                  :key="index" 
                  class="steps-table-row"
                >
                  <div class="table-cell table-cell-number">
                    <div class="step-number">{{ index + 1 }}</div>
                  </div>
                  <div class="table-cell table-cell-step">
                    <el-input 
                      v-model="step.description" 
                      type="textarea"
                      :rows="1"
                      :autosize="{ minRows: 1, maxRows: 10 }"
                      placeholder="请输入操作步骤"
                      class="step-input"
                    />
                  </div>
                  <div class="table-cell table-cell-expected">
                    <el-input 
                      v-model="step.expected_result" 
                      type="textarea"
                      :rows="1"
                      :autosize="{ minRows: 1, maxRows: 10 }"
                      placeholder="请输入预期结果"
                      class="step-input"
                    />
                  </div>
                </div>
              </div>
              
              <el-empty v-else description="暂无步骤，请添加步骤" :image-size="80" style="margin: 20px 0;" />
            </div>
          </el-col>
          
          <!-- 右侧：项目、类型、等级和评审结果 -->
          <el-col :span="6" class="drawer-right-col">
            <div class="right-section">
              <!-- 基本信息 -->
              <div class="section-block">
                <el-form :model="reviewDrawerTestCaseFormData" label-position="top" class="right-form">
                  <el-form-item label="项目">
                    {{ reviewDrawerCurrentTestCaseItem.testcase?.project?.name || '-' }}
                  </el-form-item>
                  <el-form-item label="类型">
                    <el-select v-model="reviewDrawerTestCaseFormData.type" style="width: 100%">
                      <el-option label="功能" value="functional" />
                      <el-option label="非功能" value="non-functional" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="等级">
                    <el-select v-model="reviewDrawerTestCaseFormData.priority" style="width: 100%">
                      <el-option label="P0" value="P0" />
                      <el-option label="P1" value="P1" />
                      <el-option label="P2" value="P2" />
                      <el-option label="P3" value="P3" />
                      <el-option label="P4" value="P4" />
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>
              
              <!-- 评审结果区域 -->
              <div class="section-block" style="margin-top: 24px;">
                <el-form :model="reviewDrawerReviewResultFormData" label-position="top" class="right-form">
                  <el-form-item label="评审状态" style="margin-bottom: 16px;">
                    <el-radio-group v-model="reviewDrawerReviewResultFormData.status">
                      <el-radio value="pending">待评审</el-radio>
                      <el-radio value="approved">通过</el-radio>
                      <el-radio value="rejected">不通过</el-radio>
                    </el-radio-group>
                  </el-form-item>
                  <el-form-item label="评审建议">
                    <el-input 
                      v-model="reviewDrawerReviewResultFormData.comments" 
                      type="textarea"
                      :rows="4"
                      placeholder="请输入评审建议"
                    />
                  </el-form-item>
                </el-form>
              </div>
            </div>
          </el-col>
        </el-row>

      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="reviewDrawerTestCaseDetailVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveReviewDrawerTestCase" :loading="reviewDrawerSavingReview">
            保存
          </el-button>
          <el-button type="primary" @click="handleSaveAndNextReviewDrawerTestCase" :loading="reviewDrawerSavingReview">
            保存并下一个
          </el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, Document, DocumentChecked, Folder, FolderOpened } from '@element-plus/icons-vue'
import * as reviewApi from '../api/testcase_reviews'
import * as projectApi from '../api/projects'
import * as sprintApi from '../api/sprints'
import * as userApi from '../api/users'
import * as testcaseApi from '../api/testcases'
import type { TestCaseReview, Project, Sprint, User, TestCaseReviewItem, TestCase } from '../api/types'
import { usePermissions } from '../composables/usePermissions'
import { useProjectContext } from '../composables/useProjectContext'
import dayjs from 'dayjs'

const { canCreate, canUpdate, canDelete, getCurrentUser } = usePermissions()
const { getCurrentProjectId, hasProjectSelected, onProjectChanged, ensureInitialized } = useProjectContext()

const reviews = ref<TestCaseReview[]>([])
const projects = ref<Project[]>([])
const sprints = ref<Sprint[]>([])
const users = ref<User[]>([])
const searchKeyword = ref('')
const searchProjectId = ref<number | undefined>(undefined)
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建评审')
const editingId = ref<number>()

const formData = reactive({
  project_id: undefined as number | undefined,
  sprint_id: undefined as number | undefined,
  name: '',
  initiator_id: undefined as number | undefined,
  start_date: '',
  end_date: ''
})

// 评审详情相关
const reviewDetailDrawerVisible = ref(false)
const currentReview = ref<TestCaseReview | null>(null)
const reviewItems = ref<TestCaseReviewItem[]>([])
const reviewItemsLoading = ref(false)

// 添加用例对话框
const showAddTestCaseDialog = ref(false)
const availableTestCases = ref<TestCase[]>([])
const availableTestCasesLoading = ref(false)
const testCaseSearchKeyword = ref('')
const selectedTestCases = ref<TestCase[]>([])

// 评审用例对话框
const showReviewTestCaseDialog = ref(false)
const currentReviewItem = ref<TestCaseReviewItem | null>(null)
const savingReview = ref(false)
const reviewTestCaseFormData = reactive({
  title: '',
  precondition: '',
  steps: [] as Array<{ description: string; expected_result: string }>,
  type: 'functional',
  priority: 'P2'
})
const reviewResultFormData = reactive({
  status: 'pending' as 'pending' | 'approved' | 'rejected',
  comments: ''
})

// 筛选用例抽屉（用例按钮）
const selectTestCasesDrawerVisible = ref(false)
const selectTestCasesReview = ref<TestCaseReview | null>(null)
const selectTestCasesDirectoryTreeRef = ref()
const selectTestCasesTableRef = ref()
const selectTestCasesDirectorySearchKeyword = ref('')
const selectTestCasesSearchKeyword = ref('')
const selectTestCasesSelectedDirectoryPath = ref<string | null>(null)
const selectTestCasesAllTestCases = ref<TestCase[]>([])
const selectTestCasesLoading = ref(false)
const selectTestCasesSelectedTestCases = ref<TestCase[]>([])
const selectTestCasesSelectedTestCaseIds = ref<Set<number>>(new Set())

// 目录树节点接口
interface DirectoryTreeNode {
  id: string
  label: string
  path: string | null
  count: number
  children?: DirectoryTreeNode[]
}

const directoryTreeProps = {
  children: 'children',
  label: 'label'
}

// 评审抽屉（评审按钮）
const reviewDrawerVisible = ref(false)
const reviewDrawerReview = ref<TestCaseReview | null>(null)
const reviewDrawerReviewItems = ref<TestCaseReviewItem[]>([])
const reviewDrawerReviewItemsLoading = ref(false)
const reviewDrawerSelectedTestCaseId = ref<number | null>(null)
const reviewDrawerTestCaseDetailVisible = ref(false)

const handleReset = () => {
  searchKeyword.value = ''
  if (!hasProjectSelected.value) {
    searchProjectId.value = undefined
  }
  currentPage.value = 1
  loadReviews()
}

const loadReviews = async () => {
  if (!isMounted) return
  loading.value = true
  try {
    const params: any = { limit: 1000 }
    // 优先使用当前选择的项目，否则使用搜索框中的项目
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
      searchProjectId.value = getCurrentProjectId.value
    } else if (searchProjectId.value) {
      params.project_id = searchProjectId.value
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    reviews.value = await reviewApi.getTestCaseReviews(params)
  } catch (error) {
    if (isMounted) {
      ElMessage.error('加载用例评审失败')
    }
  } finally {
    if (isMounted) {
      loading.value = false
    }
  }
}

const loadProjects = async () => {
  try {
    projects.value = await projectApi.getProjects({ limit: 1000 })
  } catch (error) {
    console.error('Failed to load projects:', error)
  }
}

const loadSprintsForProject = async () => {
  if (!formData.project_id) {
    sprints.value = []
    return
  }
  try {
    sprints.value = await sprintApi.getSprints({ project_id: formData.project_id, limit: 1000 })
  } catch (error) {
    console.error('Failed to load sprints:', error)
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
  dialogTitle.value = '新建评审'
  Object.assign(formData, {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : undefined,
    sprint_id: undefined,
    name: '',
    initiator_id: undefined,
    start_date: dayjs().format('YYYY-MM-DD'),
    end_date: dayjs().add(7, 'day').format('YYYY-MM-DD')
  })
  if (formData.project_id) {
    loadSprintsForProject()
  }
  dialogVisible.value = true
}

const handleEdit = (row: TestCaseReview) => {
  editingId.value = row.id
  dialogTitle.value = '编辑评审'
  const projectId = hasProjectSelected.value && getCurrentProjectId.value 
    ? getCurrentProjectId.value 
    : row.project_id
  Object.assign(formData, {
    project_id: projectId,
    sprint_id: row.sprint_id || undefined,
    name: row.name,
    initiator_id: row.initiator_id,
    start_date: row.start_date,
    end_date: row.end_date
  })
  if (formData.project_id) {
    loadSprintsForProject()
  }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.project_id || !formData.name || !formData.initiator_id || !formData.start_date || !formData.end_date) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  if (dayjs(formData.end_date).isBefore(dayjs(formData.start_date))) {
    ElMessage.warning('截止时间不能早于发起时间')
    return
  }

  try {
    const data: any = {
      project_id: formData.project_id,
      name: formData.name,
      initiator_id: formData.initiator_id,
      start_date: formData.start_date,
      end_date: formData.end_date
    }
    if (formData.sprint_id) {
      data.sprint_id = formData.sprint_id
    }
    
    if (editingId.value) {
      await reviewApi.updateTestCaseReview(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await reviewApi.createTestCaseReview(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadReviews()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
  }
}

const handleDelete = async (row: TestCaseReview) => {
  try {
    await ElMessageBox.confirm('确定删除此用例评审吗？', '提示', { type: 'warning' })
    await reviewApi.deleteTestCaseReview(row.id)
    ElMessage.success('删除成功')
    loadReviews()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const handleReview = async (row: TestCaseReview) => {
  await handleReviewDrawer(row)
}

const loadReviewItems = async (reviewId: number) => {
  reviewItemsLoading.value = true
  try {
    reviewItems.value = await reviewApi.getReviewItems(reviewId)
  } catch (error: any) {
    ElMessage.error('加载评审用例列表失败')
  } finally {
    reviewItemsLoading.value = false
  }
}

const loadAvailableTestCases = async () => {
  if (!currentReview.value) return
  availableTestCasesLoading.value = true
  try {
    const params: any = {
      project_id: currentReview.value.project_id,
      limit: 1000
    }
    if (testCaseSearchKeyword.value) {
      params.search = testCaseSearchKeyword.value
    }
    const allTestCases = await testcaseApi.getTestCases(params)
    // 过滤掉已经添加到评审中的用例
    const existingTestCaseIds = new Set(reviewItems.value.map(item => item.testcase_id))
    availableTestCases.value = allTestCases.filter(tc => !existingTestCaseIds.has(tc.id))
  } catch (error: any) {
    ElMessage.error('加载可用用例列表失败')
  } finally {
    availableTestCasesLoading.value = false
  }
}

const handleTestCaseSelectionChange = (selection: TestCase[]) => {
  selectedTestCases.value = selection
}

const handleAddTestCases = async () => {
  if (!currentReview.value || selectedTestCases.value.length === 0) return
  
  try {
    for (const testcase of selectedTestCases.value) {
      await reviewApi.addReviewItem(currentReview.value.id, {
        review_id: currentReview.value.id,
        testcase_id: testcase.id
      })
    }
    ElMessage.success(`成功添加 ${selectedTestCases.value.length} 个用例`)
    selectedTestCases.value = []
    showAddTestCaseDialog.value = false
    await loadReviewItems(currentReview.value.id)
    await loadAvailableTestCases()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '添加用例失败'
    ElMessage.error(errorMessage)
  }
}

const handleReviewTestCase = async (item: TestCaseReviewItem) => {
  if (!item.testcase) return
  
  currentReviewItem.value = item
  
  // 初始化用例表单数据
  Object.assign(reviewTestCaseFormData, {
    title: item.testcase.title || '',
    precondition: item.testcase.precondition || '',
    steps: item.testcase.steps ? JSON.parse(JSON.stringify(item.testcase.steps)) : [],
    type: item.testcase.type || 'functional',
    priority: item.testcase.priority || 'P2'
  })
  
  // 初始化评审结果表单数据
  Object.assign(reviewResultFormData, {
    status: item.status || 'pending',
    comments: item.comments || ''
  })
  
  showReviewTestCaseDialog.value = true
}

const handleSaveReviewTestCase = async () => {
  if (!currentReviewItem.value || !currentReview.value) return
  
  savingReview.value = true
  try {
    // 更新用例
    await testcaseApi.updateTestCase(currentReviewItem.value.testcase_id, {
      title: reviewTestCaseFormData.title,
      precondition: reviewTestCaseFormData.precondition,
      steps: reviewTestCaseFormData.steps,
      type: reviewTestCaseFormData.type,
      priority: reviewTestCaseFormData.priority
    })
    
    // 更新评审结果
    await reviewApi.updateReviewItem(
      currentReview.value.id,
      currentReviewItem.value.id,
      {
        status: reviewResultFormData.status,
        comments: reviewResultFormData.comments,
        reviewer_id: getCurrentUser()?.id
      }
    )
    
    ElMessage.success('评审结果已保存')
    showReviewTestCaseDialog.value = false
    await loadReviewItems(currentReview.value.id)
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
  } finally {
    savingReview.value = false
  }
}

const handleRemoveTestCase = async (item: TestCaseReviewItem) => {
  if (!currentReview.value) return
  
  try {
    await ElMessageBox.confirm('确定从评审中移除此用例吗？', '提示', { type: 'warning' })
    await reviewApi.deleteReviewItem(currentReview.value.id, item.id)
    ElMessage.success('用例已移除')
    await loadReviewItems(currentReview.value.id)
    await loadAvailableTestCases()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '移除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}

const formatDateTime = (dateStr: string | null | undefined) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

const getReviewItemStatusLabel = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: '待评审',
    approved: '通过',
    rejected: '不通过'
  }
  return statusMap[status] || status
}

const getReviewItemStatusType = (status: string): string => {
  const typeMap: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return typeMap[status] || ''
}

const getPriorityTag = (priority: string): string => {
  const tagMap: Record<string, string> = {
    'P0': 'danger',
    'P1': 'warning',
    'P2': 'info',
    'P3': '',
    'P4': ''
  }
  return tagMap[priority] || ''
}

const getTestCaseStatusLabel = (status: string): string => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    active: '激活',
    deprecated: '已废弃'
  }
  return statusMap[status] || status
}

const handleShowAddTestCaseDialog = async () => {
  showAddTestCaseDialog.value = true
  testCaseSearchKeyword.value = ''
  selectedTestCases.value = []
  await loadAvailableTestCases()
}

const getReviewStatus = (review: TestCaseReview | null): 'not_started' | 'in_progress' | 'ended' => {
  if (!review || !review.start_date || !review.end_date) {
    return 'not_started'
  }
  
  const now = dayjs()
  const startDate = dayjs(review.start_date)
  const endDate = dayjs(review.end_date)
  
  if (now.isBefore(startDate)) {
    return 'not_started'
  } else if (now.isSameOrAfter(startDate) && now.isSameOrBefore(endDate)) {
    return 'in_progress'
  } else {
    return 'ended'
  }
}

const getStatusLabel = (review: TestCaseReview | null): string => {
  if (!review) return '-'
  const status = getReviewStatus(review)
  const statusMap = {
    not_started: '未开始',
    in_progress: '进行中',
    ended: '已结束'
  }
  return statusMap[status]
}

const getStatusType = (review: TestCaseReview | null): string => {
  if (!review) return ''
  const status = getReviewStatus(review)
  const typeMap = {
    not_started: 'info',
    in_progress: 'success',
    ended: ''
  }
  return typeMap[status]
}

const filteredReviews = computed(() => {
  if (!reviews.value || !Array.isArray(reviews.value)) {
    return []
  }
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) {
    return reviews.value
  }
  return reviews.value.filter((review) => {
    const name = (review.name || '').toLowerCase()
    const projectName = (review.project?.name || '').toLowerCase()
    const sprintName = (review.sprint?.name || '').toLowerCase()
    return name.includes(keyword) || projectName.includes(keyword) || sprintName.includes(keyword)
  })
})

const paginatedReviews = computed(() => {
  if (!filteredReviews.value || !Array.isArray(filteredReviews.value)) {
    return []
  }
  const start = (currentPage.value - 1) * pageSize.value
  return filteredReviews.value.slice(start, start + pageSize.value)
})

let cleanupProjectChanged: (() => void) | null = null
let isMounted = false

onMounted(async () => {
  isMounted = true
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 使用 nextTick 确保 DOM 完全渲染后再执行
  await nextTick()
  loadProjects()
  loadUsers()
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    searchProjectId.value = getCurrentProjectId.value
  }
  // 延迟加载数据，避免与路由切换冲突
  setTimeout(() => {
    if (isMounted) {
      loadReviews()
    }
  }, 0)
  cleanupProjectChanged = onProjectChanged(() => {
    if (!isMounted) return
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      searchProjectId.value = getCurrentProjectId.value
    } else {
      searchProjectId.value = undefined
    }
    loadReviews()
  })
})

onUnmounted(() => {
  isMounted = false
  if (cleanupProjectChanged) {
    cleanupProjectChanged()
  }
})

watch(() => getCurrentProjectId.value, (newVal, oldVal) => {
  if (!isMounted) return
  // 避免初始化时重复加载
  if (newVal === oldVal) return
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    searchProjectId.value = getCurrentProjectId.value
  } else {
    searchProjectId.value = undefined
  }
  loadReviews()
}, { immediate: false })

watch(reviewDetailDrawerVisible, (visible) => {
  if (visible && currentReview.value) {
    loadReviewItems(currentReview.value.id)
  }
})

watch(showAddTestCaseDialog, (visible) => {
  if (visible && currentReview.value) {
    loadAvailableTestCases()
  }
})

// 监听分页数据变化或分组切换，恢复选中状态
const restoreSelectedTestCases = () => {
  nextTick(() => {
    if (selectTestCasesTableRef.value && selectTestCasesSelectedTestCaseIds.value.size > 0) {
      // 清空当前选中
      selectTestCasesTableRef.value.clearSelection()
      // 根据保存的ID集合恢复选中状态
      selectTestCasesPaginatedTestCases.value.forEach((row: TestCase) => {
        if (selectTestCasesSelectedTestCaseIds.value.has(row.id)) {
          selectTestCasesTableRef.value.toggleRowSelection(row, true)
        }
      })
    }
  })
}

watch(() => selectTestCasesPaginatedTestCases.value, () => {
  restoreSelectedTestCases()
}, { deep: true })

watch(() => selectTestCasesSelectedDirectoryPath.value, () => {
  // 切换分组时，重置到第一页并恢复选中状态
  selectTestCasesCurrentPage.value = 1
  restoreSelectedTestCases()
})

// 筛选用例抽屉相关函数
const selectTestCasesSidebarWidth = ref(280)
const selectTestCasesIsResizing = ref(false)
const selectTestCasesResizeStartX = ref(0)
const selectTestCasesResizeStartWidth = ref(0)
const selectTestCasesCurrentPage = ref(1)
const selectTestCasesPageSize = ref(10)
const selectTestCasesPriorityFilter = ref('')

const handleSelectTestCasesResizeStart = (e: MouseEvent) => {
  selectTestCasesIsResizing.value = true
  selectTestCasesResizeStartX.value = e.clientX
  selectTestCasesResizeStartWidth.value = selectTestCasesSidebarWidth.value
  document.addEventListener('mousemove', handleSelectTestCasesResizeMove)
  document.addEventListener('mouseup', handleSelectTestCasesResizeEnd)
  e.preventDefault()
}

const handleSelectTestCasesResizeMove = (e: MouseEvent) => {
  if (!selectTestCasesIsResizing.value) return
  const diff = e.clientX - selectTestCasesResizeStartX.value
  const newWidth = selectTestCasesResizeStartWidth.value + diff
  selectTestCasesSidebarWidth.value = Math.max(200, Math.min(600, newWidth))
}

const handleSelectTestCasesResizeEnd = () => {
  selectTestCasesIsResizing.value = false
  document.removeEventListener('mousemove', handleSelectTestCasesResizeMove)
  document.removeEventListener('mouseup', handleSelectTestCasesResizeEnd)
}

const handleSelectTestCasesResizeReset = () => {
  selectTestCasesSidebarWidth.value = 280
}

// 构建目录树（从用例的module字段提取）
const buildSelectTestCasesDirectoryTree = (testcases: TestCase[]): DirectoryTreeNode[] => {
  const directoryMap = new Map<string, { count: number, pathParts: string[] }>()
  
  testcases.forEach(testcase => {
    const modulePath = testcase.module || ''
    if (!modulePath) return
    
    const pathParts = modulePath.split('/').filter(p => p.trim())
    let currentPath = ''
    pathParts.forEach((part, index) => {
      currentPath = currentPath ? `${currentPath}/${part}` : part
      if (!directoryMap.has(currentPath)) {
        directoryMap.set(currentPath, { count: 0, pathParts: pathParts.slice(0, index + 1) })
      }
      if (index === pathParts.length - 1 && !testcase.title?.startsWith('[目录占位]')) {
        directoryMap.get(currentPath)!.count++
      }
    })
  })
  
  const rootNodes: DirectoryTreeNode[] = []
  const nodeMap = new Map<string, DirectoryTreeNode>()
  
  Array.from(directoryMap.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .forEach(([path, { count, pathParts }]) => {
      if (!path) return
      
      let currentPath = ''
      let parent: DirectoryTreeNode | null = null
      
      pathParts.forEach((part, index) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part
        
        if (!nodeMap.has(currentPath)) {
          const node: DirectoryTreeNode = {
            id: `dir-${currentPath}`,
            label: part,
            path: currentPath,
            count: 0,
            children: []
          }
          nodeMap.set(currentPath, node)
          
          if (parent) {
            if (!parent.children) parent.children = []
            parent.children.push(node)
          } else {
            rootNodes.push(node)
          }
        }
        
        if (index === pathParts.length - 1) {
          const node = nodeMap.get(currentPath)!
          node.count += count
        }
        
        parent = nodeMap.get(currentPath)!
      })
    })
  
  const calculateLeafNodesTotalCount = (node: DirectoryTreeNode): number => {
    if (!node.children || node.children.length === 0) {
      return node.count || 0
    }
    let total = 0
    node.children.forEach(child => {
      total += calculateLeafNodesTotalCount(child)
    })
    return total
  }
  
  const updateCounts = (nodes: DirectoryTreeNode[]) => {
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        updateCounts(node.children)
        node.count = calculateLeafNodesTotalCount(node)
      }
    })
  }
  
  if (rootNodes.length > 0) {
    updateCounts(rootNodes)
  }
  
  return rootNodes
}

const selectTestCasesDirectoryTreeData = computed(() => {
  // 使用所有用例构建分组树（与用例详情页一致）
  return buildSelectTestCasesDirectoryTree(selectTestCasesAllTestCasesForTree.value)
})

const handleSelectTestCasesDirectorySearch = () => {
  nextTick(() => {
    if (selectTestCasesDirectoryTreeRef.value) {
      selectTestCasesDirectoryTreeRef.value.filter(selectTestCasesDirectorySearchKeyword.value)
    }
  })
}

const filterSelectTestCasesDirectoryNode = (value: string, data: DirectoryTreeNode) => {
  if (!value) return true
  return data.label.toLowerCase().includes(value.toLowerCase())
}

const handleSelectTestCasesDirectoryNodeClick = (data: DirectoryTreeNode) => {
  selectTestCasesSelectedDirectoryPath.value = data.path
  selectTestCasesCurrentPage.value = 1
}

const selectTestCasesFilteredTestCases = computed(() => {
  let filtered = selectTestCasesAllTestCases.value.filter(tc => !tc.title?.startsWith('[目录占位]'))
  
  if (selectTestCasesSelectedDirectoryPath.value !== null) {
    filtered = filtered.filter(testcase => {
      const modulePath = testcase.module || ''
      return modulePath === selectTestCasesSelectedDirectoryPath.value
    })
  }
  
  if (selectTestCasesPriorityFilter.value) {
    filtered = filtered.filter(tc => tc.priority === selectTestCasesPriorityFilter.value)
  }
  
  if (selectTestCasesSearchKeyword.value) {
    const keyword = selectTestCasesSearchKeyword.value.toLowerCase()
    filtered = filtered.filter(tc => {
      const caseKey = tc.case_key?.toLowerCase() || ''
      const title = tc.title?.toLowerCase() || ''
      return caseKey.includes(keyword) || title.includes(keyword)
    })
  }
  
  return filtered
})

const selectTestCasesPaginatedTestCases = computed(() => {
  const start = (selectTestCasesCurrentPage.value - 1) * selectTestCasesPageSize.value
  return selectTestCasesFilteredTestCases.value.slice(start, start + selectTestCasesPageSize.value)
})

const handleSelectTestCasesSearch = () => {
  selectTestCasesCurrentPage.value = 1
}

const handleSelectTestCasesSelectionChange = (selection: TestCase[]) => {
  // 获取当前页所有用例的ID
  const currentPageIds = new Set(selectTestCasesPaginatedTestCases.value.map((tc: TestCase) => tc.id))
  
  // 从ID集合中移除当前页的用例ID（因为当前页的选中状态会通过selection参数更新）
  currentPageIds.forEach(id => {
    selectTestCasesSelectedTestCaseIds.value.delete(id)
  })
  
  // 将当前页新选中的用例ID添加到集合中
  selection.forEach(tc => {
    selectTestCasesSelectedTestCaseIds.value.add(tc.id)
  })
  
  // 更新选中用例数组（用于显示，只包含当前页选中的）
  selectTestCasesSelectedTestCases.value = selection
}

// 所有用例（用于构建分组树，包含已关联的）
const selectTestCasesAllTestCasesForTree = ref<TestCase[]>([])
// 未关联的用例（用于右侧列表显示和选择）
const selectTestCasesUnlinkedTestCases = ref<TestCase[]>([])

const handleSelectTestCases = async (row: TestCaseReview) => {
  selectTestCasesReview.value = row
  selectTestCasesDrawerVisible.value = true
  selectTestCasesSelectedDirectoryPath.value = null
  selectTestCasesSearchKeyword.value = ''
  selectTestCasesPriorityFilter.value = ''
  selectTestCasesSelectedTestCases.value = []
  selectTestCasesSelectedTestCaseIds.value = new Set()
  selectTestCasesCurrentPage.value = 1
  
  // 加载所有用例
  selectTestCasesLoading.value = true
  try {
    const params: any = {
      project_id: row.project_id,
      limit: 10000
    }
    const allTestCases = await testcaseApi.getTestCases(params)
    // 保存所有用例用于构建分组树（与用例详情页一致）
    selectTestCasesAllTestCasesForTree.value = allTestCases
    
    // 过滤掉已经添加到评审中的用例（用于右侧列表显示）
    const reviewItems = await reviewApi.getReviewItems(row.id)
    const existingTestCaseIds = new Set(reviewItems.map(item => item.testcase_id))
    selectTestCasesUnlinkedTestCases.value = allTestCases.filter(tc => !existingTestCaseIds.has(tc.id))
    // 为了兼容性，也设置 selectTestCasesAllTestCases（但用于列表显示）
    selectTestCasesAllTestCases.value = selectTestCasesUnlinkedTestCases.value
  } catch (error: any) {
    ElMessage.error('加载用例列表失败')
  } finally {
    selectTestCasesLoading.value = false
  }
}

const handleClearSelectedTestCases = () => {
  selectTestCasesSelectedTestCases.value = []
  selectTestCasesSelectedTestCaseIds.value = new Set()
  // 清空表格中的选中状态
  if (selectTestCasesTableRef.value) {
    selectTestCasesTableRef.value.clearSelection()
  }
}

const handleConfirmSelectTestCases = async () => {
  if (!selectTestCasesReview.value || selectTestCasesSelectedTestCaseIds.value.size === 0) return
  
  try {
    // 从所有用例中获取选中的用例对象
    const selectedTestCases = selectTestCasesAllTestCases.value.filter(tc => 
      selectTestCasesSelectedTestCaseIds.value.has(tc.id)
    )
    
    for (const testcase of selectedTestCases) {
      await reviewApi.addReviewItem(selectTestCasesReview.value.id, {
        review_id: selectTestCasesReview.value.id,
        testcase_id: testcase.id
      })
    }
    ElMessage.success(`成功关联 ${selectedTestCases.length} 个用例`)
    selectTestCasesDrawerVisible.value = false
    selectTestCasesSelectedTestCases.value = []
    selectTestCasesSelectedTestCaseIds.value = new Set()
    loadReviews()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '关联用例失败'
    ElMessage.error(errorMessage)
  }
}

// 评审抽屉相关函数
const reviewDrawerPriorityFilter = ref('')
const reviewDrawerStatusFilter = ref('')
const reviewDrawerSearchKeyword = ref('')
const reviewDrawerOnlyCommented = ref(false)
const reviewDrawerShowSubgroup = ref(true)
const reviewDrawerSortBy = ref('original')
const reviewDrawerCurrentPage = ref(1)
const reviewDrawerPageSize = ref(10)
const reviewDrawerSidebarWidth = ref(300)
const reviewDrawerIsResizing = ref(false)
const reviewDrawerResizeStartX = ref(0)
const reviewDrawerResizeStartWidth = ref(0)
const reviewDrawerCurrentTestCaseItem = ref<TestCaseReviewItem | null>(null)
const reviewDrawerSavingReview = ref(false)
const reviewDrawerSelectedGroupPath = ref<string | null>(null)
const reviewDrawerTestCaseFormData = reactive({
  title: '',
  precondition: '',
  steps: [] as Array<{ description: string; expected_result: string }>,
  type: 'functional',
  priority: 'P2'
})
const reviewDrawerReviewResultFormData = reactive({
  status: 'pending' as 'pending' | 'approved' | 'rejected',
  comments: ''
})

const handleReviewDrawer = async (row: TestCaseReview) => {
  try {
    const reviewDetail = await reviewApi.getTestCaseReview(row.id)
    reviewDrawerReview.value = reviewDetail
    reviewDrawerVisible.value = true
    // 重置筛选条件
    reviewDrawerSelectedGroupPath.value = null
    reviewDrawerPriorityFilter.value = ''
    reviewDrawerStatusFilter.value = ''
    reviewDrawerSearchKeyword.value = ''
    reviewDrawerOnlyCommented.value = false
    reviewDrawerCurrentPage.value = 1
    await loadReviewDrawerItems(row.id)
  } catch (error: any) {
    ElMessage.error('加载评审详情失败')
  }
}

const loadReviewDrawerItems = async (reviewId: number) => {
  reviewDrawerReviewItemsLoading.value = true
  try {
    reviewDrawerReviewItems.value = await reviewApi.getReviewItems(reviewId)
  } catch (error: any) {
    ElMessage.error('加载评审用例列表失败')
  } finally {
    reviewDrawerReviewItemsLoading.value = false
  }
}

// 构建评审抽屉的树形数据
const reviewDrawerTreeData = computed(() => {
  const tree: any[] = []
  const groupMap = new Map<string, any>()
  
  reviewDrawerReviewItems.value.forEach(item => {
    const modulePath = item.testcase?.module || ''
    if (!modulePath) {
      // 没有分组的用例，直接添加到根节点
      tree.push({
        id: `testcase-${item.id}`,
        label: item.testcase?.title || '未知用例',
        isLeaf: true,
        reviewItem: item,
        reviewStatus: item.status
      })
      return
    }
    
    const pathParts = modulePath.split('/').filter(p => p.trim())
    let currentPath = ''
    let parent: any = null
    
    pathParts.forEach((part, index) => {
      currentPath = currentPath ? `${currentPath}/${part}` : part
      
      if (!groupMap.has(currentPath)) {
        const groupNode = {
          id: `group-${currentPath}`,
          label: part,
          isLeaf: false,
          path: currentPath,
          children: []
        }
        groupMap.set(currentPath, groupNode)
        
        if (parent) {
          parent.children.push(groupNode)
        } else {
          tree.push(groupNode)
        }
      }
      
      parent = groupMap.get(currentPath)
      
      // 如果是最后一个路径部分，添加用例节点
      if (index === pathParts.length - 1) {
        parent.children.push({
          id: `testcase-${item.id}`,
          label: item.testcase?.title || '未知用例',
          isLeaf: true,
          reviewItem: item,
          reviewStatus: item.status
        })
      }
    })
  })
  
  return tree
})

const reviewDrawerFilteredItems = computed(() => {
  let filtered = reviewDrawerReviewItems.value
  
  // 根据选中的分组过滤
  if (reviewDrawerSelectedGroupPath.value !== null) {
    filtered = filtered.filter(item => {
      const modulePath = item.testcase?.module || ''
      // 如果用例的module路径以选中的分组路径开头，则包含该用例
      return modulePath === reviewDrawerSelectedGroupPath.value || 
             modulePath.startsWith(reviewDrawerSelectedGroupPath.value + '/')
    })
  }
  
  if (reviewDrawerPriorityFilter.value) {
    filtered = filtered.filter(item => item.testcase?.priority === reviewDrawerPriorityFilter.value)
  }
  
  if (reviewDrawerStatusFilter.value) {
    filtered = filtered.filter(item => item.status === reviewDrawerStatusFilter.value)
  }
  
  if (reviewDrawerSearchKeyword.value) {
    const keyword = reviewDrawerSearchKeyword.value.toLowerCase()
    filtered = filtered.filter(item => {
      const caseKey = item.testcase?.case_key?.toLowerCase() || ''
      const title = item.testcase?.title?.toLowerCase() || ''
      return caseKey.includes(keyword) || title.includes(keyword)
    })
  }
  
  if (reviewDrawerOnlyCommented.value) {
    filtered = filtered.filter(item => item.comments && item.comments.trim())
  }
  
  // 排序
  if (reviewDrawerSortBy.value === 'priority') {
    const priorityOrder = { 'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3, 'P4': 4 }
    filtered = [...filtered].sort((a, b) => {
      const aPriority = priorityOrder[a.testcase?.priority as keyof typeof priorityOrder] ?? 5
      const bPriority = priorityOrder[b.testcase?.priority as keyof typeof priorityOrder] ?? 5
      return aPriority - bPriority
    })
  } else if (reviewDrawerSortBy.value === 'status') {
    const statusOrder = { 'pending': 0, 'approved': 1, 'rejected': 2 }
    filtered = [...filtered].sort((a, b) => {
      const aStatus = statusOrder[a.status as keyof typeof statusOrder] ?? 3
      const bStatus = statusOrder[b.status as keyof typeof statusOrder] ?? 3
      return aStatus - bStatus
    })
  }
  
  return filtered
})

const reviewDrawerPaginatedItems = computed(() => {
  const start = (reviewDrawerCurrentPage.value - 1) * reviewDrawerPageSize.value
  return reviewDrawerFilteredItems.value.slice(start, start + reviewDrawerPageSize.value)
})

const handleReviewDrawerResizeStart = (e: MouseEvent) => {
  reviewDrawerIsResizing.value = true
  reviewDrawerResizeStartX.value = e.clientX
  reviewDrawerResizeStartWidth.value = reviewDrawerSidebarWidth.value
  document.addEventListener('mousemove', handleReviewDrawerResizeMove)
  document.addEventListener('mouseup', handleReviewDrawerResizeEnd)
  e.preventDefault()
}

const handleReviewDrawerResizeMove = (e: MouseEvent) => {
  if (!reviewDrawerIsResizing.value) return
  const diff = e.clientX - reviewDrawerResizeStartX.value
  const newWidth = reviewDrawerResizeStartWidth.value + diff
  reviewDrawerSidebarWidth.value = Math.max(200, Math.min(600, newWidth))
}

const handleReviewDrawerResizeEnd = () => {
  reviewDrawerIsResizing.value = false
  document.removeEventListener('mousemove', handleReviewDrawerResizeMove)
  document.removeEventListener('mouseup', handleReviewDrawerResizeEnd)
}

const handleReviewDrawerResizeReset = () => {
  reviewDrawerSidebarWidth.value = 300
}

const reviewDrawerProgressPercentage = computed(() => {
  if (reviewDrawerTotalCount.value === 0) return 0
  return Math.round((reviewDrawerReviewedCount.value / reviewDrawerTotalCount.value) * 100)
})

const reviewDrawerProgressStatus = computed(() => {
  const percentage = reviewDrawerProgressPercentage.value
  if (percentage === 100) return 'success'
  if (percentage >= 50) return ''
  return 'exception'
})

const reviewDrawerProgressText = computed(() => {
  return `${reviewDrawerProgressPercentage.value}%评审通过`
})

const reviewDrawerTotalCount = computed(() => {
  return reviewDrawerReviewItems.value.length
})

const reviewDrawerReviewedCount = computed(() => {
  return reviewDrawerReviewItems.value.filter(item => item.status === 'approved' || item.status === 'rejected').length
})

const reviewDrawerTotalReviewersCount = computed(() => {
  // 这里应该从评审配置中获取，暂时返回1
  return 1
})

const reviewDrawerReviewedReviewersCount = computed(() => {
  // 这里应该统计已评审的人员数，暂时返回已评审用例数大于0时返回1
  return reviewDrawerReviewedCount.value > 0 ? 1 : 0
})

const handleReviewDrawerTreeNodeClick = (data: any) => {
  if (data.isLeaf && data.reviewItem) {
    // 叶子节点（用例），打开用例详情
    handleReviewDrawerTableRowClick(data.reviewItem)
  } else if (!data.isLeaf && data.path) {
    // 中间层分组，筛选该分组下的所有用例
    reviewDrawerSelectedGroupPath.value = data.path
    reviewDrawerCurrentPage.value = 1
  }
}

const handleReviewDrawerTableRowClick = (item: TestCaseReviewItem) => {
  if (!item.testcase) return
  
  // 点击用例时，清除分组筛选
  reviewDrawerSelectedGroupPath.value = null
  
  reviewDrawerCurrentTestCaseItem.value = item
  
  Object.assign(reviewDrawerTestCaseFormData, {
    title: item.testcase.title || '',
    precondition: item.testcase.precondition || '',
    steps: item.testcase.steps ? JSON.parse(JSON.stringify(item.testcase.steps)) : [],
    type: item.testcase.type || 'functional',
    priority: item.testcase.priority || 'P2'
  })
  
  Object.assign(reviewDrawerReviewResultFormData, {
    status: item.status || 'pending',
    comments: item.comments || ''
  })
  
  reviewDrawerTestCaseDetailVisible.value = true
}

const handleSaveReviewDrawerTestCase = async () => {
  if (!reviewDrawerCurrentTestCaseItem.value || !reviewDrawerReview.value) return
  
  reviewDrawerSavingReview.value = true
  try {
    await testcaseApi.updateTestCase(reviewDrawerCurrentTestCaseItem.value.testcase_id, {
      title: reviewDrawerTestCaseFormData.title,
      precondition: reviewDrawerTestCaseFormData.precondition,
      steps: reviewDrawerTestCaseFormData.steps,
      type: reviewDrawerTestCaseFormData.type,
      priority: reviewDrawerTestCaseFormData.priority
    })
    
    await reviewApi.updateReviewItem(
      reviewDrawerReview.value.id,
      reviewDrawerCurrentTestCaseItem.value.id,
      {
        status: reviewDrawerReviewResultFormData.status,
        comments: reviewDrawerReviewResultFormData.comments,
        reviewer_id: getCurrentUser()?.id
      }
    )
    
    ElMessage.success('评审结果已保存')
    reviewDrawerTestCaseDetailVisible.value = false
    await loadReviewDrawerItems(reviewDrawerReview.value.id)
    return true
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
    return false
  } finally {
    reviewDrawerSavingReview.value = false
  }
}

const handleSaveAndNextReviewDrawerTestCase = async () => {
  if (!reviewDrawerCurrentTestCaseItem.value) return
  
  // 保存前获取当前用例的ID和下一个用例的信息
  const currentItemId = reviewDrawerCurrentTestCaseItem.value.id
  const currentIndex = reviewDrawerFilteredItems.value.findIndex(
    item => item.id === currentItemId
  )
  const nextItemId = currentIndex >= 0 && currentIndex < reviewDrawerFilteredItems.value.length - 1
    ? reviewDrawerFilteredItems.value[currentIndex + 1].id
    : null
  
  // 执行保存（保存函数内部会调用 loadReviewDrawerItems 重新加载数据）
  const success = await handleSaveReviewDrawerTestCase()
  if (!success) return
  
  // 保存成功后，从重新加载的数据中查找下一个用例
  if (nextItemId) {
    // 等待一下确保数据已更新
    await nextTick()
    const refreshedNextItem = reviewDrawerFilteredItems.value.find(item => item.id === nextItemId)
    if (refreshedNextItem) {
      handleReviewDrawerTableRowClick(refreshedNextItem)
      ElMessage.success('保存成功，进入下一个用例')
    } else {
      ElMessage.info('已是最后一个用例')
    }
  } else {
    ElMessage.info('已是最后一个用例')
    reviewDrawerTestCaseDetailVisible.value = false
  }
}

// 组件卸载时清理调整宽度的事件监听
onUnmounted(() => {
  isMounted = false
  if (cleanupProjectChanged) {
    cleanupProjectChanged()
  }
  document.removeEventListener('mousemove', handleSelectTestCasesResizeMove)
  document.removeEventListener('mouseup', handleSelectTestCasesResizeEnd)
})
</script>

<style scoped>
.testcase-review-page {
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

/* 评审详情抽屉样式 */
.review-detail-drawer :deep(.el-drawer__body) {
  padding: 20px;
  overflow-y: auto;
}

.review-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.review-detail-content {
  height: calc(100vh - 80px);
  overflow-y: auto;
}

/* 添加用例子抽屉样式 */
.add-testcase-drawer :deep(.el-drawer__body) {
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.add-testcase-drawer :deep(.el-drawer) {
  z-index: 3001 !important; /* 确保子抽屉显示在外层抽屉之上 */
}

.add-testcase-drawer :deep(.el-overlay) {
  z-index: 3000 !important;
}

/* 步骤表格样式 */
.steps-table {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 12px;
}

.steps-table-header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.header-cell {
  padding: 12px;
  text-align: center;
  border-right: 1px solid #e4e7ed;
  box-sizing: border-box;
}

.header-cell:last-child {
  border-right: none;
}

.header-cell-number {
  width: 60px;
  flex-shrink: 0;
}

.header-cell-step {
  flex: 1;
  min-width: 0;
}

.header-cell-expected {
  flex: 1;
  min-width: 0;
}

.steps-table-row {
  display: flex;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
  transition: background 0.2s;
}

.steps-table-row:hover {
  background: #f5f7fa;
}

.steps-table-row:last-child {
  border-bottom: none;
}

.table-cell {
  padding: 12px;
  border-right: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.table-cell:last-child {
  border-right: none;
}

.table-cell-number {
  width: 60px;
  flex-shrink: 0;
  justify-content: center;
}

.table-cell-step {
  flex: 1;
  min-width: 0;
}

.table-cell-expected {
  flex: 1;
  min-width: 0;
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-input {
  width: 100%;
}

.step-input :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding: 0;
  resize: none;
  font-size: 13px;
  line-height: 1.6;
}

.step-input :deep(.el-textarea__inner):focus {
  border: none;
  box-shadow: none;
}

/* 操作栏样式 */
.table-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-row {
  display: flex;
  gap: 8px;
}

/* 筛选用例抽屉样式 */
.select-testcases-drawer :deep(.el-drawer__body) {
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: calc(100vh - 60px);
}

.select-testcases-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.select-testcases-layout {
  display: flex;
  gap: 0;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.select-testcases-sidebar {
  width: 280px;
  min-width: 200px;
  max-width: 600px;
  flex-shrink: 0;
  height: 100%;
  display: flex;
  flex-direction: row;
  transition: width 0.2s ease;
}

.select-testcases-directory-card {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.select-testcases-directory-card :deep(.el-card__header) {
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.select-testcases-directory-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.select-testcases-directory-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.select-testcases-directory-tree-container {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.select-testcases-directory-tree {
  background: transparent;
}

/* 子分组对齐样式 */
.select-testcases-directory-tree :deep(.el-tree-node__children) {
  padding-left: 0;
  margin-left: 0;
}

.select-testcases-directory-tree :deep(.el-tree-node__children .el-tree-node__content::before) {
  display: none;
}

.select-testcases-directory-tree :deep(.el-tree-node__children .el-tree-node__content) {
  margin-left: 0;
  padding-left: 0;
  position: relative;
}

.select-testcases-directory-tree :deep(.el-tree-node__children .el-tree-node__expand-icon) {
  margin-left: 0;
  padding-left: 0;
  position: absolute;
  left: 26px;
}

.select-testcases-directory-tree :deep(.el-tree-node__children .select-testcases-directory-node-wrapper) {
  margin-left: 0;
  padding-left: 26px;
}

.select-testcases-directory-node-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 4px;
}

.select-testcases-directory-node-content {
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
  min-width: 0;
}

.select-testcases-directory-folder-icon {
  font-size: 18px;
  color: #f5a623;
  flex-shrink: 0;
  transition: all 0.2s;
}

.select-testcases-directory-folder-icon:not(.is-leaf) {
  color: #667eea;
}

.select-testcases-directory-folder-icon.is-expanded:not(.is-leaf) {
  color: #764ba2;
}

.select-testcases-directory-folder-icon.is-leaf {
  color: #f5a623;
}

.select-testcases-directory-node-label {
  flex: 0 1 auto;
  font-size: 14px;
  color: #303133;
  font-weight: 400;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 6px;
  min-width: 0;
}

.select-testcases-directory-node-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 18px;
  padding: 0 6px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 9px;
  font-size: 11px;
  color: #606266;
  font-weight: 500;
  flex-shrink: 0;
  margin-left: 6px;
}

.select-testcases-resize-handle {
  width: 4px;
  flex-shrink: 0;
  background: #e4e7ed;
  cursor: col-resize;
  transition: background 0.2s;
  position: relative;
  margin: 0 8px;
}

.select-testcases-resize-handle:hover {
  background: #409eff;
}

.select-testcases-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 0;
  overflow: hidden;
  height: 100%;
}

.select-testcases-list-card {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
}

.select-testcases-list-card :deep(.el-card__header) {
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.select-testcases-list-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  padding: 20px;
  flex: 1;
  min-height: 0;
}

/* 修复选择列对齐问题 */
.select-testcases-list-card :deep(.el-table__header-wrapper .el-table__header th:first-child),
.select-testcases-list-card :deep(.el-table__body-wrapper .el-table__body td:first-child) {
  text-align: center;
  padding-left: 12px;
  padding-right: 12px;
}

.select-testcases-list-card :deep(.el-checkbox) {
  display: flex;
  align-items: center;
  justify-content: center;
}

.select-testcases-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.select-testcases-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-top: 1px solid #e4e7ed;
  margin-top: 16px;
  flex-shrink: 0;
}

.select-testcases-footer-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.select-testcases-footer-left .el-button.is-link {
  background: transparent !important;
  background-color: transparent !important;
  padding: 0 !important;
  border: none !important;
  box-shadow: none !important;
}

.select-testcases-footer-left .el-button.is-link:hover {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.select-testcases-footer-left .el-button.is-link:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.select-testcases-footer-right {
  display: flex;
  gap: 10px;
}

/* 评审抽屉样式 */
.review-drawer :deep(.el-drawer) {
  border-radius: 12px 0 0 12px;
  overflow: hidden;
}

.review-drawer :deep(.el-drawer__body) {
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
}

.review-drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.review-drawer-content {
  flex: 1;
  overflow: hidden;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.review-progress-card {
  margin-bottom: 16px;
}

.review-progress-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-progress-item {
  display: flex;
  align-items: center;
}

.review-progress-label {
  font-weight: 500;
  min-width: 80px;
}

.review-progress-text {
  font-weight: 500;
  min-width: 100px;
}

.review-progress-stats {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
}

.review-drawer-layout {
  display: flex;
  gap: 0;
  margin-top: 16px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
  align-items: stretch;
}

.review-drawer-sidebar {
  width: 300px;
  min-width: 200px;
  max-width: 600px;
  flex-shrink: 0;
  display: flex;
  flex-direction: row;
  transition: width 0.2s ease;
  align-self: stretch;
}

.review-drawer-resize-handle {
  width: 4px;
  flex-shrink: 0;
  background: #e4e7ed;
  cursor: col-resize;
  transition: background 0.2s;
  position: relative;
  margin: 0 8px;
}

.review-drawer-resize-handle:hover {
  background: #409eff;
}

.review-drawer-tree-card {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
}

.review-drawer-tree-card :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
}

.review-drawer-tree-card :deep(.el-card__header) {
  flex-shrink: 0;
}

.review-drawer-tree-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.review-drawer-tree-container {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.review-drawer-tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.review-drawer-tree-icon {
  font-size: 16px;
  color: #667eea;
  flex-shrink: 0;
}

.review-drawer-tree-icon.is-leaf {
  color: #f5a623;
}

.review-drawer-tree-label {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.review-drawer-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  align-self: stretch;
}

.review-drawer-list-card {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
}

.review-drawer-list-card :deep(.el-card) {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin: 0;
  border: none;
  box-shadow: none;
}

.review-drawer-list-card :deep(.el-card__header) {
  display: none;
}

.review-drawer-list-card :deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 20px;
  min-height: 0;
}

.review-drawer-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.review-drawer-list-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.review-drawer-list-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  flex-shrink: 0;
}

/* 评审用例详情子抽屉样式 */
.review-testcase-detail-drawer :deep(.el-drawer__body) {
  padding: 20px;
  overflow-y: auto;
}

.review-testcase-detail-drawer :deep(.el-drawer) {
  border-radius: 12px 0 0 12px;
  overflow: hidden;
}

.review-testcase-detail-drawer :deep(.el-drawer__header) {
  background: #ffffff;
  color: #303133;
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
}

.review-testcase-detail-drawer :deep(.el-drawer__title) {
  color: #303133;
  font-weight: 600;
  font-size: 18px;
}

.review-testcase-detail-content {
  min-height: calc(100vh - 200px);
}

/* 抽屉布局样式（与用例详情抽屉一致） */
.review-testcase-detail-drawer .testcase-drawer-row {
  margin: 0;
  min-height: calc(100vh - 200px);
}

.review-testcase-detail-drawer .drawer-left-col {
  padding-right: 16px;
  border-right: 1px solid #e4e7ed;
}

.review-testcase-detail-drawer .drawer-right-col {
  padding-left: 16px;
}

.review-testcase-detail-drawer .right-section {
  height: 100%;
}

.review-testcase-detail-drawer .section-block {
  margin-bottom: 24px;
}

.review-testcase-detail-drawer .section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.review-testcase-detail-drawer .precondition-input {
  width: 100%;
}

.review-testcase-detail-drawer .precondition-input :deep(.el-textarea__inner) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
}

.review-testcase-detail-drawer .section-block :deep(.el-input__wrapper) {
  border-radius: 4px;
}

.review-testcase-detail-drawer .right-form {
  width: 100%;
}

.review-testcase-detail-drawer .drawer-footer {
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.review-testcase-detail-drawer .step-input :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  padding: 4px 0;
  min-height: 24px;
  line-height: 1.5;
  resize: vertical;
  box-shadow: none;
}

.review-testcase-detail-drawer .step-input :deep(.el-textarea__inner):focus {
  border: none;
  background: transparent;
  box-shadow: none;
}
</style>
