<template>
  <div class="requirements-page">
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Sunny /></el-icon>需求管理
          <span v-if="hasProjectSelected && getCurrentProjectName" class="current-project-tag">
            {{ getCurrentProjectName }}
          </span>
        </h2>
      </div>
      <div class="filter-row">
        <el-select v-if="!hasProjectSelected" v-model="searchProjectId" placeholder="选择项目" clearable @change="handleSearch" style="width: 180px">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="searchSprintId" placeholder="选择迭代" clearable @change="handleSearch" style="width: 180px">
          <el-option v-for="s in sprints" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="searchStatus" placeholder="状态" clearable @change="handleSearch" style="width: 140px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="searchPriority" placeholder="优先级" clearable @change="handleSearch" style="width: 120px">
          <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-input v-model="searchKeyword" placeholder="搜索需求标题" clearable @keyup.enter="handleSearch" style="width: 220px">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" style="margin-left: auto" @click="handleCreate">
          <el-icon><Plus /></el-icon>新建需求
        </el-button>
      </div>
    </el-card>

    <el-card class="table-card">
      <el-table
        ref="tableRef"
        :data="items"
        v-loading="loading"
        class="req-requirements-table"
        style="width: 100%"
        stripe
        row-key="id"
        :indent="22"
        :tree-props="{ children: 'children' }"
      >
        <!-- 编号列放第一位，隐藏展开箭头 -->
        <el-table-column label="编号" width="80" align="center" class-name="req-id-col hide-expand">
          <template #default="{ row }">{{ row.id }}</template>
        </el-table-column>
        <!-- 标题列，手动添加展开箭头 -->
        <el-table-column label="标题" min-width="340" class-name="req-title-col">
          <template #default="{ row }">
            <div
              :class="['req-table-title-inner', row.parent_id ? 'req-table-title-inner--child' : '']"
            >
              <!-- 展开/收起箭头 -->
              <span 
                v-if="row.children && row.children.length" 
                class="custom-expand-icon"
                @click.stop="toggleRowExpand(row)"
              >
                <el-icon :class="{ 'is-expanded': isRowExpanded(row) }"><CaretRight /></el-icon>
              </span>
              <span v-else class="custom-expand-placeholder"></span>
              <span
                v-if="row.parent_id"
                class="req-table-tree-branch"
                aria-hidden="true"
              >{{ tableChildBranchChar(row) }}</span>
              <span v-if="row.parent_id" class="req-child-marker">子</span>
              <el-icon class="req-icon"><Sunny /></el-icon>
              <span
                :class="(row.children && row.children.length) ? 'req-title-parent' : 'req-title-child'"
                @click="handleEdit(row)"
              >{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="项目" min-width="140" align="center">
          <template #default="{ row }">{{ row.project?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="迭代" min-width="140" align="center">
          <template #default="{ row }">{{ row.sprint?.name || '-' }}</template>
        </el-table-column>
        <el-table-column label="优先级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityTagType(row.priority)" size="small">{{ priorityLabel(row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理人" min-width="120" align="center">
          <template #default="{ row }">{{ row.assignee?.display_name || row.assignee?.username || '-' }}</template>
        </el-table-column>
        <el-table-column label="截止日期" width="120" align="center">
          <template #default="{ row }">{{ row.due_date || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="130" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" size="small" @click="handleEdit(row)">
                <el-icon><EditPen /></el-icon>编辑
              </el-button>
              <el-button link type="danger" size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>删除
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
          :total="total"
          @current-change="loadData"
          @size-change="() => { currentPage = 1; loadData() }"
        />
      </div>
    </el-card>

    <!-- 新建/编辑需求抽屉 -->
    <el-drawer
      v-model="dialogVisible"
      :title="editingId ? '编辑需求' : '新建需求'"
      size="80%"
      class="req-drawer"
      :close-on-click-modal="true"
    >
      <div class="req-drawer-layout">
        <!-- 左侧：标题 + 内容 + 子需求 -->
        <div class="req-main">
          <div class="req-main-scroll">
            <el-form :model="formData" label-position="top">
              <el-form-item label="标题" required>
                <el-input v-model="formData.title" placeholder="请输入需求标题" />
              </el-form-item>
              <el-form-item label="内容">
                <el-input
                  v-model="formData.content"
                  type="textarea"
                  :rows="10"
                  placeholder="请输入需求内容"
                />
              </el-form-item>
            </el-form>

            <!-- 子需求区块（仅编辑时显示） -->
            <template v-if="editingId">
              <el-divider style="margin: 12px 0" />
              <div class="children-section">
                <div class="children-header">
                  <span class="children-title">子需求</span>
                  <span
                    class="add-child-link"
                    v-if="!showQuickCreate"
                    @click="showQuickCreate = true"
                  >
                    <el-icon><Plus /></el-icon>
                  </span>
                  <span class="children-progress" v-if="editingChildren.length > 0">
                    {{ completedChildCount }}/{{ editingChildren.length }} 已完成
                  </span>
                </div>

                <!-- 子需求列表（树状缩进，与父标题区错开） -->
                <div v-if="editingChildren.length > 0" class="children-list-wrapper">
                  <div class="children-list">
                    <div
                      v-for="(child, childIdx) in editingChildren"
                      :key="child.id"
                      class="child-item"
                    >
                      <div class="child-main" @click="openChildEdit(child)">
                        <span class="child-tree-branch" aria-hidden="true">
                          {{ childIdx === editingChildren.length - 1 ? '└' : '├' }}
                        </span>
                        <span class="drawer-child-marker">子</span>
                        <el-icon class="child-icon drawer-child-icon"><Sunny /></el-icon>
                        <span class="child-id">#{{ child.id }}</span>
                        <span class="child-title">{{ child.title }}</span>
                        <span v-if="child.due_date" class="child-due">{{ child.due_date }} 截止</span>
                        <el-tag :type="priorityTagType(child.priority)" size="small" class="child-tag">
                          {{ priorityLabel(child.priority) }}
                        </el-tag>
                        <el-tag :type="statusTagType(child.status)" size="small" class="child-tag">
                          {{ statusLabel(child.status) }}
                        </el-tag>
                      </div>
                      <div class="child-actions">
                        <el-button
                          link
                          size="small"
                          @click.stop="deleteChildById(child.id, child.title)"
                        >
                          删除
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 快速创建子需求 -->
                <div v-if="showQuickCreate" class="quick-create-row">
                  <span class="child-tree-branch child-tree-branch--continue" aria-hidden="true">├</span>
                  <span class="drawer-child-marker drawer-child-marker--ghost">子</span>
                  <el-icon class="child-icon drawer-child-icon"><Sunny /></el-icon>
                  <el-input
                    v-model="quickCreateTitle"
                    placeholder="输入标题快速创建需求"
                    size="small"
                    style="flex: 1"
                    @keyup.enter="quickCreateChild"
                    ref="quickCreateInputRef"
                  />
                  <el-button type="primary" size="small" :loading="quickCreating" @click="quickCreateChild">创建</el-button>
                  <el-button size="small" @click="showQuickCreate = false; quickCreateTitle = ''">取消</el-button>
                </div>
                <div v-else-if="editingChildren.length === 0" class="children-empty">
                  暂无子需求，点击 <el-icon style="vertical-align: middle"><Plus /></el-icon> 添加
                </div>
              </div>
            </template>

          </div>
        </div>

        <!-- 右侧：项目 / 迭代 / 状态等字段 -->
        <div class="req-side">
          <div class="req-side-title">基本信息</div>
          <el-form :model="formData" label-position="top">
            <el-form-item label="项目" required>
              <el-select v-model="formData.project_id" placeholder="选择项目" filterable style="width: 100%"
                :disabled="hasProjectSelected || !!editingId"
                :style="{ opacity: (hasProjectSelected || !!editingId) ? 0.6 : 1 }"
                @change="onProjectChange">
                <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="迭代">
              <el-select v-model="formData.sprint_id" placeholder="选择迭代" filterable clearable style="width: 100%">
                <el-option v-for="s in filteredSprints" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="处理人">
              <el-select v-model="formData.assignee_id" placeholder="选择处理人" filterable clearable style="width: 100%">
                <el-option v-for="u in users" :key="u.id" :label="u.display_name || u.username" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="优先级">
              <el-select v-model="formData.priority" style="width: 100%">
                <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期">
              <el-date-picker v-model="formData.start_date" type="date" placeholder="选择开始日期"
                style="width: 100%" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="截止日期">
              <el-date-picker v-model="formData.due_date" type="date" placeholder="选择截止日期"
                style="width: 100%" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item v-if="editingId" label="状态">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-drawer>

    <!-- 子需求编辑抽屉 -->
    <el-drawer
      v-model="childDrawerVisible"
      title="编辑子需求"
      size="60%"
      class="req-drawer child-req-drawer"
      :close-on-click-modal="true"
      @closed="childEditingId = undefined"
    >
      <div class="req-drawer-layout child-layout">
        <div class="req-main">
          <div class="req-main-scroll">
            <el-form :model="childFormData" label-position="top">
              <el-form-item label="标题" required>
                <el-input v-model="childFormData.title" placeholder="请输入子需求标题" />
              </el-form-item>
              <el-form-item label="内容">
                <el-input
                  v-model="childFormData.content"
                  type="textarea"
                  :rows="10"
                  placeholder="请输入子需求内容"
                />
              </el-form-item>
            </el-form>
          </div>
        </div>

        <div class="req-side child-side">
          <div class="req-side-title">基本信息</div>
          <el-form :model="childFormData" label-position="top">
            <el-form-item label="项目" required>
              <el-select v-model="childFormData.project_id" placeholder="选择项目" filterable style="width: 100%"
                :disabled="hasProjectSelected || !!childEditingId"
                :style="{ opacity: (hasProjectSelected || !!childEditingId) ? 0.6 : 1 }"
                @change="onChildProjectChange">
                <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="迭代">
              <el-select v-model="childFormData.sprint_id" placeholder="选择迭代" filterable clearable style="width: 100%">
                <el-option v-for="s in childFilteredSprints" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="处理人">
              <el-select v-model="childFormData.assignee_id" placeholder="选择处理人" filterable clearable style="width: 100%">
                <el-option v-for="u in users" :key="u.id" :label="u.display_name || u.username" :value="u.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="优先级">
              <el-select v-model="childFormData.priority" style="width: 100%">
                <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="开始日期">
              <el-date-picker v-model="childFormData.start_date" type="date" placeholder="选择开始日期"
                style="width: 100%" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="截止日期">
              <el-date-picker v-model="childFormData.due_date" type="date" placeholder="选择截止日期"
                style="width: 100%" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="childFormData.status" style="width: 100%">
                <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>

      <template #footer>
        <el-button @click="childDrawerVisible = false">取消</el-button>
        <el-button type="primary" :loading="childSaving" @click="saveChild">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, Sunny, CaretRight } from '@element-plus/icons-vue'
import * as reqApi from '../api/requirements'
import * as projectApi from '../api/projects'
import * as sprintApi from '../api/sprints'
import * as userApi from '../api/users'
import type { Requirement, RequirementChild } from '../api/requirements'
import { useProjectContext } from '../composables/useProjectContext'

const { getCurrentProjectId, getCurrentProjectName, hasProjectSelected, onProjectChanged, ensureInitialized } = useProjectContext()

// ── 列表数据 ──────────────────────────────
const items = ref<Requirement[]>([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)

// ── 表格展开/收起控制 ────────────────────────
const tableRef = ref()
const expandedRows = ref<Set<number>>(new Set())

const toggleRowExpand = (row: any) => {
  if (expandedRows.value.has(row.id)) {
    expandedRows.value.delete(row.id)
  } else {
    expandedRows.value.add(row.id)
  }
  if (tableRef.value) {
    tableRef.value.toggleRowExpansion(row)
  }
}

const isRowExpanded = (row: any) => {
  return expandedRows.value.has(row.id)
}

// ── 搜索筛选 ──────────────────────────────
const projects = ref<any[]>([])
const sprints = ref<any[]>([])
const users = ref<any[]>([])
const searchProjectId = ref<number | undefined>()
const searchSprintId = ref<number | undefined>()
const searchStatus = ref('')
const searchPriority = ref('')
const searchKeyword = ref('')

// ── 主编辑弹窗 ────────────────────────────
const dialogVisible = ref(false)
const saving = ref(false)
const editingId = ref<number | undefined>()
const editingChildren = ref<RequirementChild[]>([])

const formData = reactive({
  project_id: undefined as number | undefined,
  sprint_id: null as number | null,
  title: '',
  content: '',
  priority: 'medium',
  status: 'not_started',
  assignee_id: null as number | null,
  start_date: null as string | null,
  due_date: null as string | null,
})

// ── 子需求快速创建 ────────────────────────
const showQuickCreate = ref(false)
const quickCreateTitle = ref('')
const quickCreating = ref(false)
const quickCreateInputRef = ref()

// ── 子需求编辑抽屉 ────────────────────────
const childDrawerVisible = ref(false)
const childSaving = ref(false)
const childEditingId = ref<number | undefined>()
const childFormData = reactive({
  project_id: undefined as number | undefined,
  title: '',
  content: '',
  priority: 'medium',
  status: 'not_started',
  assignee_id: null as number | null,
  sprint_id: null as number | null,
  start_date: null as string | null,
  due_date: null as string | null,
})

// ── 枚举选项 ──────────────────────────────
const priorityOptions = [
  { value: 'urgent', label: '紧急' },
  { value: 'high', label: '高' },
  { value: 'medium', label: '中' },
  { value: 'low', label: '低' },
]
const statusOptions = [
  { value: 'not_started', label: '未开始' },
  { value: 'developing', label: '开发中' },
  { value: 'testing', label: '测试中' },
  { value: 'completed', label: '已完成' },
]

const priorityLabel = (v: string) => priorityOptions.find(p => p.value === v)?.label ?? v
const statusLabel = (v: string) => statusOptions.find(s => s.value === v)?.label ?? v

/** 需求列表子行：树形连接符（与抽屉子列表一致） */
function tableChildBranchChar(row: { id: number; parent_id?: number | null }) {
  if (row.parent_id == null) return ''
  for (const p of items.value) {
    const ch = p.children ?? []
    const idx = ch.findIndex(c => c.id === row.id)
    if (idx >= 0) return idx === ch.length - 1 ? '└' : '├'
  }
  return '└'
}
const priorityTagType = (v: string) => ({ urgent: 'danger', high: 'warning', medium: '', low: 'info' } as any)[v] ?? ''
const statusTagType = (v: string) => ({ not_started: 'info', developing: 'primary', testing: 'warning', completed: 'success' } as any)[v] ?? ''

const completedChildCount = computed(() =>
  editingChildren.value.filter(c => c.status === 'completed').length
)

const filteredSprints = computed(() => {
  const pid = formData.project_id
  if (!pid) return sprints.value
  return sprints.value.filter((s: any) => s.project_id === pid)
})

const childFilteredSprints = computed(() => {
  const pid = childFormData.project_id
  if (!pid) return sprints.value
  return sprints.value.filter((s: any) => s.project_id === pid)
})

const onProjectChange = () => { formData.sprint_id = null }
const onChildProjectChange = () => { childFormData.sprint_id = null }

// ── 数据加载 ──────────────────────────────
const loadData = async () => {
  if (!isMounted) return
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
      searchProjectId.value = getCurrentProjectId.value
    } else if (searchProjectId.value) {
      params.project_id = searchProjectId.value
    }
    if (searchSprintId.value) params.sprint_id = searchSprintId.value
    if (searchStatus.value) params.status = searchStatus.value
    if (searchPriority.value) params.priority = searchPriority.value
    if (searchKeyword.value) params.keyword = searchKeyword.value
    const res = await reqApi.getRequirements(params)
    items.value = res.items
    total.value = res.total
  } catch {
    if (isMounted) ElMessage.error('加载需求失败')
  } finally {
    if (isMounted) loading.value = false
  }
}

const handleSearch = () => { currentPage.value = 1; loadData() }
const handleReset = () => {
  searchKeyword.value = ''
  searchSprintId.value = undefined
  searchStatus.value = ''
  searchPriority.value = ''
  if (!hasProjectSelected.value) searchProjectId.value = undefined
  currentPage.value = 1
  loadData()
}

// ── 新建需求 ──────────────────────────────
const handleCreate = () => {
  editingId.value = undefined
  editingChildren.value = []
  Object.assign(formData, {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : undefined,
    sprint_id: null, title: '', content: '', priority: 'medium',
    status: 'not_started', assignee_id: null, start_date: null, due_date: null,
  })
  dialogVisible.value = true
}

// ── 编辑需求 ──────────────────────────────
const handleEdit = (row: Requirement) => {
  editingId.value = row.id
  editingChildren.value = [...(row.children ?? [])]
  showQuickCreate.value = false
  quickCreateTitle.value = ''
  Object.assign(formData, {
    project_id: row.project_id,
    sprint_id: row.sprint_id ?? null,
    title: row.title,
    content: row.content ?? '',
    priority: row.priority,
    status: row.status,
    assignee_id: row.assignee_id ?? null,
    start_date: row.start_date ?? null,
    due_date: row.due_date ?? null,
  })
  dialogVisible.value = true
}

// ── 保存需求 ──────────────────────────────
const handleSave = async () => {
  if (!formData.project_id || !formData.title) {
    ElMessage.warning('请填写必填项：项目和标题')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await reqApi.updateRequirement(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await reqApi.createRequirement(formData as any)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// ── 删除需求 ──────────────────────────────
const handleDelete = async (row: Requirement) => {
  const hasChildren = (row.children ?? []).length > 0
  const tip = hasChildren
    ? `需求「${row.title}」含 ${row.children!.length} 个子需求，删除后子需求将变为顶级需求，确定删除吗？`
    : `确定删除需求「${row.title}」吗？`
  try {
    await ElMessageBox.confirm(tip, '提示', { type: 'warning' })
    await reqApi.deleteRequirement(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// ── 快速创建子需求 ─────────────────────────
const quickCreateChild = async () => {
  if (!quickCreateTitle.value.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!editingId.value) return
  quickCreating.value = true
  try {
    // 找到当前编辑的父需求以获取 project_id
    const parentItem = items.value.find(r => r.id === editingId.value)
    const projectId = formData.project_id ?? parentItem?.project_id
    if (!projectId) { ElMessage.warning('未能确定所属项目'); return }

    const child = await reqApi.createRequirement({
      project_id: projectId,
      title: quickCreateTitle.value.trim(),
      priority: 'medium',
      status: 'not_started',
      parent_id: editingId.value,
    })
    editingChildren.value.push(child as any)
    quickCreateTitle.value = ''
    showQuickCreate.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '创建失败')
  } finally {
    quickCreating.value = false
  }
}

watch(showQuickCreate, (val) => {
  if (val) nextTick(() => quickCreateInputRef.value?.focus())
})

// ── 打开子需求编辑抽屉 ─────────────────────
const openChildEdit = async (child: RequirementChild) => {
  childEditingId.value = child.id
  try {
    const full = await reqApi.getRequirement(child.id)
    Object.assign(childFormData, {
      project_id: full.project_id,
      title: full.title,
      content: full.content ?? '',
      priority: full.priority,
      status: full.status,
      assignee_id: full.assignee_id ?? null,
      sprint_id: full.sprint_id ?? null,
      start_date: full.start_date ?? null,
      due_date: full.due_date ?? null,
    })
  } catch {
    Object.assign(childFormData, {
      project_id: (child as any).project_id ?? formData.project_id ?? childFormData.project_id,
      title: child.title,
      content: (child as any).content ?? '',
      priority: child.priority,
      status: child.status,
      assignee_id: child.assignee_id ?? null,
      sprint_id: (child as any).sprint_id ?? null,
      start_date: (child as any).start_date ?? null,
      due_date: child.due_date ?? null,
    })
  }
  childDrawerVisible.value = true
}

// ── 保存子需求 ────────────────────────────
const saveChild = async () => {
  if (!childFormData.title) { ElMessage.warning('请填写标题'); return }
  if (!childEditingId.value) return
  childSaving.value = true
  try {
    const updated = await reqApi.updateRequirement(childEditingId.value, childFormData)
    // 同步更新父需求编辑中的子需求列表
    const idx = editingChildren.value.findIndex(c => c.id === childEditingId.value)
    if (idx >= 0) {
      editingChildren.value[idx] = {
        ...editingChildren.value[idx],
        title: updated.title,
        priority: updated.priority,
        status: updated.status,
        due_date: updated.due_date ?? null,
        assignee_id: updated.assignee_id ?? null,
        assignee: updated.assignee,
      } as any
    }
    ElMessage.success('保存成功')
    childDrawerVisible.value = false
    loadData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    childSaving.value = false
  }
}

// ── 父需求抽屉中删除子需求 ────────────────────────────
const deleteChildById = async (childId: number, title: string) => {
  try {
    await ElMessageBox.confirm(`确定删除子需求「${title}」吗？`, '提示', { type: 'warning' })
    await reqApi.deleteRequirement(childId)
    editingChildren.value = editingChildren.value.filter(c => c.id !== childId)
    ElMessage.success('删除成功')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

// ── 生命周期 ──────────────────────────────
let cleanupProjectChanged: (() => void) | null = null
let isMounted = false

onMounted(async () => {
  isMounted = true
  await ensureInitialized()
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    searchProjectId.value = getCurrentProjectId.value
  }
  try { projects.value = (await projectApi.getProjects({ page_size: 1000 })).items } catch {}
  try {
    const pid = getCurrentProjectId.value
    sprints.value = (await sprintApi.getSprints({ project_id: pid ?? undefined, page_size: 1000 })).items
  } catch {}
  try { users.value = (await userApi.getUsers({ status: 'active', page_size: 1000 })).items } catch {}
  loadData()
  cleanupProjectChanged = onProjectChanged(() => {
    if (!isMounted) return
    searchProjectId.value = hasProjectSelected.value && getCurrentProjectId.value
      ? getCurrentProjectId.value : undefined
    currentPage.value = 1
    loadData()
  })
})

onUnmounted(() => { isMounted = false; cleanupProjectChanged?.() })

watch(() => getCurrentProjectId.value, (newVal, oldVal) => {
  if (newVal === oldVal) return
  searchProjectId.value = hasProjectSelected.value && getCurrentProjectId.value
    ? getCurrentProjectId.value : undefined
  currentPage.value = 1
  loadData()
})
</script>

<style scoped>
.requirements-page { animation: fadeIn 0.4s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.filter-header h2 {
  display: flex; align-items: center; gap: 8px;
  margin: 0 0 16px; font-size: 20px; font-weight: 600;
}
.current-project-tag {
  font-size: 14px;
  font-weight: 500;
  color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  padding: 4px 12px;
  border-radius: 16px;
  margin-left: 8px;
}
.filter-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.table-card { margin-top: 16px; }
.table-actions { display: flex; gap: 4px; justify-content: center; }

:deep(.el-table th.el-table__cell) { white-space: nowrap; }
:deep(.el-table__body td) { padding: 12px 0; border-bottom: 1px solid #f0f2f5; }

/* 标题列：图标 + 子需求标记 */
.req-icon { color: #409eff; font-size: 16px; margin-right: 8px; vertical-align: middle; }
.req-child-marker {
  display: inline-block;
  font-size: 11px;
  color: #909399;
  background: #f0f2f5;
  padding: 1px 5px;
  border-radius: 4px;
  margin-right: 6px;
  vertical-align: middle;
}
.req-title-parent,
.req-title-child { cursor: pointer; color: #303133; }
.req-title-parent:hover,
.req-title-child:hover { color: #303133; text-decoration: underline; }

/* 需求列表：树形标题列（展开/缩进在首列 + 子行 ├└） */
:deep(.req-requirements-table td.req-title-col .cell) {
  display: inline-flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 0;
  line-height: 1.4;
}
.req-table-title-inner {
  display: inline-flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 6px;
  min-width: 0;
}

/* 隐藏编号列的默认展开箭头和缩进 */
:deep(.hide-expand .cell) {
  padding-left: 12px !important;
}
:deep(.el-table__expand-icon) {
  display: none !important;
}
/* 移除树形缩进，让编号列对齐 */
:deep(.el-table__indent) {
  display: none !important;
}
:deep(.el-table__placeholder) {
  display: none !important;
}

/* 自定义展开箭头 */
.custom-expand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  cursor: pointer;
  color: #909399;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.custom-expand-icon:hover {
  color: #667eea;
}
.custom-expand-icon .el-icon {
  transition: transform 0.2s ease;
}
.custom-expand-icon .el-icon.is-expanded {
  transform: rotate(90deg);
}
.custom-expand-placeholder {
  width: 20px;
  flex-shrink: 0;
}
.req-table-title-inner--child {
  margin-left: 4px;
}
.req-table-tree-branch {
  flex-shrink: 0;
  width: 1.1em;
  text-align: center;
  color: #b1b5bd;
  font-size: 14px;
  line-height: 1;
  user-select: none;
}

/* 对话框 */
.dialog-header { display: flex; flex-direction: column; gap: 6px; }
.dialog-title { font-size: 18px; font-weight: 600; color: #303133; }
.dialog-description { font-size: 13px; color: #909399; }

:deep(.req-drawer .el-drawer__body) {
  padding: 0 0 12px;
  display: flex;
  flex-direction: column;
}

.req-drawer-layout {
  flex: 1;
  display: flex;
  padding: 12px 20px 0 20px;
  gap: 16px;
  min-height: 0;
}

.req-main {
  flex: 3;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.req-main-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 12px;
}

.req-side {
  width: 320px;
  flex-shrink: 0;
  border-left: 1px solid #ebeef5;
  padding-left: 16px;
  overflow-y: auto;
}

.child-layout .req-side {
  width: 260px;
}

.req-side-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

/* 活动日志 */
.activity-section {
  margin-top: 16px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.activity-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.activity-empty {
  font-size: 13px;
  color: #c0c4cc;
}

/* 子需求区块 */
.children-section { margin-bottom: 8px; }
.children-header {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px; font-size: 14px; font-weight: 600; color: #303133;
}
.children-title { font-size: 14px; font-weight: 600; }
.add-child-btn { padding: 2px 6px !important; }
.children-progress { margin-left: auto; font-size: 12px; color: #909399; font-weight: normal; }

.children-list { display: flex; flex-direction: column; gap: 2px; }

.child-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border-radius: 6px;
  transition: background 0.15s;
  font-size: 13px;
}
.child-item:hover { background: #f5f7fa; }

.children-list-wrapper {
  border: 1px solid #ebeef5;
  border-left: none;
  border-radius: 6px;
  padding: 8px 10px;
  margin-left: 28px;
  background-color: #fafafa;
}

.child-main {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
  cursor: pointer;
  padding-left: 2px;
}
.child-tree-branch {
  flex-shrink: 0;
  width: 1.1em;
  text-align: center;
  color: #b1b5bd;
  font-size: 14px;
  line-height: 1;
  user-select: none;
  margin-right: 2px;
}
.child-tree-branch--continue {
  color: #a8abb2;
}
.drawer-child-marker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 11px;
  color: #909399;
  background: #f0f2f5;
  padding: 1px 5px;
  border-radius: 4px;
  line-height: 1;
}
.drawer-child-marker--ghost {
  opacity: 0.65;
}
.drawer-child-icon {
  margin-left: 2px;
}
.child-icon { color: #409eff; font-size: 14px; flex-shrink: 0; }
.child-id { color: #909399; font-size: 12px; flex-shrink: 0; }
.child-title { flex: 1; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.child-due {
  font-size: 12px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 1px 6px;
  border-radius: 4px;
  flex-shrink: 0;
  min-width: 120px;
  text-align: center;
}
.child-tag {
  flex-shrink: 0;
  min-width: 72px;
  text-align: center;
}

.child-actions :deep(.el-button) {
  background-color: transparent !important;
  border: none !important;
  padding: 0 4px;
  box-shadow: none !important;
}

.add-child-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #409eff;
  margin-left: 8px;
}

.add-child-link:hover {
  color: #66b1ff;
}

.child-actions :deep(.el-button) {
  color: #f56c6c;
}

.child-actions :deep(.el-button:hover) {
  color: #f78989;
  background-color: transparent;
}

.quick-create-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  margin-left: 28px;
  border-radius: 6px;
  border: 1px solid #dcdfe6;
  margin-top: 8px;
  background: #fafafa;
}
.children-empty {
  font-size: 13px;
  color: #c0c4cc;
  padding: 8px 10px;
  margin-left: 28px;
}
</style>
