<template>
  <div class="project-selector">
    <el-card shadow="never" class="project-selector-card">
      <div class="project-selector-content">
        <div class="project-info">
          <el-icon class="project-icon"><FolderOpened /></el-icon>
          <div class="project-text">
            <div class="project-label">当前项目</div>
            <div class="project-name">
              <span v-if="hasProjectSelected" class="project-name-text">{{ getCurrentProjectName }}</span>
              <span v-else class="project-name-placeholder">未选择项目</span>
            </div>
          </div>
        </div>
        <div class="project-actions">
          <el-button 
            v-if="hasProjectSelected" 
            type="primary" 
            size="small" 
            @click="showSelector = true"
          >
            <el-icon><Switch /></el-icon>
            切换项目
          </el-button>
          <el-button 
            v-else 
            type="primary" 
            size="small" 
            @click="showSelector = true"
          >
            <el-icon><Plus /></el-icon>
            选择项目
          </el-button>
          <el-button 
            v-if="hasProjectSelected" 
            type="default" 
            size="small" 
            @click="handleClearProject"
          >
            <el-icon><Close /></el-icon>
            取消过滤
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 项目选择对话框 -->
    <el-dialog
      v-model="showSelector"
      title="选择项目"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-select
        v-model="selectedProjectId"
        placeholder="请选择项目"
        filterable
        style="width: 100%"
        @change="handleProjectChange"
      >
        <el-option
          v-for="project in projects"
          :key="project.id"
          :label="project.name"
          :value="project.id"
        >
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>{{ project.name }}</span>
            <el-tag v-if="project.id === getCurrentProjectId" type="success" size="small">当前</el-tag>
          </div>
        </el-option>
      </el-select>
      <template #footer>
        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <el-button @click="showSelector = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmProject" :disabled="!selectedProjectId">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { FolderOpened, Switch, Plus, Close } from '@element-plus/icons-vue'
import { useProjectContext } from '../composables/useProjectContext'

const {
  currentProject,
  setCurrentProject,
  clearCurrentProject,
  getCurrentProjectId,
  getCurrentProjectName,
  hasProjectSelected,
  getProjects,
  refreshProjects
} = useProjectContext()

const showSelector = ref(false)
const selectedProjectId = ref<number | null>(null)
const projects = ref<any[]>([])

// 加载项目列表
const loadProjectsList = async () => {
  try {
    projects.value = await getProjects()
    // 如果当前有选中的项目，设置默认选中
    if (getCurrentProjectId.value) {
      selectedProjectId.value = getCurrentProjectId.value
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

// 确认选择项目
const handleConfirmProject = async () => {
  if (selectedProjectId.value) {
    await setCurrentProject(selectedProjectId.value)
    ElMessage.success('项目切换成功')
    showSelector.value = false
  }
}

// 项目选择变化
const handleProjectChange = (projectId: number) => {
  // 可以在这里添加即时切换逻辑，或者只在确认时切换
}

// 清除项目过滤
const handleClearProject = () => {
  clearCurrentProject()
  ElMessage.success('已取消项目过滤')
}

// 监听对话框打开，刷新项目列表
watch(showSelector, (newVal) => {
  if (newVal) {
    loadProjectsList()
  }
})

onMounted(() => {
  loadProjectsList()
  
  // 监听项目切换事件，刷新项目列表
  window.addEventListener('project:changed', () => {
    loadProjectsList()
  })
})
</script>

<style scoped>
.project-selector {
  margin: 20px 20px 20px 20px;
}

.project-selector-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.project-selector-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.project-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.project-icon {
  font-size: 28px;
  color: #409eff;
}

.project-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-label {
  font-size: 12px;
  color: #909399;
}

.project-name {
  font-size: 16px;
  font-weight: 500;
}

.project-name-text {
  color: #303133;
  font-weight: 600;
}

.project-name-placeholder {
  color: #c0c4cc;
}

.project-actions {
  display: flex;
  gap: 8px;
}

:deep(.el-card__body) {
  padding: 12px 16px;
}
</style>

