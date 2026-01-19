<template>
  <div class="models-page">
    <!-- 顶部：标题 + 搜索 + 新建按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><Cpu /></el-icon>
          模型管理
        </h2>
      </div>
      <div class="filter-row">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索模型名称"
          clearable
          @keyup.enter="() => {}"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="searchKeyword = searchKeyword.trim()">搜索</el-button>
        <el-button @click="searchKeyword = ''">重置</el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新建模型
        </el-button>
      </div>
    </el-card>

    <!-- 底部：模型列表 -->
    <el-card class="table-card">
      <el-table :data="paginatedModels" v-loading="loading" :max-height="600">
        <el-table-column label="编号" width="80" type="index" :index="(index) => (currentPage - 1) * pageSize + index + 1" />
        <el-table-column prop="name" label="模型名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="provider" label="提供商" width="120">
          <template #default="{ row }">
            <el-tag :type="getProviderTag(row.provider)">{{ getProviderLabel(row.provider) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'api' ? 'success' : 'info'">
              {{ row.type === 'api' ? 'API' : '本地' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型标识" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.model_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_default" style="color: #67c23a; font-size: 20px;"><Check /></el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button 
                link 
                :type="row.status === 'active' ? 'warning' : 'success'"
                @click="handleToggleStatus(row)"
              >
                <el-icon><Switch /></el-icon>
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button 
                link 
                type="primary"
                @click="handleTest(row)"
              >
                <el-icon><VideoPlay /></el-icon>
                测试
              </el-button>
              <el-button 
                link 
                type="primary"
                @click="handleEdit(row)"
              >
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button 
                link 
                type="danger"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 12px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="prev, pager, next, sizes, jumper, ->, total"
          :total="filteredModels.length"
        />
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" width="700px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建模型' ? '配置AI模型，支持API KEY调用' : '修改模型配置信息' }}</span>
        </div>
      </template>
      <el-form :model="formData" label-width="120px" label-position="left">
        <el-form-item label="模型名称" required>
          <el-input v-model="formData.name" placeholder="例如：GPT-4" />
        </el-form-item>
        
        <el-form-item label="提供商" required>
          <el-select v-model="formData.provider" placeholder="选择提供商" style="width: 100%">
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="通义千问" value="qwen" />
            <el-option label="豆包" value="doubao" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="API Key" required>
          <el-input 
            v-model="formData.api_key" 
            type="password" 
            show-password
            placeholder="输入API密钥"
          />
        </el-form-item>
        
        <el-form-item label="API Base URL">
          <el-input 
            v-model="formData.api_base" 
            placeholder="可选，默认使用官方API地址"
          />
        </el-form-item>
        
        <el-form-item label="模型标识" required>
          <el-input 
            v-model="formData.model_name" 
            :placeholder="getModelNamePlaceholder()"
          />
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">
            {{ getModelNameHint() }}
          </div>
        </el-form-item>

        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="描述">
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="3"
            placeholder="模型描述信息（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 测试对话框 -->
    <el-dialog v-model="testDialogVisible" title="测试模型" width="600px">
      <el-form label-width="100px">
        <el-form-item label="测试提示词">
          <el-input 
            v-model="testPrompt" 
            type="textarea" 
            :rows="4"
            placeholder="输入测试提示词"
          />
        </el-form-item>
        <el-form-item label="响应结果">
          <el-input 
            v-model="testResponse" 
            type="textarea" 
            :rows="6"
            readonly
            placeholder="模型响应将显示在这里"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <el-button @click="testDialogVisible = false">关闭</el-button>
          <el-button type="primary" :loading="testing" @click="handleTestSubmit">测试</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, Cpu, Check, VideoPlay, Switch } from '@element-plus/icons-vue'
import * as modelApi from '@/api/models'
import type { Model } from '@/api/types'

const models = ref<Model[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const testDialogVisible = ref(false)
const editingId = ref<number | null>(null)
const searchKeyword = ref('')
const testPrompt = ref('你好，请介绍一下你自己')
const testResponse = ref('')
const testing = ref(false)
const testingModelId = ref<number | null>(null)

const dialogTitle = computed(() => editingId.value ? '编辑模型' : '新建模型')

const filteredModels = computed(() => {
  if (!searchKeyword.value.trim()) {
    return models.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return models.value.filter(model => 
    model.name.toLowerCase().includes(keyword) ||
    (model.model_name && model.model_name.toLowerCase().includes(keyword)) ||
    (model.description && model.description.toLowerCase().includes(keyword))
  )
})

const paginatedModels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredModels.value.slice(start, start + pageSize.value)
})

const formData = ref<Partial<Model>>({
  name: '',
  provider: 'openai',
  type: 'api',
  api_key: '',
  api_base: '',
  model_name: '',
  is_default: false,
  status: 'active',
  description: ''
})

const fetchModels = async () => {
  loading.value = true
  try {
    models.value = await modelApi.getModels()
  } catch (error: any) {
    ElMessage.error(error.message || '获取模型列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  editingId.value = null
  formData.value = {
    name: '',
    provider: 'openai',
    type: 'api',
    api_key: '',
    api_base: '',
    model_name: '',
    is_default: false,
    status: 'active',
    description: ''
  }
  dialogVisible.value = true
}

const handleEdit = (model: Model) => {
  editingId.value = model.id
  formData.value = {
    ...model
  }
  dialogVisible.value = true
}

const handleTypeChange = () => {
  // 类型切换逻辑已移除（只支持 API 类型）
}

const handleSave = async () => {
  if (!formData.value.name) {
    ElMessage.warning('请输入模型名称')
    return
  }
  
  // 只支持 API 类型
  if (!formData.value.provider) {
    ElMessage.warning('请选择提供商')
    return
  }
  if (!formData.value.api_key) {
    ElMessage.warning('请输入API Key')
    return
  }
  if (!formData.value.model_name) {
    ElMessage.warning('请输入模型标识')
    return
  }

  try {
    if (editingId.value) {
      await modelApi.updateModel(editingId.value, formData.value)
      ElMessage.success('模型更新成功')
    } else {
      await modelApi.createModel(formData.value)
      ElMessage.success('模型创建成功')
    }
    dialogVisible.value = false
    fetchModels()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

const handleDelete = async (model: Model) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模型吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await modelApi.deleteModel(model.id)
    ElMessage.success('删除成功')
    fetchModels()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleToggleStatus = async (model: Model) => {
  try {
    const newStatus = model.status === 'active' ? 'inactive' : 'active'
    await modelApi.updateModel(model.id, { status: newStatus })
    ElMessage.success(`模型已${newStatus === 'active' ? '启用' : '禁用'}`)
    fetchModels()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleTest = (model: Model) => {
  testingModelId.value = model.id
  testPrompt.value = '你好，请介绍一下你自己'
  testResponse.value = ''
  testDialogVisible.value = true
}

const handleTestSubmit = async () => {
  if (!testingModelId.value) return
  if (!testPrompt.value.trim()) {
    ElMessage.warning('请输入测试提示词')
    return
  }

  testing.value = true
  try {
    const result = await modelApi.testModel(testingModelId.value, testPrompt.value)
    testResponse.value = result.response || '无响应'
  } catch (error: any) {
    ElMessage.error(error.message || '测试失败')
    testResponse.value = `错误: ${error.message || '未知错误'}`
  } finally {
    testing.value = false
  }
}

const getProviderLabel = (provider: string) => {
  const map: Record<string, string> = {
    openai: 'OpenAI',
    deepseek: 'DeepSeek',
    qwen: '通义千问',
    doubao: '豆包'
  }
  return map[provider] || provider
}

const getProviderTag = (provider: string) => {
  const map: Record<string, string> = {
    openai: 'success',
    deepseek: 'primary',
    qwen: 'warning',
    doubao: 'info',
    local: ''
  }
  return map[provider] || ''
}

const getModelNamePlaceholder = () => {
  const provider = formData.value.provider
  const placeholders: Record<string, string> = {
    openai: '例如：gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo',
    deepseek: '例如：deepseek-chat（对话）, deepseek-coder（代码）, deepseek-vl（视觉）',
    qwen: '例如：qwen-turbo, qwen-plus, qwen-max',
    doubao: '例如：doubao-pro-32k, doubao-lite-32k'
  }
  return placeholders[provider] || '请输入模型标识'
}

const getModelNameHint = () => {
  const provider = formData.value.provider
  const hints: Record<string, string> = {
    openai: '常见模型：gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo（视觉：gpt-4-vision-preview）',
    deepseek: '常见模型：deepseek-chat（对话）, deepseek-coder（代码）, deepseek-vl（视觉，支持图片解析，推荐）',
    qwen: '常见模型：qwen-turbo, qwen-plus, qwen-max',
    doubao: '常见模型：doubao-pro-32k, doubao-lite-32k'
  }
  return hints[provider] || '请填写正确的模型标识名称'
}

onMounted(() => {
  fetchModels()
})
</script>

<style scoped>
.models-page {
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

.table-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  width: 100%;
}

.table-actions .el-button {
  width: 100%;
  justify-content: center;
}
</style>

