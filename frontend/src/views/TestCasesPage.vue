<template>
  <div class="testcases-page">
    <!-- 顶部：标题、搜索框、创建按钮同一行 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Document /></el-icon>
          用例详情
        </h2>
      </div>
      <div class="filter-row">
        <el-select 
          v-model="filters.project_id" 
          placeholder="选择项目" 
          clearable 
          style="width: 200px" 
          @change="handleProjectChange"
          :disabled="hasProjectSelected"
          :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
        >
          <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
        </el-select>
        <el-input
          v-model="testcaseSearchKeyword"
          placeholder="搜索用例ID或标题"
          clearable
          @keyup.enter="handleTestCaseSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="handleTestCaseSearch">搜索</el-button>
        <el-button @click="testcaseSearchKeyword = ''; handleTestCaseSearch()">重置</el-button>
        <div style="flex-grow: 1;"></div>
        <el-button 
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新建用例
        </el-button>
        <el-button type="primary" @click="handleSmartGenerate">
          <el-icon><MagicStick /></el-icon>
          智能生成
        </el-button>
      </div>
    </el-card>

    <!-- 左右分栏布局 -->
    <div class="testcases-layout">
      <!-- 左侧：目录树 -->
      <div class="directory-sidebar" :style="{ width: sidebarWidth + 'px' }">
        <el-card class="directory-card">
          <div class="directory-header">
            <el-button 
              type="primary" 
              size="default" 
              @click="handleAddMainDirectory"
              style="width: 100%; margin-bottom: 16px;"
            >
              <el-icon><Plus /></el-icon>
              创建主分组
            </el-button>
            <el-input
              v-model="directorySearchKeyword"
              placeholder="搜索分组"
              clearable
              size="default"
              @input="handleDirectorySearch"
              class="directory-search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div class="directory-tree-container" v-loading="loading">
            <el-tree
              ref="directoryTreeRef"
              :data="directoryTreeData"
              :props="directoryTreeProps"
              :default-expand-all="false"
              :expand-on-click-node="true"
              node-key="id"
              class="directory-tree"
              :filter-node-method="filterDirectoryNode"
              :highlight-current="true"
              @node-click="handleDirectoryNodeClick"
            >
              <template #default="{ node, data }">
                <div class="directory-node-wrapper">
                  <div class="directory-node-content">
                    <el-icon class="directory-folder-icon" :class="{ 'is-expanded': node.expanded, 'is-leaf': !data.children || data.children.length === 0 }">
                      <FolderOpened v-if="node.expanded" />
                      <Folder v-else />
                    </el-icon>
                    <span class="directory-node-label">{{ data.label }}</span>
                  </div>
                  <div class="directory-node-actions" @click.stop>
                    <el-button
                      link
                      type="primary"
                      size="small"
                      @click.stop="handleAddSubDirectory(data)"
                      title="新建子分组"
                      class="directory-action-btn"
                    >
                      <el-icon><Plus /></el-icon>
                    </el-button>
                    <el-button
                      v-if="data.path"
                      link
                      type="primary"
                      size="small"
                      @click.stop="handleEditDirectory(data)"
                      title="重命名分组"
                      class="directory-action-btn"
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                    <el-button
                      v-if="data.path"
                      link
                      type="danger"
                      size="small"
                      @click.stop="handleDeleteDirectory(data)"
                      title="删除分组"
                      class="directory-action-btn"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </template>
            </el-tree>
          </div>
        </el-card>
      </div>
      
      <!-- 分割条 -->
      <div 
        class="resize-handle" 
        @mousedown="handleResizeStart"
        @dblclick="handleResizeReset"
        title="拖拽调整宽度，双击重置"
      ></div>

      <!-- 右侧：用例列表 -->
      <div class="testcases-main" :style="{ width: `calc(100% - ${sidebarWidth + 20}px)` }">
        <!-- 用例列表（表格） -->
        <el-card class="testcases-list-card">
          <div style="flex: 1; min-height: 0; display: flex; flex-direction: column;">
            <el-table
              :data="paginatedTestCases"
              v-loading="loading"
              stripe
              style="flex: 1;"
              @row-click="handleRowClick"
              :row-style="{ cursor: 'pointer' }"
            >
            <el-table-column label="编号" width="160">
              <template #default="{ row }">
                {{ row.case_key }}
              </template>
            </el-table-column>
            <el-table-column prop="title" label="用例名称" min-width="350" show-overflow-tooltip />
            <el-table-column prop="priority" label="等级" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getPriorityTag(row.priority)" size="small">{{ row.priority || 'P2' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建人" width="120">
              <template #default="{ row }">
                {{ row.creator?.display_name || row.creator?.username || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click.stop="handleCopy(row)" class="table-action-btn">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
                <el-button
                  link
                  type="danger"
                  @click.stop="handleDelete(row)"
                  class="table-action-btn"
                >
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
            </el-table>
            
            <div style="margin-top: 16px; text-align: right; flex-shrink: 0;">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                layout="prev, pager, next, sizes, jumper, ->, total"
                :total="filteredTestCases.length"
              />
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 智能生成对话框 -->
    <el-dialog
      v-model="smartGenerateDialogVisible"
      width="600px"
      :close-on-click-modal="true"
    >
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">智能生成测试用例</span>
          <span class="dialog-description">上传设计原型图片，系统将自动分析并生成对应的测试用例</span>
        </div>
      </template>
      <el-form :model="smartGenerateForm" label-position="top" style="padding: 0 20px;">
        <el-form-item label="选择项目" required>
          <el-select 
            v-model="smartGenerateForm.project_id" 
            placeholder="选择项目" 
            style="width: 100%"
            :disabled="hasProjectSelected"
            :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
          >
            <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="是否调用大模型解析">
          <el-switch 
            v-model="smartGenerateForm.use_model" 
            active-text="是" 
            inactive-text="否"
            @change="handleUseModelChange"
          />
        </el-form-item>
        
        <el-form-item 
          v-if="smartGenerateForm.use_model" 
          label="选择模型" 
          required
        >
          <el-select 
            v-model="smartGenerateForm.model_id" 
            placeholder="选择模型" 
            style="width: 100%"
            :loading="loadingModels"
          >
            <el-option 
              v-for="model in availableModels" 
              :key="model.id" 
              :label="model.name" 
              :value="model.id"
            >
              <span>{{ model.name }}</span>
              <span style="color: #909399; font-size: 12px; margin-left: 8px;">
                ({{ model.provider === 'openai' ? 'OpenAI' : model.provider === 'deepseek' ? 'DeepSeek' : model.provider === 'qwen' ? '通义千问' : model.provider === 'doubao' ? '豆包' : '本地' }})
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="上传设计原型图片" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleImageChange"
            :limit="1"
            accept="image/*"
            drag
            :file-list="imageFileList"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              拖拽图片到此处或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 JPG、PNG 等图片格式，建议上传清晰的设计原型图
              </div>
            </template>
          </el-upload>
          
          <!-- 图片预览 -->
          <div v-if="imagePreview" style="margin-top: 16px; text-align: center;">
            <img :src="imagePreview" alt="预览" style="max-width: 100%; max-height: 300px; border-radius: 8px; border: 1px solid #e4e7ed;" />
          </div>
        </el-form-item>
        
        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 16px;"
        >
          <template #title>
            <div style="font-size: 13px;">
              <strong>功能说明：</strong>上传设计原型图片后，系统将使用AI分析图片内容，自动生成对应的测试用例，包括用例标题、步骤描述和预期结果。
            </div>
          </template>
        </el-alert>
      </el-form>
      
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="handleCloseSmartGenerate">取消</el-button>
          <el-button type="primary" :loading="smartGenerating" @click="handleSubmitSmartGenerate">
            <el-icon><MagicStick /></el-icon>
            {{ smartGenerating ? '生成中...' : '开始生成' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 创建/编辑抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="isEdit ? '编辑用例' : '新建用例'"
      direction="rtl"
      size="70%"
      :close-on-click-modal="true"
    >
      <el-row :gutter="24" class="testcase-drawer-row">
        <!-- 左侧：标题、前置条件和步骤 -->
        <el-col :span="18" class="drawer-left-col">
          <!-- 标题 -->
          <div class="section-block" style="margin-bottom: 24px;">
            <div class="section-title">标题</div>
            <el-input v-model="formData.title" placeholder="请输入用例标题" />
          </div>
          
          <!-- 前置条件 -->
          <div class="section-block" style="margin-top: 0;">
            <div class="section-title">前置条件</div>
            <el-input 
              v-model="formData.precondition" 
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
            <div class="steps-table" v-if="formData.steps && formData.steps.length > 0">
              <!-- 表头 -->
              <div class="steps-table-header">
                <div class="header-cell header-cell-number">#</div>
                <div class="header-cell header-cell-step">步骤</div>
                <div class="header-cell header-cell-expected">预期</div>
                <div class="header-cell header-cell-action">操作</div>
              </div>
              
              <!-- 表格内容 -->
              <div 
                v-for="(step, index) in formData.steps" 
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
                <div class="table-cell table-cell-action">
                  <el-button 
                    @click="removeStep(index)" 
                    type="danger" 
                    link 
                    size="small"
                    class="step-delete-btn"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
            
            <el-empty v-else description="暂无步骤，请添加步骤" :image-size="80" style="margin: 20px 0;" />
            
            <!-- 增加步骤按钮 -->
            <el-button 
              @click="addStep" 
              type="primary" 
              plain 
              size="default" 
              class="add-step-btn"
              style="width: 100%; margin-top: 16px;"
            >
              <el-icon><Plus /></el-icon>
              <span>增加步骤</span>
            </el-button>
          </div>
        </el-col>
        
        <!-- 右侧：项目、类型、等级和修改记录 -->
        <el-col :span="6" class="drawer-right-col">
          <div class="right-section">
            <!-- 基本信息 -->
            <div class="section-block">
              <el-form :model="formData" label-position="top" class="right-form">
                <el-form-item label="项目" required>
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
                <el-form-item label="分组">
                  <el-select 
                    v-model="formData.module" 
                    placeholder="请选择分组（只能选择最内层分组）" 
                    style="width: 100%"
                    filterable
                    clearable
                  >
                    <el-option
                      v-for="option in directorySelectOptions"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                      :disabled="!option.isLeaf"
                    >
                      <span :style="{ whiteSpace: 'pre', color: option.isLeaf ? 'inherit' : '#c0c4cc' }">{{ option.label }}</span>
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="类型">
                  <el-select v-model="formData.type" placeholder="选择类型" style="width: 100%">
                    <el-option label="功能" value="functional" />
                    <el-option label="非功能" value="non-functional" />
                  </el-select>
                </el-form-item>
                <el-form-item label="等级">
                  <el-select v-model="formData.priority" placeholder="选择等级" style="width: 100%">
                    <el-option label="P0" value="P0" />
                    <el-option label="P1" value="P1" />
                    <el-option label="P2" value="P2" />
                    <el-option label="P3" value="P3" />
                    <el-option label="P4" value="P4" />
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
            
            <!-- 修改记录 -->
            <div class="section-block" style="margin-top: 24px;">
              <div class="section-title">修改记录</div>
              <div class="info-section">
                <div class="info-item" v-if="formData.created_by && formData.created_at">
                  <el-avatar :size="32" class="info-avatar">
                    {{ getInitials(formData.created_by) }}
                  </el-avatar>
                  <div class="info-text">
                    <div class="info-name">{{ getCreatorName(formData.created_by) }}</div>
                    <div class="info-time">创建于 {{ formatRelativeTime(formData.created_at) }}</div>
                  </div>
                </div>
                <div class="info-item" v-if="formData.updated_by && formData.updated_at">
                  <el-avatar :size="32" class="info-avatar">
                    {{ getInitials(formData.updated_by) }}
                  </el-avatar>
                  <div class="info-text">
                    <div class="info-name">{{ getUpdaterName(formData.updated_by) }}</div>
                    <div class="info-time">最后修改于 {{ formatRelativeTime(formData.updated_at) }}</div>
                  </div>
                </div>
                <div v-if="!formData.created_by" class="info-empty">
                  暂无记录
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 底部操作按钮 -->
      <template #footer>
        <div class="drawer-footer">
          <el-button type="primary" @click="handleSaveAndClose">保存并关闭</el-button>
          <el-button @click="handleSaveAndNext">保存并下一个</el-button>
          <el-button @click="handleSaveAndNew">保存并新建</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, Document, MagicStick, UploadFilled, Folder, FolderOpened, CopyDocument } from '@element-plus/icons-vue'
import * as testcaseApi from '@/api/testcases'
import * as projectApi from '@/api/projects'
import * as modelApi from '@/api/models'
import * as userApi from '@/api/users'
import type { TestCase, Project, User } from '@/api/types'
import { usePermissions } from '@/composables/usePermissions'
import { useProjectContext } from '@/composables/useProjectContext'

const { canCreate, canUpdate, canDelete, getCurrentUser } = usePermissions()

const testcases = ref<TestCase[]>([])
const projects = ref<Project[]>([])
const users = ref<User[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const drawerVisible = ref(false)
const isEdit = ref(false)
const smartGenerateDialogVisible = ref(false)
const smartGenerating = ref(false)
const uploadRef = ref()
const imageFileList = ref<any[]>([])
const imagePreview = ref<string>('')
const selectedImageFile = ref<File | null>(null)

const smartGenerateForm = ref({
  project_id: undefined as number | undefined,
  use_model: false,
  model_id: undefined as number | undefined
})

const availableModels = ref<any[]>([])
const loadingModels = ref(false)

const filters = ref({
  project_id: undefined as number | undefined,
  priority: '' as string,
  status: '' as string,
  search: ''
})

const formData = ref<Partial<TestCase>>({
  project_id: undefined,
  title: '',
  module: '',
  description: '',
  precondition: '',
  steps: [],
  expected_result: '',
  type: 'functional',
  priority: 'P2',
  status: 'draft',
  tags: []
})

const attachmentList = ref<any[]>([])
const directoryTreeRef = ref()
const directorySearchKeyword = ref('')
const testcaseSearchKeyword = ref('')
const selectedDirectoryPath = ref<string | null>(null)
const sidebarWidth = ref(280) // 左侧分组栏宽度，默认280px
const isResizing = ref(false)
const resizeStartX = ref(0)
const resizeStartWidth = ref(0)

// 目录树节点接口
interface DirectoryTreeNode {
  id: string
  label: string
  path: string | null  // null表示根目录
  count: number
  children?: DirectoryTreeNode[]
}

const directoryTreeProps = {
  children: 'children',
  label: 'label'
}

let isMounted = false

const fetchTestCases = async () => {
  if (!isMounted) return
  loading.value = true
  try {
    const params: any = {}
    
    // 优先使用当前项目过滤
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      params.project_id = getCurrentProjectId.value
    } else if (filters.value.project_id) {
      params.project_id = filters.value.project_id
    }
    
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.search) params.search = filters.value.search
    
    testcases.value = await testcaseApi.getTestCases(params)
  } catch (error) {
    if (isMounted) {
      ElMessage.error('获取用例列表失败')
    }
  } finally {
    if (isMounted) {
      loading.value = false
    }
  }
}

const paginatedTestcases = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return testcases.value.slice(start, start + pageSize.value)
})

// 构建目录树（从用例的module字段提取）
const buildDirectoryTree = (testcases: TestCase[]): DirectoryTreeNode[] => {
  const directoryMap = new Map<string, { count: number, pathParts: string[] }>()
  
  // 统计每个目录下的用例数量（包含占位用例用于显示目录结构，但计数时排除占位用例）
  testcases.forEach(testcase => {
    const modulePath = testcase.module || ''
    if (!modulePath) {
      // 没有module的用例，跳过（不显示在目录树中）
      return
    }
    
    const pathParts = modulePath.split('/').filter(p => p.trim())
    // 为每个路径层级创建条目
    let currentPath = ''
    pathParts.forEach((part, index) => {
      currentPath = currentPath ? `${currentPath}/${part}` : part
      if (!directoryMap.has(currentPath)) {
        directoryMap.set(currentPath, { count: 0, pathParts: pathParts.slice(0, index + 1) })
      }
      // 如果是完整的路径（最后一部分），且不是占位用例，计数加1
      if (index === pathParts.length - 1 && !testcase.title?.startsWith('[目录占位]')) {
        directoryMap.get(currentPath)!.count++
      }
    })
  })
  
  // 构建树形结构（不包含根节点）
  const rootNodes: DirectoryTreeNode[] = []
  const nodeMap = new Map<string, DirectoryTreeNode>()
  
  Array.from(directoryMap.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .forEach(([path, { count, pathParts }]) => {
      if (!path) {
        // 根目录下的用例，跳过（不显示）
        return
      }
      
      // 找到或创建所有父节点
      let currentPath = ''
      let parent: DirectoryTreeNode | null = null
      
      pathParts.forEach((part, index) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part
        
        if (!nodeMap.has(currentPath)) {
          const node: DirectoryTreeNode = {
            id: `dir-${currentPath}`,
            label: part,
            path: currentPath,
            count: 0,  // 初始化为0，后面统一计算
            children: []
          }
          nodeMap.set(currentPath, node)
          
          if (parent) {
            if (!parent.children) parent.children = []
            parent.children.push(node)
          } else {
            // 这是顶级目录
            rootNodes.push(node)
          }
        }
        
        // 如果是叶子节点（最后一部分），累加计数
        if (index === pathParts.length - 1) {
          const node = nodeMap.get(currentPath)!
          node.count += count
        }
        
        parent = nodeMap.get(currentPath)!
      })
    })
  
  // 递归计算每个目录下所有叶子节点的用例总数
  // 每个分组显示的是：该分组下所有叶子节点分组的用例总数
  // 对于叶子节点：显示自己的用例数
  // 对于中间节点：显示所有子分组（递归到叶子节点）的用例总数
  const calculateLeafNodesTotalCount = (node: DirectoryTreeNode): number => {
    // 如果是叶子节点，返回自己的用例数
    if (!node.children || node.children.length === 0) {
      return node.count || 0
    }
    
    // 如果是中间节点，递归计算所有子节点（叶子节点）的用例总数
    let total = 0
    node.children.forEach(child => {
      total += calculateLeafNodesTotalCount(child)
    })
    return total
  }
  
  // 更新计数：每个分组显示该分组所有叶子节点分组的用例总数
  const updateCounts = (nodes: DirectoryTreeNode[]) => {
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        // 先递归处理子节点
        updateCounts(node.children)
        // 计算该分组下所有叶子节点分组的用例总数
        node.count = calculateLeafNodesTotalCount(node)
      }
      // 叶子节点（没有子节点）：保持自己的直接用例数，不修改
    })
  }
  
  if (rootNodes.length > 0) {
    updateCounts(rootNodes)
  }
  
  return rootNodes
}

// 目录树数据
const directoryTreeData = computed(() => {
  return buildDirectoryTree(testcases.value)
})

// 将目录树转换为选择器选项（扁平化，带缩进显示，显示完整树状结构）
const flattenDirectoryTree = (nodes: DirectoryTreeNode[], level: number = 0): Array<{ label: string, value: string, path: string, isLeaf: boolean }> => {
  const options: Array<{ label: string, value: string, path: string, isLeaf: boolean }> = []
  nodes.forEach(node => {
    // 判断是否是叶子节点
    const isLeaf = !node.children || node.children.length === 0
    // 使用空格缩进显示层级关系
    const indent = '  '.repeat(level) // 每级缩进2个空格
    options.push({
      label: `${indent}${node.label}`,
      value: node.path || '',
      path: node.path || '',
      isLeaf: isLeaf
    })
    // 如果有子节点，递归处理子节点
    if (node.children && node.children.length > 0) {
      options.push(...flattenDirectoryTree(node.children, level + 1))
    }
  })
  return options
}

// 目录选择器选项
const directorySelectOptions = computed(() => {
  return flattenDirectoryTree(directoryTreeData.value)
})

// 根据选中的目录过滤用例
const filteredTestCases = computed(() => {
  let filtered = testcases.value
  
  // 过滤掉占位用例（标题以"[目录占位]"开头的）
  filtered = filtered.filter(tc => !tc.title?.startsWith('[目录占位]'))
  
  // 根据选中目录过滤
  if (selectedDirectoryPath.value !== null) {
    filtered = filtered.filter(testcase => {
      const modulePath = testcase.module || ''
      // 精确匹配路径
      return modulePath === selectedDirectoryPath.value
    })
  }
  
  // 根据优先级过滤
  if (filters.value.priority) {
    filtered = filtered.filter(tc => tc.priority === filters.value.priority)
  }
  
  // 根据状态过滤
  if (filters.value.status) {
    filtered = filtered.filter(tc => tc.status === filters.value.status)
  }
  
  // 根据搜索关键字过滤
  if (testcaseSearchKeyword.value) {
    const keyword = testcaseSearchKeyword.value.toLowerCase()
    filtered = filtered.filter(tc => {
      const caseKey = tc.case_key?.toLowerCase() || ''
      const title = tc.title?.toLowerCase() || ''
      return caseKey.includes(keyword) || title.includes(keyword)
    })
  }
  
  return filtered
})

// 分页用例列表
const paginatedTestCases = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredTestCases.value.slice(start, start + pageSize.value)
})

// 获取当前目录名称
const getCurrentDirectoryName = () => {
  if (selectedDirectoryPath.value === null) {
    return '全部用例'
  }
  const parts = selectedDirectoryPath.value.split('/')
  return parts[parts.length - 1] || '全部用例'
}

// 目录搜索
const handleDirectorySearch = () => {
  nextTick(() => {
    if (directoryTreeRef.value) {
      directoryTreeRef.value.filter(directorySearchKeyword.value)
    }
  })
}

watch(directorySearchKeyword, () => {
  handleDirectorySearch()
})

// 监听选中的分组路径变化，更新表单中的分组字段（仅在创建模式下）
watch(selectedDirectoryPath, (newPath) => {
  if (!isEdit.value && drawerVisible.value) {
    formData.value.module = newPath || ''
  }
})

const filterDirectoryNode = (value: string, data: DirectoryTreeNode) => {
  if (!value) return true
  return data.label.toLowerCase().includes(value.toLowerCase())
}

// 判断节点是否是叶子节点（没有子节点）
const isLeafNode = (node: DirectoryTreeNode): boolean => {
  return !node.children || node.children.length === 0
}

// 在目录树数据中查找节点
const findNodeByPath = (nodes: DirectoryTreeNode[], path: string | null): DirectoryTreeNode | null => {
  if (!path) return null
  for (const node of nodes) {
    if (node.path === path) {
      return node
    }
    if (node.children && node.children.length > 0) {
      const found = findNodeByPath(node.children, path)
      if (found) return found
    }
  }
  return null
}

// 目录节点点击事件
const handleDirectoryNodeClick = (data: DirectoryTreeNode) => {
  selectedDirectoryPath.value = data.path
  currentPage.value = 1
  // 如果正在创建用例，更新表单中的分组字段
  if (!isEdit.value && drawerVisible.value) {
    formData.value.module = data.path || ''
  }
}

// 新增主分组
const handleAddMainDirectory = async () => {
  try {
    const { value } = await ElMessageBox.prompt('输入主分组名称', '新建主分组', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入目录名称',
      inputValidator: (value) => {
        if (!value || !value.trim()) {
          return '目录名称不能为空'
        }
        if (value.includes('/')) {
          return '目录名称不能包含"/"'
        }
        return true
      }
    })
    
    if (value) {
      const newDirectoryName = value.trim()
      const newPath = newDirectoryName
      
      // 创建占位用例来让目录显示出来
      const currentUser = getCurrentUser()
      if (!currentUser) {
        ElMessage.error('请先登录')
        return
      }
      
      if (!hasProjectSelected.value || !getCurrentProjectId.value) {
        ElMessage.warning('请先选择项目')
        return
      }
      
      // 检查目录是否已存在
      const existingTestCases = testcases.value.filter(tc => {
        const modulePath = tc.module || ''
        return modulePath === newPath || modulePath.startsWith(`${newPath}/`)
      })
      
      if (existingTestCases.length > 0) {
        ElMessage.warning('该分组已存在')
        return
      }
      
      // 创建占位用例
      await testcaseApi.createTestCase({
        project_id: getCurrentProjectId.value,
        title: `[目录占位] ${newDirectoryName}`,
        module: newPath,
        description: '',
        precondition: '',
        steps: [],
        expected_result: '',
        type: 'functional',
        priority: 'P2',
        status: 'draft',
        tags: [],
        created_by: currentUser.user_id
      })
      
      selectedDirectoryPath.value = newPath
      ElMessage.success('分组已创建')
      // 刷新用例列表以更新目录树
      await fetchTestCases()
      // 等待DOM更新后，选中新创建的目录节点
      await nextTick()
      if (directoryTreeRef.value) {
        const nodeId = `dir-${newPath}`
        directoryTreeRef.value.setCurrentKey(nodeId)
      }
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '创建分组失败'
      ElMessage.error(errorMessage)
      console.error('创建分组失败:', error)
    }
  }
}

// 新增子目录
const handleAddSubDirectory = async (parentNode: DirectoryTreeNode) => {
  try {
    const { value } = await ElMessageBox.prompt('输入子分组名称', '新建子分组', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入目录名称',
      inputValidator: (value) => {
        if (!value || !value.trim()) {
          return '目录名称不能为空'
        }
        if (value.includes('/')) {
          return '目录名称不能包含"/"'
        }
        return true
      }
    })
    
    if (value) {
      const newDirectoryName = value.trim()
      const newPath = parentNode.path 
        ? `${parentNode.path}/${newDirectoryName}`
        : newDirectoryName
      
      // 创建占位用例来让目录显示出来
      const currentUser = getCurrentUser()
      if (!currentUser) {
        ElMessage.error('请先登录')
        return
      }
      
      if (!hasProjectSelected.value || !getCurrentProjectId.value) {
        ElMessage.warning('请先选择项目')
        return
      }
      
      // 检查目录是否已存在
      const existingTestCases = testcases.value.filter(tc => {
        const modulePath = tc.module || ''
        return modulePath === newPath || modulePath.startsWith(`${newPath}/`)
      })
      
      if (existingTestCases.length > 0) {
        ElMessage.warning('该分组已存在')
        return
      }
      
      // 创建占位用例
      await testcaseApi.createTestCase({
        project_id: getCurrentProjectId.value,
        title: `[目录占位] ${newDirectoryName}`,
        module: newPath,
        description: '',
        precondition: '',
        steps: [],
        expected_result: '',
        type: 'functional',
        priority: 'P2',
        status: 'draft',
        tags: [],
        created_by: currentUser.user_id
      })
      
      selectedDirectoryPath.value = newPath
      ElMessage.success('分组已创建')
      // 刷新用例列表以更新目录树
      await fetchTestCases()
      // 等待DOM更新后，选中新创建的目录节点
      await nextTick()
      if (directoryTreeRef.value) {
        const nodeId = `dir-${newPath}`
        directoryTreeRef.value.setCurrentKey(nodeId)
      }
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '创建分组失败'
      ElMessage.error(errorMessage)
      console.error('创建分组失败:', error)
    }
  }
}

// 编辑目录（重命名分组）
const handleEditDirectory = async (node: DirectoryTreeNode) => {
  if (!node.path) {
    ElMessage.warning('不能重命名根分组')
    return
  }
  
  try {
    const { value } = await ElMessageBox.prompt('输入新的分组名称', '重命名分组', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入新的分组名称',
      inputValue: node.label,
      inputValidator: (value) => {
        if (!value || !value.trim()) {
          return '分组名称不能为空'
        }
        if (value.includes('/')) {
          return '分组名称不能包含"/"'
        }
        return true
      }
    })
    
    if (value) {
      const newDirectoryName = value.trim()
      
      // 如果名称没有改变，直接返回
      if (newDirectoryName === node.label) {
        return
      }
      
      const pathParts = node.path.split('/')
      pathParts[pathParts.length - 1] = newDirectoryName
      const newPath = pathParts.join('/')
      
      // 检查新路径是否已存在（排除当前路径及其子路径）
      const existingTestCases = testcases.value.filter(tc => {
        const modulePath = tc.module || ''
        // 如果新路径和旧路径相同，说明只是名称相同但路径相同，允许
        if (newPath === node.path) {
          return false
        }
        // 检查是否有其他分组使用新路径
        return (modulePath === newPath || modulePath.startsWith(`${newPath}/`)) && 
               !modulePath.startsWith(node.path)
      })
      
      if (existingTestCases.length > 0) {
        ElMessage.warning('该分组名称已存在')
        return
      }
      
      // 找到所有使用该分组路径的用例（包括子分组）
      const directoryTestCases = testcases.value.filter(tc => {
        const modulePath = tc.module || ''
        return modulePath === node.path || modulePath.startsWith(`${node.path}/`)
      })
      
      if (directoryTestCases.length === 0) {
        ElMessage.info('该分组下没有用例')
        return
      }
      
      const currentUser = getCurrentUser()
      if (!currentUser) {
        ElMessage.error('请先登录')
        return
      }
      
      // 更新所有相关用例的 module 字段
      let successCount = 0
      let failCount = 0
      
      for (const testcase of directoryTestCases) {
        if (!testcase.id || !testcase.module) continue
        
        try {
          // 替换路径：将旧路径替换为新路径
          const oldModulePath = testcase.module
          const newModulePath = oldModulePath.replace(node.path, newPath)
          
          await testcaseApi.updateTestCase(testcase.id, {
            ...testcase,
            module: newModulePath,
            updated_by: currentUser.user_id
          })
          successCount++
        } catch (error: any) {
          console.error('更新用例失败:', error)
          failCount++
        }
      }
      
      if (successCount > 0) {
        ElMessage.success(`成功重命名 ${successCount} 个用例的分组路径`)
        
        // 如果当前选中的是重命名的分组，更新选中状态
        if (selectedDirectoryPath.value === node.path) {
          selectedDirectoryPath.value = newPath
        } else if (selectedDirectoryPath.value?.startsWith(`${node.path}/`)) {
          // 如果选中的是子分组，也要更新路径
          selectedDirectoryPath.value = selectedDirectoryPath.value.replace(node.path, newPath)
        }
        
        // 刷新用例列表以更新目录树
        await fetchTestCases()
        
        // 等待DOM更新后，选中重命名后的目录节点
        await nextTick()
        if (directoryTreeRef.value) {
          const nodeId = `dir-${newPath}`
          directoryTreeRef.value.setCurrentKey(nodeId)
        }
      }
      
      if (failCount > 0) {
        ElMessage.warning(`${failCount} 个用例更新失败`)
      }
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '重命名分组失败'
      ElMessage.error(errorMessage)
      console.error('重命名分组失败:', error)
    }
  }
}

// 删除目录（实际上是删除该目录下的所有用例）
const handleDeleteDirectory = async (node: DirectoryTreeNode) => {
  if (!node.path) {
    ElMessage.warning('不能删除根分组')
    return
  }
  
  // 找到该目录下的所有用例
  const directoryTestCases = testcases.value.filter(tc => {
    const modulePath = tc.module || ''
    return modulePath === node.path || modulePath.startsWith(`${node.path}/`)
  })
  
  if (directoryTestCases.length === 0) {
    ElMessage.info('该目录为空，无需删除')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除分组"${node.label}"吗？这将删除该分组下的 ${directoryTestCases.length} 个用例。`,
      '删除分组',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 删除该目录下的所有用例
    for (const testcase of directoryTestCases) {
      if (testcase.id) {
        await testcaseApi.deleteTestCase(testcase.id)
      }
    }
    
    ElMessage.success('目录及用例删除成功')
    fetchTestCases()
  } catch {
    // 取消操作
  }
}

// 用例搜索
const handleTestCaseSearch = () => {
  currentPage.value = 1
}

// 处理项目变更
const handleProjectChange = () => {
  currentPage.value = 1
  fetchTestCases()
}

watch(testcaseSearchKeyword, () => {
  handleTestCaseSearch()
})


// 表格行点击事件
const handleRowClick = (row: TestCase) => {
  handleEdit(row)
}

// 筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
}

const handleReset = () => {
  filters.value = {
    project_id: undefined,
    priority: '',
    search: ''
  }
  fetchTestCases()
}

const { 
  getProjects: getFilteredProjects,
  getCurrentProjectId,
  hasProjectSelected,
  onProjectChanged,
  ensureInitialized
} = useProjectContext()

const fetchProjects = async () => {
  try {
    // 使用 useProjectContext 的 getProjects，会自动根据选中的项目过滤
    projects.value = await getFilteredProjects()
    
    // 如果有选中的项目，自动设置过滤器并禁用下拉框
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.value.project_id = getCurrentProjectId.value
    } else {
      // 如果没有选中的项目，清空过滤器
      filters.value.project_id = undefined
    }
  } catch (error) {
    ElMessage.error('获取项目列表失败')
  }
}

const fetchUsers = async () => {
  try {
    users.value = await userApi.getUsers({ status: 'active' })
  } catch (error) {
    // 忽略错误，避免影响用例列表加载
  }
}

const handleCreate = () => {
  // 检查是否选择了分组
  if (!selectedDirectoryPath.value) {
    ElMessage.warning('请先选择一个分组')
    return
  }
  
  // 检查选中的分组是否是叶子节点（只有叶子节点才能新建用例）
  const selectedNode = findNodeByPath(directoryTreeData.value, selectedDirectoryPath.value)
  if (!selectedNode) {
    ElMessage.warning('请先选择一个有效的分组')
    return
  }
  
  if (!isLeafNode(selectedNode)) {
    ElMessage.warning('只能在最内层的分组（叶子节点）中新建用例，请选择最内层的分组')
    return
  }
  
  isEdit.value = false
  formData.value = {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : undefined,
    title: '',
    module: selectedDirectoryPath.value || '',  // 自动关联到选中的分组（包含所有层目录结构）
    description: '',
    precondition: '',
    steps: [{ description: '', expected_result: '' }],
    expected_result: '',
    type: 'functional',
    priority: 'P2',
    status: 'draft',
    tags: []
  }
  attachmentList.value = []
  drawerVisible.value = true
}

const handleEdit = (testcase: TestCase) => {
  isEdit.value = true
  // 使用深拷贝避免引用问题
  formData.value = {
    ...testcase,
    description: (testcase as any).description || '',
    steps: testcase.steps ? JSON.parse(JSON.stringify(testcase.steps)) : []
  }
  attachmentList.value = []
  drawerVisible.value = true
}

// 复制用例
const handleCopy = (testcase: TestCase) => {
  isEdit.value = false
  // 使用深拷贝避免引用问题，并清除 id 以创建新用例
  const copiedData = {
    ...testcase,
    description: (testcase as any).description || '',
    steps: testcase.steps ? JSON.parse(JSON.stringify(testcase.steps)) : []
  }
  // 移除 id，这样保存时会创建新用例
  delete (copiedData as any).id
  // 修改标题，添加"副本"标识
  copiedData.title = `${copiedData.title} (副本)`
  formData.value = copiedData
  attachmentList.value = []
  drawerVisible.value = true
  ElMessage.success('已复制用例，请修改后保存')
}

const handleSave = async () => {
  if (!formData.value.title || !formData.value.project_id) {
    ElMessage.warning('请填写必填项：项目和标题')
    return
  }

  // 校验分组：只有叶子节点才能关联用例
  if (formData.value.module) {
    const selectedNode = findNodeByPath(directoryTreeData.value, formData.value.module)
    if (!selectedNode) {
      ElMessage.warning('请选择有效的分组')
      return
    }
    if (!isLeafNode(selectedNode)) {
      ElMessage.warning('只能在最内层的分组（叶子节点）中添加用例，请选择最内层的分组')
      return
    }
  }

  const currentUser = getCurrentUser()
  if (!currentUser) {
    ElMessage.error('请先登录')
    return
  }

  try {
    if (isEdit.value && formData.value.id) {
      await testcaseApi.updateTestCase(formData.value.id, {
        ...formData.value,
        updated_by: currentUser.user_id
      })
      ElMessage.success('用例更新成功')
    } else {
      await testcaseApi.createTestCase({
        ...formData.value,
        created_by: currentUser.user_id
      })
      ElMessage.success('用例创建成功')
    }
    fetchTestCases()
    return true
  } catch (error: any) {
    console.error('保存错误:', error)
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
    return false
  }
}

const handleClose = () => {
  drawerVisible.value = false
}

const handleSaveAndNext = async () => {
  const success = await handleSave()
  if (success && isEdit.value && formData.value.id) {
    // 找到当前用例在列表中的索引
    const currentIndex = testcases.value.findIndex(tc => tc.id === formData.value.id)
    
    // 如果找到了当前用例，且不是最后一个
    if (currentIndex >= 0 && currentIndex < testcases.value.length - 1) {
      const nextTestCase = testcases.value[currentIndex + 1]
      ElMessage.success('保存成功，进入下一个用例')
      handleEdit(nextTestCase)
    } else {
      ElMessage.info('已是最后一个用例')
      drawerVisible.value = false
    }
  } else if (success) {
    // 如果是新建，就关闭抽屉
    drawerVisible.value = false
    ElMessage.success('保存成功')
  }
}

const handleSaveAndClose = async () => {
  const success = await handleSave()
  if (success) {
    drawerVisible.value = false
  }
}

const handleSaveAndNew = async () => {
  const success = await handleSave()
  if (success) {
    handleCreate()
  }
}

const handleAttachmentChange = (file: any) => {
  attachmentList.value.push(file)
}

const getInitials = (userId: number) => {
  const user = users.value.find(u => u.id === userId)
  if (user && user.display_name) {
    return user.display_name.charAt(0).toUpperCase()
  } else if (user && user.username) {
    return user.username.charAt(0).toUpperCase()
  }
  return 'U'
}

const getCreatorName = (userId: number) => {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    return user.display_name || user.username || '用户'
  }
  return '用户'
}

const getUpdaterName = (userId: number) => {
  const user = users.value.find(u => u.id === userId)
  if (user) {
    return user.display_name || user.username || '用户'
  }
  return '用户'
}

const formatRelativeTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const years = Math.floor(days / 365)
  
  if (years > 0) {
    return `${years} 年前`
  } else if (days > 0) {
    return `${days} 天前`
  } else {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours > 0) {
      return `${hours} 小时前`
    } else {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes > 0 ? `${minutes} 分钟前` : '刚刚'
    }
  }
}

const handleDelete = async (testcase: TestCase) => {
  try {
    await ElMessageBox.confirm('确定要删除这个用例吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await testcaseApi.deleteTestCase(testcase.id)
    ElMessage.success('删除成功')
    fetchTestCases()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const handleSmartGenerate = async () => {
  smartGenerateForm.value = {
    project_id: hasProjectSelected.value ? getCurrentProjectId.value : undefined,
    use_model: false,
    model_id: undefined
  }
  imageFileList.value = []
  imagePreview.value = ''
  selectedImageFile.value = null
  availableModels.value = []
  smartGenerateDialogVisible.value = true
  
  // 加载模型列表
  await fetchModels()
}

const fetchModels = async () => {
  loadingModels.value = true
  try {
    const models = await modelApi.getModels()
    // 只显示启用状态的模型
    availableModels.value = models.filter((m: any) => m.status === 'active')
  } catch (error: any) {
    console.error('获取模型列表失败:', error)
    // 不显示错误，因为可能没有配置模型
    availableModels.value = []
  } finally {
    loadingModels.value = false
  }
}

const handleUseModelChange = (value: boolean) => {
  if (value && availableModels.value.length === 0) {
    ElMessage.warning('没有可用的模型，请先在模型管理中配置模型')
    smartGenerateForm.value.use_model = false
  } else if (value && !smartGenerateForm.value.model_id && availableModels.value.length > 0) {
    // 自动选择第一个模型
    smartGenerateForm.value.model_id = availableModels.value[0].id
  }
}

const handleImageChange = (file: any) => {
  selectedImageFile.value = file.raw
  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

const handleCloseSmartGenerate = () => {
  smartGenerateDialogVisible.value = false
  imageFileList.value = []
  imagePreview.value = ''
  selectedImageFile.value = null
  smartGenerateForm.value = {
    project_id: undefined,
    use_model: false,
    model_id: undefined
  }
  availableModels.value = []
}

const handleSubmitSmartGenerate = async () => {
  if (!smartGenerateForm.value.project_id) {
    ElMessage.warning('请选择项目')
    return
  }
  
  if (!selectedImageFile.value) {
    ElMessage.warning('请上传设计原型图片')
    return
  }
  
  if (smartGenerateForm.value.use_model && !smartGenerateForm.value.model_id) {
    ElMessage.warning('请选择模型')
    return
  }

  smartGenerating.value = true
  try {
    const generatedTestCases = await testcaseApi.generateTestCasesFromImage(
      smartGenerateForm.value.project_id,
      selectedImageFile.value,
      smartGenerateForm.value.use_model ? smartGenerateForm.value.model_id : undefined
    )
    
    ElMessage.success(`成功生成 ${generatedTestCases.length} 个测试用例`)
    smartGenerateDialogVisible.value = false
    fetchTestCases()
    
    // 清空表单
    handleCloseSmartGenerate()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '生成失败'
    ElMessage.error(errorMessage)
  } finally {
    smartGenerating.value = false
  }
}

const addStep = () => {
  if (!formData.value.steps) {
    formData.value.steps = []
  }
  formData.value.steps.push({ 
    description: '', 
    expected_result: '' 
  })
}

const removeStep = (index: number) => {
  formData.value.steps?.splice(index, 1)
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    functional: 'success',
    'non-functional': 'info'
  }
  return map[type] || ''
}

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    functional: '功能',
    'non-functional': '非功能'
  }
  return map[type] || type
}

const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = {
    P0: 'danger',
    P1: 'danger',
    P2: 'warning',
    P3: 'info',
    P4: 'info'
  }
  return map[priority] || ''
}

const getPriorityLabel = (priority: string) => {
  return priority || '-'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    active: 'success',
    deprecated: 'danger'
  }
  return map[status] || ''
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    active: '激活',
    deprecated: '已废弃'
  }
  return map[status] || status
}

// 调整宽度相关函数
const handleResizeStart = (e: MouseEvent) => {
  isResizing.value = true
  resizeStartX.value = e.clientX
  resizeStartWidth.value = sidebarWidth.value
  document.addEventListener('mousemove', handleResizeMove)
  document.addEventListener('mouseup', handleResizeEnd)
  e.preventDefault()
}

const handleResizeMove = (e: MouseEvent) => {
  if (!isResizing.value) return
  const diff = e.clientX - resizeStartX.value
  const newWidth = resizeStartWidth.value + diff
  // 限制最小宽度和最大宽度
  sidebarWidth.value = Math.max(200, Math.min(600, newWidth))
}

const handleResizeEnd = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResizeMove)
  document.removeEventListener('mouseup', handleResizeEnd)
}

const handleResizeReset = () => {
  sidebarWidth.value = 280 // 重置为默认宽度
}

onMounted(async () => {
  isMounted = true
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 初始化项目选择
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    filters.value.project_id = getCurrentProjectId.value
  }
  fetchTestCases()
  fetchProjects()
  fetchUsers()
  
  // 监听项目切换事件
  const cleanup = onProjectChanged(() => {
    if (!isMounted) return
    // 项目切换时重新加载项目列表和数据
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.value.project_id = getCurrentProjectId.value
    }
    fetchProjects()
    fetchTestCases()
  })
  
  // 组件卸载时清理监听
  onUnmounted(() => {
    isMounted = false
    cleanup()
    // 清理调整宽度的事件监听
    document.removeEventListener('mousemove', handleResizeMove)
    document.removeEventListener('mouseup', handleResizeEnd)
  })
})
</script>

<style scoped>
.testcases-page {
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

/* 左右分栏布局 */
.testcases-layout {
  display: flex;
  gap: 0;
  height: calc(100vh - 200px);
  min-height: 400px;
  max-height: calc(100vh - 200px);
  overflow: hidden;
  position: relative;
}

/* 分割条 */
.resize-handle {
  width: 4px;
  flex-shrink: 0;
  background: #e4e7ed;
  cursor: col-resize;
  transition: background 0.2s;
  position: relative;
  margin: 0 8px;
}

.resize-handle:hover {
  background: #409eff;
}

.resize-handle::before {
  content: '';
  position: absolute;
  left: -2px;
  right: -2px;
  top: 0;
  bottom: 0;
  cursor: col-resize;
}

.resize-handle::after {
  content: '⋮';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  color: #909399;
  font-size: 12px;
  pointer-events: none;
  line-height: 1;
  letter-spacing: -2px;
}

/* 左侧目录树 */
.directory-sidebar {
  width: 280px;
  min-width: 200px;
  max-width: 600px;
  flex-shrink: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease;
}

.directory-card {
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.directory-card :deep(.el-card__body) {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.directory-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f2f5;
}

.directory-search-input {
  position: relative;
}

.directory-search-input :deep(.el-input__inner) {
  text-align: center;
  padding-left: 30px;
  padding-right: 30px;
}

.directory-search-input :deep(.el-input__prefix) {
  left: 8px;
  pointer-events: none;
}

.directory-header .el-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  color: #ffffff !important;
}

.directory-header .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
  color: #ffffff !important;
}

.directory-tree-container {
  flex: 1;
  overflow-y: auto;
  min-height: 400px;
}

.directory-tree {
  background: transparent;
  overflow: visible; /* 确保内容可见 */
}

/* 确保tree容器不截断内容 */
.directory-tree :deep(.el-tree) {
  overflow: visible;
}

.directory-tree :deep(.el-tree-node) {
  overflow: visible;
}

.directory-tree :deep(.el-tree-node) {
  margin-bottom: 4px;
}

.directory-tree :deep(.el-tree-node__expand-icon) {
  color: #909399;
  font-size: 14px;
  padding: 0 4px;
  transition: all 0.2s;
}

.directory-tree :deep(.el-tree-node__expand-icon:hover) {
  color: #409eff;
}

.directory-tree :deep(.el-tree-node__content) {
  height: 40px;
  padding: 0 8px;
  border-radius: 8px;
  transition: all 0.2s;
  margin-bottom: 2px;
  border: 1px solid transparent;
  position: relative;
}

.directory-tree :deep(.el-tree-node__content:hover) {
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-color: #e0e7ff;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
}

.directory-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: linear-gradient(135deg, #ecf5ff 0%, #e0f0ff 100%);
  border-color: #409eff;
  color: #409eff;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

/* 子分组使用标准缩进，让箭头对齐父分组图标 */
.directory-tree :deep(.el-tree-node__children) {
  padding-left: 18px;
}

.directory-node-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 4px;
  box-sizing: border-box;
  min-width: 0;
  overflow: visible;
  gap: 8px;
}

.directory-node-content {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.directory-folder-icon {
  font-size: 18px;
  color: #f5a623;
  flex-shrink: 0;
  transition: all 0.2s;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 非叶子节点使用紫色 */
.directory-folder-icon:not(.is-leaf) {
  color: #667eea; /* 紫色 */
}

.directory-folder-icon.is-expanded:not(.is-leaf) {
  color: #764ba2; /* 展开时的深紫色 */
}

/* 叶子节点保持橙色 */
.directory-folder-icon.is-leaf {
  color: #f5a623; /* 橙色 */
}

.directory-node-wrapper:hover .directory-folder-icon {
  transform: scale(1.1);
}

.directory-node-label {
  flex: 1 1 auto;
  font-size: 14px;
  color: #303133;
  font-weight: 400;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-left: 6px;
  min-width: 20px;
  max-width: none;
  visibility: visible !important;
}

.directory-node-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 16px;
  padding: 0 4px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  font-size: 11px;
  color: #606266;
  font-weight: 500;
  flex-shrink: 0;
  margin-left: 2px;
  transition: all 0.2s;
}

.directory-node-wrapper:hover .directory-node-count {
  background: #e9ecef;
  border-color: #d0d7de;
  color: #495057;
}

.directory-node-actions {
  display: flex;
  align-items: center;
  gap: 0;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
  margin-left: auto;
}

.directory-node-wrapper:hover .directory-node-actions {
  opacity: 1;
}

.directory-action-btn {
  background: transparent !important;
  background-color: transparent !important;
  padding: 1px !important;
  border: none !important;
  box-shadow: none !important;
  min-width: auto !important;
  width: auto !important;
  margin: 0 -2px !important;
}

.directory-action-btn :deep(.el-icon) {
  font-size: 14px !important;
}

.directory-action-btn:hover {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.directory-action-btn:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

/* 右侧主内容区 */
.testcases-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
  overflow: hidden;
  height: 100%;
}


.testcases-list-card {
  height: 100%;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.testcases-list-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  flex: 1;
  min-height: 0;
}

/* 隐藏右侧滚动条 */
.testcases-list-card :deep(.el-card__body)::-webkit-scrollbar,
.testcases-list-card :deep(.el-card__body) *::-webkit-scrollbar {
  display: none;
}

.testcases-list-card :deep(.el-card__body),
.testcases-list-card :deep(.el-card__body) * {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.testcases-list-card :deep(.el-table__body-wrapper)::-webkit-scrollbar {
  display: none;
}

.testcases-list-card :deep(.el-table__body-wrapper) {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 表格操作按钮样式 - 无背景色 */
.table-action-btn {
  background: transparent !important;
  background-color: transparent !important;
  padding: 4px 8px !important;
  border: none !important;
  box-shadow: none !important;
}

.table-action-btn:hover {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.table-action-btn:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.table-action-btn[type="primary"] {
  color: #409eff !important;
}

.table-action-btn[type="primary"]:hover {
  color: #66b1ff !important;
}

.table-action-btn[type="danger"] {
  color: #f56c6c !important;
}

.table-action-btn[type="danger"]:hover {
  color: #f78989 !important;
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

/* 增加步骤按钮图标和文字颜色为白色 */
.add-step-btn.el-button--primary.is-plain,
:deep(.add-step-btn.el-button--primary.is-plain .el-icon),
:deep(.add-step-btn.el-button--primary.is-plain .el-icon svg),
:deep(.add-step-btn .el-icon svg),
:deep(.add-step-btn .el-icon path),
.add-step-text {
  color: #ffffff !important;
  fill: #ffffff !important;
}

.add-step-btn.el-button--primary.is-plain:hover,
:deep(.add-step-btn.el-button--primary.is-plain:hover .el-icon),
:deep(.add-step-btn.el-button--primary.is-plain:hover .el-icon svg),
:deep(.add-step-btn.el-button--primary.is-plain:hover .el-icon path) {
  color: #ffffff !important;
  fill: #ffffff !important;
}

/* 抽屉样式 - 参考缺陷管理 */
:deep(.el-drawer) {
  border-radius: 12px 0 0 12px;
  overflow: hidden;
}

:deep(.el-drawer__header) {
  background: #ffffff;
  color: #303133;
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-drawer__title) {
  color: #303133;
  font-weight: 600;
  font-size: 18px;
}

/* 抽屉底部按钮 */
.drawer-footer {
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

/* 抽屉布局样式 */
.testcase-drawer-row {
  margin: 0;
  min-height: calc(100vh - 200px);
}

.drawer-left-col {
  padding-right: 16px;
  border-right: 1px solid #e4e7ed;
}

.drawer-center-col {
  padding: 0 16px;
  border-right: 1px solid #e4e7ed;
}

.drawer-right-col {
  padding-left: 16px;
}

/* 左侧区域样式 */
.left-section {
  height: 100%;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.description-input,
.precondition-input {
  width: 100%;
}

.description-input :deep(.el-textarea__inner),
.precondition-input :deep(.el-textarea__inner) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
}

/* 标题输入框样式，与前置条件保持一致 */
.section-block :deep(.el-input__wrapper) {
  border-radius: 4px;
}

/* 步骤区域样式 */
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

.header-cell-action {
  width: 80px;
  flex-shrink: 0;
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

.table-cell-action {
  width: 80px;
  flex-shrink: 0;
  justify-content: center;
  text-align: center;
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
  font-weight: bold;
  font-size: 14px;
  margin: 0 auto;
}

.step-input {
  width: 100%;
}

.step-input :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  padding: 4px 0;
  min-height: 24px;
  line-height: 1.5;
  resize: vertical;
  box-shadow: none;
}

.step-input :deep(.el-textarea__inner):focus {
  border: none;
  background: transparent;
  box-shadow: none;
}

.step-delete-btn {
  background: transparent !important;
  background-color: transparent !important;
  padding: 0 !important;
  border: none !important;
  box-shadow: none !important;
}

.step-delete-btn:hover {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.step-delete-btn:focus {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
}

.add-step-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 右侧区域样式 */
.right-section {
  height: 100%;
}

.info-section {
  margin-top: 12px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-avatar {
  flex-shrink: 0;
  background: #409eff;
  color: #fff;
  font-size: 12px;
}

.info-text {
  flex: 1;
  min-width: 0;
}

.info-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.info-time {
  font-size: 12px;
  color: #909399;
}

.info-empty {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 20px 0;
}

/* 树形结构样式 */
.testcases-tree-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 600px;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 16px;
}

.tree-header-left {
  display: flex;
  align-items: center;
}

.tree-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.tree-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  min-height: 500px;
}

.testcases-tree {
  background: transparent;
}

.testcases-tree :deep(.el-tree-node) {
  margin-bottom: 4px;
}

.testcases-tree :deep(.el-tree-node__content) {
  height: 36px;
  padding: 0 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.testcases-tree :deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}

.tree-node-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0 8px;
  cursor: pointer;
}

.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.tree-node-icon {
  display: flex;
  align-items: center;
  color: #409eff;
  font-size: 16px;
}

.tree-node-icon .el-icon {
  font-size: 16px;
}

.tree-node-label {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-node-count {
  display: inline-block;
  padding: 2px 8px;
  background: #f0f2f5;
  border-radius: 12px;
  font-size: 12px;
  color: #606266;
  margin-left: 8px;
}

.tree-node-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node-wrapper:hover .tree-node-actions {
  opacity: 1;
}
</style>

