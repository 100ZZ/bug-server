<template>
  <div class="users-page">
    <!-- 顶部：标题 + 搜索 + 新建按钮 -->
    <el-card class="filter-card">
      <div class="filter-header">
        <h2>
          <el-icon><User /></el-icon>
          用户管理
        </h2>
      </div>
      <div class="filter-row">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用户名、显示名称或邮箱"
          clearable
          @keyup.enter="() => {}"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button @click="searchKeyword = searchKeyword.trim()">搜索</el-button>
        <el-button @click="searchKeyword = ''">重置</el-button>
        <el-button 
          v-if="canCreate('users')" 
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新建用户
        </el-button>
      </div>
    </el-card>

    <!-- 底部：用户列表 -->
    <el-card class="table-card">
      <el-table :data="paginatedUsers" v-loading="loading" :max-height="600">
        <el-table-column label="编号" width="80" type="index" :index="(index) => (currentPage - 1) * pageSize + index + 1" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="display_name" label="显示名称" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="roles" label="角色" width="200">
          <template #default="{ row }">
            <el-tag v-for="role in (row.roles || [])" :key="role" style="margin-right: 4px; margin-bottom: 4px;">
              {{ getRoleLabel(role) }}
            </el-tag>
            <span v-if="!row.roles || row.roles.length === 0" style="color: #909399;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" v-if="canUpdate('users') || canDelete('users')">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button 
                v-if="canUpdate('users')" 
                link 
                type="primary"
                @click="handleEdit(row)"
              >
                <el-icon><EditPen /></el-icon>
                编辑
              </el-button>
              <el-button 
                v-if="canDelete('users')" 
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
          :total="filteredUsers.length"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" width="600px">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">{{ dialogTitle }}</span>
          <span class="dialog-description">{{ dialogTitle === '新建用户' ? '创建新用户账号，设置用户名、邮箱和角色权限' : '修改用户的基本信息和权限设置' }}</span>
        </div>
      </template>
      <el-form :model="formData" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="formData.username" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="formData.email" />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="formData.display_name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="formData.roles" multiple style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="产品" value="product" />
            <el-option label="开发" value="developer" />
            <el-option label="测试" value="tester" />
            <el-option label="游客" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">活跃</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, EditPen, Delete, User } from '@element-plus/icons-vue'
import * as userApi from '../api/users'
import type { User as UserType } from '../api/types'
import { usePermissions } from '../composables/usePermissions'

const { canCreate, canUpdate, canDelete } = usePermissions()

const users = ref<User[]>([])
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新建用户')
const editingId = ref<number>()

const formData = reactive({
  username: '',
  email: '',
  display_name: '',
  roles: [] as string[],
  status: 'active'
})

const loadUsers = async () => {
  loading.value = true
  try {
    users.value = await userApi.getUsers()
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  editingId.value = undefined
  dialogTitle.value = '新建用户'
  Object.assign(formData, { username: '', email: '', display_name: '', roles: [], status: 'active' })
  dialogVisible.value = true
}

const handleEdit = (row: UserType) => {
  editingId.value = row.id
  dialogTitle.value = '编辑用户'
  Object.assign(formData, {
    username: row.username,
    email: row.email,
    display_name: row.display_name || '',
    roles: row.roles || [],
    status: row.status
  })
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!formData.username || !formData.email) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    if (editingId.value) {
      await userApi.updateUser(editingId.value, formData)
      ElMessage.success('更新成功')
    } else {
      await userApi.createUser(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadUsers()
  } catch (error: any) {
    const errorMessage = error.message || error.response?.data?.detail || '保存失败'
    ElMessage.error(errorMessage)
  }
}

const handleDelete = async (row: UserType) => {
  try {
    await ElMessageBox.confirm('确定删除此用户吗？', '提示', { type: 'warning' })
    await userApi.deleteUser(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      const errorMessage = error.message || error.response?.data?.detail || '删除失败'
      ElMessage.error(errorMessage)
    }
  }
}

const handleReset = () => {
  searchKeyword.value = ''
}

const filteredUsers = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) {
    return users.value
  }
  return users.value.filter((user) => {
    const username = (user.username || '').toLowerCase()
    const email = (user.email || '').toLowerCase()
    const displayName = (user.display_name || '').toLowerCase()
    return username.includes(keyword) || email.includes(keyword) || displayName.includes(keyword)
  })
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredUsers.value.slice(start, start + pageSize.value)
})

const getRoleLabel = (role: string) => {
  const map: Record<string, string> = {
    admin: '管理员',
    product: '产品',
    developer: '开发',
    tester: '测试',
    guest: '游客'
  }
  return map[role] || role
}

onMounted(loadUsers)
</script>

<style scoped>
.users-page {
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
</style>

