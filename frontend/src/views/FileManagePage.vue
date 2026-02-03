<template>
  <div class="file-manage-page">
    <!-- 顶部：标题 + 搜索 + 新建按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><FolderOpened /></el-icon>
          文件管理
        </h2>
      </div>
      <div class="filter-row">
        <el-select 
          v-model="filters.file_type" 
          placeholder="文件类型" 
          clearable 
          @change="loadFiles"
          style="width: 150px;"
        >
          <el-option label="全部" value="" />
          <el-option label="流程导出" value="flow" />
          <el-option label="本地上传" value="local" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索文件名称或描述"
          clearable
          @keyup.enter="loadFiles"
          style="width: 250px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="loadFiles">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建文件
        </el-button>
      </div>
    </el-card>

    <!-- 底部：文件列表 -->
    <el-card class="table-card">
      <el-table
        :data="files"
        v-loading="loading"
        stripe
        style="width: 100%"
        table-layout="fixed"
        :max-height="600"
        row-key="id"
      >
        <el-table-column label="编号" width="80" align="center" type="index" :index="(index: number) => (currentPage - 1) * pageSize + index + 1" />
        <el-table-column prop="name" label="名称" min-width="200" align="center" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="250" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.description || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.file_type === 'flow' ? 'success' : 'primary'" size="small">
              {{ row.file_type === 'flow' ? '流程导出' : '本地上传' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_name" label="文件名" min-width="250" align="center" show-overflow-tooltip>
          <template #default="{ row }">
            <el-link type="primary" @click="handleDownload(row)" :underline="false">
              {{ row.file_name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="handleEdit(row)">
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button link type="danger" @click="handleDelete(row)">
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
          :total="total"
          @current-change="loadFiles"
          @size-change="loadFiles"
        />
      </div>
    </el-card>

    <!-- 上传文件对话框 -->
    <el-dialog v-model="uploadDialogVisible" width="600px" :close-on-click-modal="false">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">上传文件</span>
          <span class="dialog-description">上传本地文件到文件管理系统</span>
        </div>
      </template>
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="文件名称" required>
          <el-input v-model="uploadForm.name" placeholder="请输入文件名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="3" placeholder="请输入文件描述（可选）" />
        </el-form-item>
        <el-form-item label="选择文件" required>
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".json,.txt,.csv,.xml"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              选择文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">支持 .json, .txt, .csv, .xml 格式文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑文件对话框 -->
    <el-dialog v-model="editDialogVisible" width="600px" :close-on-click-modal="false">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">编辑文件</span>
          <span class="dialog-description">修改文件的名称和描述信息</span>
        </div>
      </template>
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="文件名称" required>
          <el-input v-model="editForm.name" placeholder="请输入文件名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入文件描述（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { FolderOpened, Search, Upload, Plus, EditPen, Delete } from '@element-plus/icons-vue'
import { 
  getTestFiles, 
  createTestFile, 
  updateTestFile, 
  deleteTestFile,
  downloadTestFile,
  type TestFile 
} from '../api/apitest'

const files = ref<TestFile[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = reactive({
  keyword: '',
  file_type: ''
})

// 上传对话框
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref()
const uploadForm = reactive({
  name: '',
  description: '',
  file: null as File | null
})

// 编辑对话框
const editDialogVisible = ref(false)
const saving = ref(false)
const editingFile = ref<TestFile | null>(null)
const editForm = reactive({
  name: '',
  description: ''
})

// 加载文件列表
const loadFiles = async () => {
  loading.value = true
  try {
    const response = await getTestFiles({
      keyword: filters.keyword || undefined,
      file_type: filters.file_type || undefined,
      page: currentPage.value,
      page_size: pageSize.value
    })
    files.value = response.items
    total.value = response.total
  } catch (error: any) {
    ElMessage.error('加载文件列表失败: ' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 重置筛选
const handleReset = () => {
  filters.keyword = ''
  filters.file_type = ''
  currentPage.value = 1
  loadFiles()
}

// 打开上传对话框
const handleCreate = () => {
  uploadForm.name = ''
  uploadForm.description = ''
  uploadForm.file = null
  uploadDialogVisible.value = true
}

// 文件选择变化
const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  // 自动设置文件名称
  if (!uploadForm.name && file.name) {
    uploadForm.name = file.name.replace(/\.[^/.]+$/, '') // 去掉扩展名
  }
}

// 文件移除
const handleFileRemove = () => {
  uploadForm.file = null
}

// 上传文件
const handleUpload = async () => {
  if (!uploadForm.name) {
    ElMessage.warning('请输入文件名称')
    return
  }
  if (!uploadForm.file) {
    ElMessage.warning('请选择文件')
    return
  }
  
  uploading.value = true
  try {
    await createTestFile({
      name: uploadForm.name,
      description: uploadForm.description,
      file_type: 'local',
      file: uploadForm.file
    })
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    loadFiles()
  } catch (error: any) {
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
  } finally {
    uploading.value = false
  }
}

// 下载文件
const handleDownload = async (row: TestFile) => {
  try {
    const response = await downloadTestFile(row.id)
    // 创建下载链接
    const blob = new Blob([response as any])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = row.file_name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    ElMessage.error('下载失败: ' + (error.message || '未知错误'))
  }
}

// 打开编辑对话框
const handleEdit = (row: TestFile) => {
  editingFile.value = row
  editForm.name = row.name
  editForm.description = row.description || ''
  editDialogVisible.value = true
}

// 保存编辑
const handleSave = async () => {
  if (!editForm.name) {
    ElMessage.warning('请输入文件名称')
    return
  }
  if (!editingFile.value) return
  
  saving.value = true
  try {
    await updateTestFile(editingFile.value.id, {
      name: editForm.name,
      description: editForm.description
    })
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    loadFiles()
  } catch (error: any) {
    ElMessage.error('保存失败: ' + (error.message || '未知错误'))
  } finally {
    saving.value = false
  }
}

// 删除文件
const handleDelete = async (row: TestFile) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${row.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteTestFile(row.id)
    ElMessage.success('删除成功')
    loadFiles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number | undefined) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

// 格式化日期
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

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.file-manage-page {
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
  transition: all 0.3s ease;
  position: relative;
}

.table-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 0.8);
}

.table-actions {
  display: flex;
  gap: 8px;
}

.table-card :deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

.table-card :deep(.el-table__header) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.table-card :deep(.el-table__header th) {
  background: transparent;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
  padding: 16px 0;
}

.table-card :deep(.el-table__body tr) {
  transition: all 0.2s ease;
}

.table-card :deep(.el-table__body tr:hover) {
  background: #f8f9ff !important;
}

.table-card :deep(.el-table__body td) {
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
}

.dialog-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.dialog-description {
  font-size: 13px;
  color: #909399;
}
</style>
