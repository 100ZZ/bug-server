<template>
  <div class="api-test-page">
        <!-- 顶部：标题 + 筛选 + 同步/上传按钮 -->
        <el-card class="filter-card">
          <div class="filter-header">
            <h2>
              <el-icon><Connection /></el-icon>
              接口测试
            </h2>
          </div>
          <div class="filter-row">
            <!-- 左侧：搜索和筛选区域 -->
            <div class="filter-left">
            <el-select 
              v-model="filters.project_id" 
              placeholder="选择项目" 
              clearable 
              style="width: 200px" 
              @change="loadEndpoints"
              :disabled="hasProjectSelected"
              :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
            >
              <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
            </el-select>
            <el-select v-model="filters.method" placeholder="HTTP方法" clearable style="width: 150px" @change="loadEndpoints">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
              <el-option label="PATCH" value="PATCH" />
            </el-select>
            <el-input
              v-model="filters.keyword"
              placeholder="搜索接口名称、路径或描述"
              clearable
              @keyup.enter="loadEndpoints"
                style="width: 280px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button @click="loadEndpoints">搜索</el-button>
              <el-button @click="handleReset">重置</el-button>
        <el-button 
          :type="filters.showFavorite ? 'primary' : 'default'"
          :icon="Star"
          @click="toggleFavoriteFilter"
        >
          收藏
        </el-button>
            </div>
            
            <!-- 右侧：主要操作按钮区域 -->
            <div class="filter-right">
              <el-button type="primary" @click="handleRecordApi">
                <el-icon><VideoCamera /></el-icon>
                录制接口
              </el-button>
              <el-button type="primary" @click="handleSyncSwagger">
                <el-icon><Refresh /></el-icon>
                同步接口
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 底部：接口列表 -->
        <el-card class="table-card">
          <el-table
            ref="endpointsTableRef"
            :data="pagedEndpoints"
            v-loading="loading"
            stripe
            style="width: 100%"
            table-layout="fixed"
            :max-height="600"
            row-key="id"
          >
            <el-table-column label="编号" width="80" align="center" type="index" :index="(index: number) => (pagination.currentPage - 1) * pagination.pageSize + index + 1" />
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
            <el-table-column prop="project" label="项目" width="140" align="center" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.project?.name || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="name" label="名称" min-width="200" align="center" show-overflow-tooltip />
            <el-table-column prop="tags" label="标签" width="180" align="center">
              <template #default="{ row }">
                <el-tag v-for="tag in (row.tags || [])" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="250" align="center" show-overflow-tooltip />
            <el-table-column prop="method" label="方法" width="90" align="center">
              <template #default="{ row }">
                <el-tag :type="getMethodTag(row.method)" size="small">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="path" label="路径" min-width="350" align="center" show-overflow-tooltip />
            <el-table-column prop="created_at" label="创建时间" width="180" align="center" show-overflow-tooltip>
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center" fixed="right">
              <template #default="{ row }">
                <div class="table-actions">
                  <el-button link type="primary" @click="handleExecute(row)">
                    <el-icon><View /></el-icon>
                    详情
                  </el-button>
                  <el-button link type="danger" @click="handleDeleteEndpoint(row)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 12px; text-align: right;">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="prev, pager, next, sizes, jumper, ->, total"
              :total="endpoints.length"
            />
          </div>
        </el-card>

    <!-- 同步接口对话框（合并URL和文件上传） -->
    <el-dialog v-model="syncDialogVisible" width="700px" :close-on-click-modal="true">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">同步接口</span>
          <span class="dialog-description">可以从Swagger URL或上传Swagger文件来同步接口，系统将自动解析并导入接口信息</span>
        </div>
      </template>
      <el-alert
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      >
        同步接口会删除现有接口并导入新接口
      </el-alert>
      
      <el-tabs v-model="syncType" @tab-change="handleSyncTypeChange">
        <el-tab-pane label="从URL同步" name="url">
          <el-form :model="syncFormData" label-width="120px" style="margin-top: 20px">
            <el-form-item label="选择项目" required>
              <el-select
                v-model="syncFormData.project_id"
                placeholder="选择项目"
                style="width: 100%"
                @change="syncFormData.environment_id = undefined"
                :disabled="hasProjectSelected"
                :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
              >
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择环境" required>
              <el-select v-model="syncFormData.environment_id" placeholder="选择环境" style="width: 100%" :disabled="!syncFormData.project_id">
                <el-option
                  v-for="env in filteredEnvironments"
                  :key="env.id"
                  :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
                  :value="env.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="Swagger路径">
              <el-input v-model="syncFormData.swagger_path" placeholder="/v3/api-docs" />
            </el-form-item>
            <el-form-item label="完整URL" v-if="syncFormData.environment_id && syncFormData.swagger_path">
              <el-text>{{ getFullSwaggerUrl() }}</el-text>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="上传文件" name="file">
          <el-form :model="syncFormData" label-width="120px" style="margin-top: 20px">
            <el-form-item label="选择项目" required>
              <el-select
                v-model="syncFormData.project_id"
                placeholder="选择项目"
                style="width: 100%"
                :disabled="hasProjectSelected"
                :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
              >
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="上传文件" required>
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :limit="1"
                accept=".json"
                drag
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持Swagger v2/v3格式的JSON文件
                  </div>
                </template>
              </el-upload>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-start;">
          <el-button @click="syncDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="syncing" @click="handleSyncSubmit">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 录制接口对话框 -->
    <el-dialog v-model="recordDialogVisible" width="1000px" :close-on-click-modal="true">
      <template #header>
        <div class="dialog-header">
          <span class="dialog-title">录制接口</span>
          <span class="dialog-description">从指定的URL爬取所有子页面，自动提取REST接口并保存到接口列表</span>
        </div>
      </template>
      <div style="display: flex; gap: 20px;">
        <!-- 左侧：基本配置 -->
        <div style="flex: 1;">
          <div style="margin-bottom: 16px; font-weight: 500; color: #606266;">录制信息</div>
          <el-alert
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          >
            系统将从指定的URL开始，爬取所有子页面的REST接口，包括 GET、POST、PUT、DELETE 等方法
          </el-alert>
          <el-form :model="recordFormData" label-width="120px">
            <el-form-item label="选择项目" required>
              <el-select
                v-model="recordFormData.project_id"
                placeholder="选择项目"
                style="width: 100%"
                @change="recordFormData.environment_id = undefined"
                :disabled="hasProjectSelected"
                :style="{ opacity: hasProjectSelected ? 0.6 : 1 }"
              >
                <el-option v-for="project in projects" :key="project.id" :label="project.name" :value="project.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="选择环境" required>
              <el-select 
                v-model="recordFormData.environment_id" 
                placeholder="选择环境" 
                style="width: 100%" 
                :disabled="!recordFormData.project_id"
              >
                <el-option
                  v-for="env in recordFilteredEnvironments"
                  :key="env.id"
                  :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
                  :value="env.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="起始URL" required>
              <el-input 
                v-model="recordFormData.start_url" 
                placeholder="例如：http://192.168.1.100:8080" 
              />
              <div style="font-size: 12px; color: #909399; margin-top: 4px;">
                将从此URL开始爬取所有子页面的接口
              </div>
            </el-form-item>
            <el-form-item label="爬取深度">
              <el-input-number 
                v-model="recordFormData.max_depth" 
                :min="1" 
                :max="5" 
                style="width: 100%"
              />
              <div style="font-size: 12px; color: #909399; margin-top: 4px;">
                控制爬取的深度，1表示只爬取起始页面，数值越大爬取范围越广（建议2-3）
              </div>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 右侧：登录信息 -->
        <div style="flex: 1; border-left: 1px solid #e4e7ed; padding-left: 20px;">
          <div style="margin-bottom: 16px; font-weight: 500; color: #606266;">登录信息（可选）</div>
          <el-alert
            type="info"
            :closable="false"
            style="margin-bottom: 20px"
          >
            如果目标URL需要登录才能访问，请填写登录信息。系统会在爬取前自动登录。
          </el-alert>
          <el-form :model="recordFormData" label-width="100px">
            <el-form-item label="登录URL">
              <el-input 
                v-model="recordFormData.login_url" 
                placeholder="例如：http://192.168.1.100:8080/api/login" 
              />
              <div style="font-size: 12px; color: #909399; margin-top: 4px;">
                登录接口的URL地址（可选）
              </div>
            </el-form-item>
            <el-form-item label="用户名">
              <el-input 
                v-model="recordFormData.login_username" 
                placeholder="登录用户名（可选）" 
              />
            </el-form-item>
            <el-form-item label="密码">
              <el-input 
                v-model="recordFormData.login_password" 
                type="password" 
                show-password
                placeholder="登录密码（可选）" 
              />
            </el-form-item>
            <el-form-item label="登录数据（JSON）">
              <el-input 
                v-model="loginDataText" 
                type="textarea" 
                :rows="4"
                placeholder='自定义登录请求体，例如：{"username": "${username}", "password": "${password}", "captcha": ""}'
              />
              <div style="font-size: 12px; color: #909399; margin-top: 4px;">
                自定义登录请求体，如果为空则使用默认格式。可以使用占位符：${username} 和 ${password} 会被自动替换
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-start;">
          <el-button @click="recordDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="recording" @click="handleRecordSubmit">开始录制</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 执行接口抽屉 -->
    <el-drawer v-model="executeDrawerVisible" :with-header="false" size="80%" :close-on-click-modal="true">
      <div class="execute-drawer-content">
        <!-- 左侧：请求参数 -->
        <div class="execute-left">
          <!-- 顶部信息 -->
          <div style="margin-bottom: 16px;">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="项目">{{ selectedEndpoint?.project?.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="名称">{{ selectedEndpoint?.name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="标签">
                <el-tag v-for="tag in (selectedEndpoint?.tags || [])" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="描述">{{ selectedEndpoint?.description || '-' }}</el-descriptions-item>
              <el-descriptions-item label="方法">
                <el-tag :type="selectedEndpoint ? getMethodTag(selectedEndpoint.method) : 'info'">
                  {{ selectedEndpoint?.method || '-' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="路径">{{ selectedEndpoint?.path || '-' }}</el-descriptions-item>
            </el-descriptions>
          </div>
          
          <!-- 环境选择 -->
          <el-form :model="executeFormData" label-position="left" label-width="100px" class="env-form">
            <el-form-item label="选择环境">
              <el-select v-model="executeFormData.environment_id" placeholder="选择测试环境" style="width: 100%">
                <el-option
                  v-for="env in executeEnvironments"
                  :key="env.id"
                  :label="env.description ? `${env.name} (${env.base_url}) - ${env.description}` : `${env.name} (${env.base_url})`"
                  :value="env.id"
                />
              </el-select>
            </el-form-item>
          </el-form>
          
          <!-- 请求参数 -->
          <el-divider>请求参数</el-divider>
          <el-tabs v-model="activeParamTab" class="param-tabs">
            <el-tab-pane label="Header" name="headers">
              <el-input
                v-model="headersText"
                type="textarea"
                class="param-textarea"
                :autosize="{ minRows: 12, maxRows: 30 }"
                placeholder='JSON格式，例如：{"Authorization": "Bearer token"}'
              />
            </el-tab-pane>
            <el-tab-pane label="Query" name="query_params">
              <el-input
                v-model="queryParamsText"
                type="textarea"
                class="param-textarea"
                :autosize="{ minRows: 12, maxRows: 30 }"
                placeholder='JSON格式，例如：{"page": 1, "size": 10}'
              />
            </el-tab-pane>
            <el-tab-pane label="Body" name="body">
              <el-input
                v-model="bodyText"
                type="textarea"
                class="param-textarea"
                :autosize="{ minRows: 15, maxRows: 35 }"
                placeholder='JSON格式，例如：{"name": "test", "age": 18}'
              />
            </el-tab-pane>
            <el-tab-pane label="Path" name="path_params">
              <el-input
                v-model="pathParamsText"
                type="textarea"
                class="param-textarea"
                :autosize="{ minRows: 12, maxRows: 30 }"
                placeholder='JSON格式，例如：{"id": 123}'
              />
            </el-tab-pane>
            <el-tab-pane label="Assertion" name="assertions">
              <div class="assertion-list">
                <div
                  v-for="(item, index) in assertions"
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
                  <el-button
                    type="primary"
                    link
                    @click="addAssertion(index)"
                  >
                    新增
                  </el-button>
                  <el-button
                    type="danger"
                    link
                    @click="removeAssertion(index)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <!-- 右侧：响应信息 -->
        <div class="execute-right">
          <el-divider>响应信息</el-divider>
          <div v-if="!executionResult" class="no-response">
            <el-empty description="执行接口后显示响应信息" :image-size="100" />
          </div>
          <div v-else class="response-content">
            <el-descriptions :column="1" border style="margin-bottom: 16px;">
              <el-descriptions-item label="状态">
                <el-tag :type="executionResult.success ? 'success' : 'danger'">
                  {{ executionResult.success ? '成功' : '失败' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="响应状态码">
                {{ executionResult.response_status || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="响应时间">
                {{ executionResult.response_time ? `${executionResult.response_time}ms` : '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="执行时间">
                {{ formatDate(executionResult.executed_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="请求URL">
                {{ executionResult.request_url || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="错误信息" v-if="executionResult.error_message">
                <el-text type="danger" style="white-space: pre-wrap;">{{ executionResult.error_message }}</el-text>
              </el-descriptions-item>
            </el-descriptions>
            
            <el-tabs>
              <el-tab-pane label="Header">
                <pre class="response-pre">{{ formatJsonObject(executionResult.request_headers || {}) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="Query">
                <pre class="response-pre">{{ formatJsonObject(executionResult.request_query_params || {}) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="Body">
                <pre class="response-pre">{{ formatResponseBody(executionResult.request_body) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="Path">
                <pre class="response-pre">{{ formatJsonObject(executionResult.request_path_params || {}) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="响应头">
                <pre class="response-pre">{{ formatJsonObject(executionResult.response_headers || {}) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="响应体">
                <pre class="response-pre">{{ formatResponseBody(executionResult.response_body) }}</pre>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-start;">
          <el-button type="primary" :loading="executing" @click="handleExecuteSubmit">执行</el-button>
          <el-button @click="handleSave">保存</el-button>
          <el-button @click="executeDrawerVisible = false">取消</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- 执行结果对话框 -->
    <el-dialog v-model="resultDialogVisible" title="执行结果" width="1000px" :close-on-click-modal="true">
      <div v-if="executionResult">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="executionResult.success ? 'success' : 'danger'">
              {{ executionResult.success ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="响应状态码">
            {{ executionResult.response_status || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="响应时间">
            {{ executionResult.response_time ? `${executionResult.response_time}ms` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ formatDate(executionResult.executed_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="请求URL" :span="2">
            {{ executionResult.request_url || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" :span="2" v-if="executionResult.error_message">
            <el-text type="danger" style="white-space: pre-wrap;">{{ executionResult.error_message }}</el-text>
          </el-descriptions-item>
        </el-descriptions>
        <el-divider>请求详情</el-divider>
        <el-tabs>
          <el-tab-pane label="Header">
            <pre>{{ formatJsonObject(executionResult.request_headers || {}) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="Query">
            <pre>{{ formatJsonObject(executionResult.request_query_params || {}) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="Body">
            <pre>{{ formatResponseBody(executionResult.request_body) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="Path">
            <pre>{{ formatJsonObject(executionResult.request_path_params || {}) }}</pre>
          </el-tab-pane>
        </el-tabs>
        <el-divider>响应详情</el-divider>
        <el-tabs>
          <el-tab-pane label="响应头">
            <pre>{{ formatJsonObject(executionResult.response_headers || {}) }}</pre>
          </el-tab-pane>
          <el-tab-pane label="响应体">
            <pre>{{ executionResult.response_body || '-' }}</pre>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <div style="display: flex; gap: 10px; justify-content: flex-start;">
          <el-button @click="resultDialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, UploadFilled, View, Delete, Star, StarFilled, Connection, VideoCamera, Setting } from '@element-plus/icons-vue'
import * as apitestApi from '../api/apitest'
import * as projectApi from '../api/projects'
import { useProjectContext } from '../composables/useProjectContext'
import type { ApiEndpoint, ApiEnvironment, ApiTestData, ApiExecutionRecord, Project } from '../api/types'

// 项目上下文
const {
  getCurrentProjectId,
  hasProjectSelected,
  getProjects: getFilteredProjects,
  onProjectChanged,
  ensureInitialized
} = useProjectContext()

// 数据
const endpoints = ref<ApiEndpoint[]>([])
const projects = ref<Project[]>([])
const allEnvironments = ref<ApiEnvironment[]>([])  // 所有环境
const testDataList = ref<ApiTestData[]>([])
const loading = ref(false)
const executing = ref(false)
const syncing = ref(false)
const endpointsTableRef = ref()

// 根据项目筛选的环境列表
const filteredEnvironments = computed(() => {
  if (!syncFormData.project_id) {
    return allEnvironments.value
  }
  return allEnvironments.value.filter(env => env.project_id === syncFormData.project_id)
})

// 执行时使用的环境列表（根据选择的项目筛选）
const executeEnvironments = computed(() => {
  if (!executeFormData.environment_id && !selectedEndpoint.value) {
    return allEnvironments.value
  }
  const projectId = selectedEndpoint.value?.project_id
  if (!projectId) {
    return allEnvironments.value
  }
  return allEnvironments.value.filter(env => env.project_id === projectId)
})

const pagedEndpoints = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  return endpoints.value.slice(start, start + pagination.pageSize)
})

// 筛选条件
const filters = reactive({
  project_id: undefined as number | undefined,
  method: '',
  keyword: '',
  showFavorite: false  // 是否只显示收藏的接口
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

// 同步对话框（合并URL和文件上传）
const syncDialogVisible = ref(false)
const syncType = ref<'url' | 'file'>('url') // 同步类型：url 或 file
const syncFormData = reactive({
  project_id: undefined as number | undefined,
  environment_id: undefined as number | undefined,
  swagger_path: '/v3/api-docs'
})
const uploadRef = ref()
const selectedFile = ref<File | null>(null)

// 录制接口对话框
const recordDialogVisible = ref(false)
const recording = ref(false)
const recordFormData = reactive({
  project_id: undefined as number | undefined,
  environment_id: undefined as number | undefined,
  start_url: '',
  max_depth: 2,
  login_url: '',
  login_username: '',
  login_password: '',
  login_data: undefined as Record<string, any> | undefined
})
const loginDataText = ref('')

// 录制接口时使用的环境列表（根据选择的项目筛选）
const recordFilteredEnvironments = computed(() => {
  if (!recordFormData.project_id) {
    return allEnvironments.value
  }
  return allEnvironments.value.filter(env => env.project_id === recordFormData.project_id)
})

// 执行对话框
const executeDrawerVisible = ref(false)
const selectedEndpoint = ref<ApiEndpoint | null>(null)
const executeFormData = reactive({
  environment_id: undefined as number | undefined,
  test_data_id: undefined as number | undefined,  // 用于保存时识别是否有测试数据
  path_params: undefined as Record<string, any> | undefined,
  query_params: undefined as Record<string, any> | undefined,
  headers: undefined as Record<string, any> | undefined,
  body: undefined as Record<string, any> | undefined
})
const activeParamTab = ref('headers')
const pathParamsText = ref('')
const queryParamsText = ref('')
const headersText = ref('')
const bodyText = ref('')

type AssertionType = 'status_code' | 'json_path' | 'response_time' | 'contains'

interface AssertionRow {
  type: AssertionType
  operator: string
  target?: string
  expected?: string
}

const assertions = ref<AssertionRow[]>([
  { type: 'status_code', operator: 'eq', expected: '200' }
])

// 执行结果
const resultDialogVisible = ref(false)
const executionResult = ref<ApiExecutionRecord | null>(null)

// 加载接口列表
const loadEndpoints = async () => {
  loading.value = true
  try {
    const params: any = {
      method: filters.method || undefined,
      keyword: filters.keyword || undefined,
      is_favorite: filters.showFavorite ? true : undefined,
      limit: 500
    }
    
    // 如果已选择项目上下文，自动应用项目过滤（单选模式）
    const currentProjectId = getCurrentProjectId.value
    if (hasProjectSelected.value && currentProjectId) {
      // 使用当前选中的项目ID
      params.project_id = currentProjectId
    } else if (filters.project_id) {
      // 如果页面内选择了项目，使用单个项目ID
      params.project_id = filters.project_id
    }
    
    console.log('加载接口参数:', params)
    endpoints.value = await apitestApi.getApiEndpoints(params)
  } catch (error: any) {
    ElMessage.error(error.message || '加载接口列表失败')
  } finally {
    loading.value = false
  }
}

// 加载项目列表 - 使用 useProjectContext 的 getProjects，会自动根据选中的项目过滤
const loadProjects = async () => {
  try {
    projects.value = await getFilteredProjects()
    
    // 如果有选中的项目，自动设置过滤器
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.project_id = getCurrentProjectId.value
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载项目列表失败')
  }
}

// 加载环境列表
const loadEnvironments = async () => {
  try {
    allEnvironments.value = await apitestApi.getApiEnvironments()
  } catch (error: any) {
    ElMessage.error(error.message || '加载环境列表失败')
  }
}

// 加载测试数据列表
const loadTestData = async (endpointId?: number) => {
  try {
    testDataList.value = await apitestApi.getApiTestDataList(endpointId)
    // 如后端尚未生成默认测试数据，这里兜底创建一条
    if (endpointId && (!testDataList.value || testDataList.value.length === 0)) {
      const created = await apitestApi.createApiTestData({
        endpoint_id: endpointId,
        name: '测试数据#默认',
        expected_status: 200,
        path_params: {},
        query_params: {},
        headers: {},
        body: {}
      })
      testDataList.value = [created]
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载测试数据失败')
  }
}

const prefillFromTestData = () => {
  try {
  const defaultData = testDataList.value[0]
  const endpoint = selectedEndpoint.value
  
    // 优先从 swagger 参数生成默认值（作为后备）
  // 格式化空对象的辅助函数
  const formatEmptyObject = () => '{\n\n}'
  
  const swaggerDefaults = generateDefaultsFromSwagger(endpoint)
  
  if (!defaultData) {
    // 没有测试数据时使用 swagger 默认值
    pathParamsText.value = Object.keys(swaggerDefaults.path_params).length > 0 
      ? JSON.stringify(swaggerDefaults.path_params, null, 2) 
      : formatEmptyObject()
    queryParamsText.value = Object.keys(swaggerDefaults.query_params).length > 0 
      ? JSON.stringify(swaggerDefaults.query_params, null, 2) 
      : formatEmptyObject()
    headersText.value = Object.keys(swaggerDefaults.headers).length > 0 
      ? JSON.stringify(swaggerDefaults.headers, null, 2) 
      : formatEmptyObject()
    bodyText.value = Object.keys(swaggerDefaults.body).length > 0 
      ? JSON.stringify(swaggerDefaults.body, null, 2) 
      : formatEmptyObject()
    assertions.value = [{ type: 'status_code', operator: 'eq', expected: '200' }]
    executeFormData.test_data_id = undefined
    return
  }
  
  // 优先使用测试数据中的值，如果测试数据中某个字段为空或 null，则使用 swagger 默认值
  // 安全地检查字段是否存在且是对象类型，并且有内容
  const pathParams = (defaultData.path_params && typeof defaultData.path_params === 'object' && !Array.isArray(defaultData.path_params) && Object.keys(defaultData.path_params).length > 0)
    ? defaultData.path_params
    : (swaggerDefaults.path_params || {})
  const queryParams = (defaultData.query_params && typeof defaultData.query_params === 'object' && !Array.isArray(defaultData.query_params) && Object.keys(defaultData.query_params).length > 0)
    ? defaultData.query_params
    : (swaggerDefaults.query_params || {})
  const headers = (defaultData.headers && typeof defaultData.headers === 'object' && !Array.isArray(defaultData.headers) && Object.keys(defaultData.headers).length > 0)
    ? defaultData.headers
    : (swaggerDefaults.headers || {})
  const body = (defaultData.body && typeof defaultData.body === 'object' && Object.keys(defaultData.body).length > 0)
    ? defaultData.body 
    : (swaggerDefaults.body || {})
  
  // JSON 格式化显示（确保都是有效的对象）
  try {
    // 确保 pathParams 是有效对象
    if (pathParams && typeof pathParams === 'object' && !Array.isArray(pathParams)) {
      try {
        pathParamsText.value = Object.keys(pathParams).length > 0
          ? JSON.stringify(pathParams, null, 2) 
          : formatEmptyObject()
      } catch (e: any) {
        console.error('Path参数格式化错误:', e, '数据:', pathParams)
        pathParamsText.value = formatEmptyObject()
      }
    } else {
      pathParamsText.value = formatEmptyObject()
    }
    
    // 确保 queryParams 是有效对象
    if (queryParams && typeof queryParams === 'object' && !Array.isArray(queryParams)) {
      try {
        queryParamsText.value = Object.keys(queryParams).length > 0
          ? JSON.stringify(queryParams, null, 2) 
          : formatEmptyObject()
      } catch (e: any) {
        console.error('Query参数格式化错误:', e, '数据:', queryParams)
        queryParamsText.value = formatEmptyObject()
      }
    } else {
      queryParamsText.value = formatEmptyObject()
    }
    
    // 确保 headers 是有效对象
    if (headers && typeof headers === 'object' && !Array.isArray(headers)) {
      try {
        headersText.value = Object.keys(headers).length > 0
          ? JSON.stringify(headers, null, 2) 
          : formatEmptyObject()
      } catch (e: any) {
        console.error('Header参数格式化错误:', e, '数据:', headers)
        headersText.value = formatEmptyObject()
      }
    } else {
      headersText.value = formatEmptyObject()
    }
    
    // body 可以是对象或数组
    if (body && typeof body === 'object') {
      try {
        bodyText.value = Object.keys(body).length > 0 || Array.isArray(body)
          ? JSON.stringify(body, null, 2) 
          : formatEmptyObject()
      } catch (e: any) {
        console.error('Body参数格式化错误:', e, '数据:', body)
        bodyText.value = formatEmptyObject()
      }
    } else {
      bodyText.value = formatEmptyObject()
    }
  } catch (error: any) {
    console.error('JSON格式化未知错误:', error)
    // 如果JSON.stringify失败，使用空对象
    pathParamsText.value = formatEmptyObject()
    queryParamsText.value = formatEmptyObject()
    headersText.value = formatEmptyObject()
    bodyText.value = formatEmptyObject()
    ElMessage.error('测试数据格式错误，已重置为空: ' + (error.message || ''))
  }
  
    // 从测试数据中恢复断言，如果没有则使用期望状态码创建默认断言
    if (defaultData.assertions && Array.isArray(defaultData.assertions) && defaultData.assertions.length > 0) {
      assertions.value = defaultData.assertions.map((a: any) => ({
        type: a.type || 'status_code',
        operator: a.operator || 'eq',
        target: a.target || undefined,
        expected: a.expected ? String(a.expected) : undefined
      }))
    } else {
      // 如果没有断言，使用期望状态码创建默认断言
  const expected = defaultData.expected_status ? String(defaultData.expected_status) : '200'
  assertions.value = [{ type: 'status_code', operator: 'eq', expected }]
    }
  executeFormData.test_data_id = defaultData.id
  } catch (error: any) {
    console.error('prefillFromTestData 错误:', error)
    ElMessage.error('加载测试数据失败: ' + (error.message || '未知错误'))
    // 重置为空值
    const formatEmptyObject = () => '{\n\n}'
    pathParamsText.value = formatEmptyObject()
    queryParamsText.value = formatEmptyObject()
    headersText.value = formatEmptyObject()
    bodyText.value = formatEmptyObject()
  }
}

// 根据 swagger 参数生成默认值
const generateDefaultsFromSwagger = (endpoint: ApiEndpoint | null) => {
  const defaults = {
    path_params: {} as Record<string, any>,
    query_params: {} as Record<string, any>,
    headers: {} as Record<string, any>,
    body: {} as Record<string, any>
  }
  
  if (!endpoint) return defaults
  
  // 解析 parameters 列表
  const parameters = endpoint.parameters || []
  for (const param of parameters) {
    const value = generateValueFromParam(param)
    
    switch (param.in) {
      case 'path':
        defaults.path_params[param.name] = value
        break
      case 'query':
        defaults.query_params[param.name] = value
        break
      case 'header':
        defaults.headers[param.name] = value
        break
    }
  }
  
  // 解析 request_body
  const requestBody = endpoint.request_body
  if (requestBody && requestBody.schema) {
    defaults.body = generateValueFromSchema(requestBody.schema)
  }
  
  return defaults
}

// 根据参数定义生成值
const generateValueFromParam = (param: any): any => {
  // 优先使用 example
  if (param.example !== undefined && param.example !== null) {
    return param.example
  }
  
  // 其次使用 default
  if (param.default !== undefined && param.default !== null) {
    return param.default
  }
  
  // 使用 enum 的第一个值
  if (param.enum && param.enum.length > 0) {
    return param.enum[0]
  }
  
  // 根据类型生成默认值
  const type = param.type || param.schema?.type
  return generateDefaultByType(type, param.name)
}

// 根据 schema 生成值
const generateValueFromSchema = (schema: any): any => {
  if (!schema) return {}
  
  // 处理 allOf/oneOf/anyOf
  if (schema.allOf && schema.allOf.length > 0) {
    const merged: Record<string, any> = {}
    for (const subSchema of schema.allOf) {
      Object.assign(merged, generateValueFromSchema(subSchema))
    }
    return merged
  }
  
  if (schema.oneOf && schema.oneOf.length > 0) {
    return generateValueFromSchema(schema.oneOf[0])
  }
  
  if (schema.anyOf && schema.anyOf.length > 0) {
    return generateValueFromSchema(schema.anyOf[0])
  }
  
  const type = schema.type
  
  // 处理对象类型
  if (type === 'object' || schema.properties) {
    const obj: Record<string, any> = {}
    const properties = schema.properties || {}
    
    for (const [key, propSchema] of Object.entries(properties)) {
      const prop = propSchema as any
      // 优先使用 example
      if (prop.example !== undefined && prop.example !== null) {
        obj[key] = prop.example
      } else if (prop.default !== undefined && prop.default !== null) {
        obj[key] = prop.default
      } else if (prop.enum && prop.enum.length > 0) {
        obj[key] = prop.enum[0]
      } else if (prop.type === 'object' || prop.properties) {
        obj[key] = generateValueFromSchema(prop)
      } else if (prop.type === 'array') {
        obj[key] = prop.items ? [generateValueFromSchema(prop.items)] : []
      } else {
        obj[key] = generateDefaultByType(prop.type, key)
      }
    }
    return obj
  }
  
  // 处理数组类型
  if (type === 'array') {
    return schema.items ? [generateValueFromSchema(schema.items)] : []
  }
  
  // 简单类型
  if (schema.example !== undefined) return schema.example
  if (schema.default !== undefined) return schema.default
  if (schema.enum && schema.enum.length > 0) return schema.enum[0]
  
  return generateDefaultByType(type, '')
}

// 根据类型和名称生成默认值
const generateDefaultByType = (type: string | undefined, name: string): any => {
  const nameLower = name.toLowerCase()
  
  // 根据常见字段名推断
  if (nameLower.includes('id')) return 1
  if (nameLower.includes('page') && !nameLower.includes('size')) return 1
  if (nameLower.includes('size') || nameLower.includes('limit')) return 10
  if (nameLower.includes('name')) return 'test'
  if (nameLower.includes('email')) return 'test@example.com'
  if (nameLower.includes('phone') || nameLower.includes('mobile')) return '13800138000'
  if (nameLower.includes('password')) return 'password123'
  if (nameLower.includes('url') || nameLower.includes('link')) return 'https://example.com'
  if (nameLower.includes('time') || nameLower.includes('date')) return new Date().toISOString()
  if (nameLower.includes('status')) return 0
  if (nameLower.includes('type')) return 1
  if (nameLower.includes('enable') || nameLower.includes('active')) return true
  
  // 根据类型生成
  switch (type) {
    case 'integer':
    case 'number':
      return 0
    case 'boolean':
      return true
    case 'array':
      return []
    case 'object':
      return {}
    case 'string':
    default:
      return ''
  }
}


// 重置筛选
const handleReset = () => {
  filters.project_id = undefined
  filters.method = ''
  filters.keyword = ''
  filters.showFavorite = false
   pagination.currentPage = 1
  loadEndpoints()
}

// 切换收藏筛选
const toggleFavoriteFilter = () => {
  filters.showFavorite = !filters.showFavorite
  loadEndpoints()
}

// 收藏/取消收藏接口
const handleToggleFavorite = async (row: ApiEndpoint) => {
  try {
    const newFavoriteStatus = !row.is_favorite
    await apitestApi.toggleFavoriteEndpoint(row.id, newFavoriteStatus)
    row.is_favorite = newFavoriteStatus
    ElMessage.success(newFavoriteStatus ? '已收藏' : '已取消收藏')
    // 如果当前在收藏筛选模式下，取消收藏后需要重新加载列表
    if (filters.showFavorite && !newFavoriteStatus) {
      loadEndpoints()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 同步接口（合并URL和文件上传）
const handleSyncSwagger = async () => {
  await loadProjects()
  await loadEnvironments()
  
  if (projects.value.length === 0) {
    ElMessage.warning('请先创建项目')
    return
  }
  
  // 如果有项目上下文，使用项目上下文的项目ID，否则使用过滤器的项目ID或第一个项目
  syncFormData.project_id = hasProjectSelected.value ? getCurrentProjectId.value : (filters.project_id || projects.value[0].id)
  syncFormData.environment_id = undefined
  syncFormData.swagger_path = '/v3/api-docs'
  selectedFile.value = null
  syncType.value = 'url' // 默认选择URL同步
  syncDialogVisible.value = true
}

// 切换同步类型
const handleSyncTypeChange = (type: string) => {
  if (type === 'url') {
    // 切换到URL同步时，如果有环境数据则保持不变
    if (!syncFormData.project_id && allEnvironments.value.length === 0) {
      ElMessage.warning('请先创建环境')
    }
  } else {
    // 切换到文件上传时，清空环境相关数据
    syncFormData.environment_id = undefined
    syncFormData.swagger_path = '/v3/api-docs'
  }
  // 清空文件选择
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 获取完整Swagger URL
const getFullSwaggerUrl = () => {
  if (!syncFormData.environment_id || !syncFormData.swagger_path) {
    return ''
  }
  const env = filteredEnvironments.value.find(e => e.id === syncFormData.environment_id)
  if (!env) return ''
  const baseUrl = env.base_url.replace(/\/+$/, '')
  return `${baseUrl}${syncFormData.swagger_path}`
}

// 提交同步（根据类型选择URL同步或文件上传）
const handleSyncSubmit = async () => {
  if (!syncFormData.project_id) {
    ElMessage.warning('请选择项目')
    return
  }

  if (syncType.value === 'url') {
    // 从URL同步
    if (!syncFormData.environment_id) {
      ElMessage.warning('请选择环境')
      return
    }

    syncing.value = true
    try {
      const result = await apitestApi.syncSwaggerFromEnvironment({
        project_id: syncFormData.project_id,
        environment_id: syncFormData.environment_id,
        swagger_path: syncFormData.swagger_path
      })
      syncDialogVisible.value = false
      const message = result.message || `同步成功，导入 ${result.imported_count} 个接口，生成 ${result.test_data_count} 条测试数据`
      ElMessage.success(message)
      loadEndpoints()
    } catch (error: any) {
      ElMessage.error(error.message || '同步失败')
    } finally {
      syncing.value = false
    }
  } else {
    // 从文件上传
    if (!selectedFile.value) {
      ElMessage.warning('请选择文件')
      return
    }

    syncing.value = true
    try {
      const result = await apitestApi.uploadSwaggerFile(selectedFile.value, syncFormData.project_id)
      syncDialogVisible.value = false
      const message = result.message || `上传成功，导入 ${result.imported_count} 个接口，生成 ${result.test_data_count} 条测试数据`
      ElMessage.success(message)
      loadEndpoints()
    } catch (error: any) {
      ElMessage.error(error.message || '上传失败')
    } finally {
      syncing.value = false
    }
  }
}

// 文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

// 文件移除
const handleFileRemove = () => {
  selectedFile.value = null
}

// 录制接口
const handleRecordApi = async () => {
  await loadProjects()
  await loadEnvironments()
  
  if (projects.value.length === 0) {
    ElMessage.warning('请先创建项目')
    return
  }
  
  // 如果有项目上下文，使用项目上下文的项目ID，否则使用过滤器的项目ID或第一个项目
  recordFormData.project_id = hasProjectSelected.value ? getCurrentProjectId.value : (filters.project_id || projects.value[0].id)
  recordFormData.environment_id = undefined
  recordFormData.start_url = ''
  recordFormData.max_depth = 2
  recordFormData.login_url = ''
  recordFormData.login_username = ''
  recordFormData.login_password = ''
  recordFormData.login_data = undefined
  loginDataText.value = ''
  recordDialogVisible.value = true
}

// 提交录制
const handleRecordSubmit = async () => {
  if (!recordFormData.project_id) {
    ElMessage.warning('请选择项目')
    return
  }

  if (!recordFormData.environment_id) {
    ElMessage.warning('请选择环境')
    return
  }

  if (!recordFormData.start_url || !recordFormData.start_url.trim()) {
    ElMessage.warning('请输入起始URL')
    return
  }

  // 验证URL格式
  try {
    new URL(recordFormData.start_url)
  } catch (e) {
    ElMessage.warning('请输入有效的URL格式')
    return
  }

  // 处理登录数据
  let loginData = undefined
  if (loginDataText.value.trim()) {
    try {
      // 替换占位符
      let loginDataStr = loginDataText.value
        .replace(/\$\{username\}/g, recordFormData.login_username || '')
        .replace(/\$\{password\}/g, recordFormData.login_password || '')
      loginData = JSON.parse(loginDataStr)
    } catch (e) {
      ElMessage.warning('登录数据JSON格式错误')
      return
    }
  }

  recording.value = true
  try {
    const result = await apitestApi.recordApiFromUrl({
      project_id: recordFormData.project_id,
      environment_id: recordFormData.environment_id,
      start_url: recordFormData.start_url.trim(),
      max_depth: recordFormData.max_depth,
      login_url: recordFormData.login_url.trim() || undefined,
      login_username: recordFormData.login_username.trim() || undefined,
      login_password: recordFormData.login_password || undefined,
      login_data: loginData
    })
    recordDialogVisible.value = false
    const message = result.message || `录制成功，发现 ${result.discovered_count} 个接口，导入 ${result.imported_count} 个接口`
    ElMessage.success(message)
    loadEndpoints()
  } catch (error: any) {
    ElMessage.error(error.message || '录制失败')
  } finally {
    recording.value = false
  }
}

// 执行接口
const handleExecute = async (row: ApiEndpoint) => {
  selectedEndpoint.value = row
  executeFormData.environment_id = undefined
  executeFormData.test_data_id = undefined
  executeFormData.path_params = undefined
  executeFormData.query_params = undefined
  executeFormData.headers = undefined
  executeFormData.body = undefined
  activeParamTab.value = 'headers'
  assertions.value = [{ type: 'status_code', operator: 'eq', expected: '200' }]
  executionResult.value = null  // 清空之前的执行结果
  
  // 清空所有文本输入框
  pathParamsText.value = ''
  queryParamsText.value = ''
  headersText.value = ''
  bodyText.value = ''
  
  await loadEnvironments()
  await loadTestData(row.id)
  prefillFromTestData()

  if (executeEnvironments.value.length === 0) {
    ElMessage.warning('请先为该项目创建测试环境')
    return
  }
  // 默认选中该项目第一个环境
  executeFormData.environment_id = executeEnvironments.value[0]?.id
  
  executeDrawerVisible.value = true
}

// 解析包含模板语法的JSON（支持 NUM(), STR(), $API[N].path, $var 等）
const parseJsonWithTemplatesForExecute = (jsonText: string): any => {
  try {
    return JSON.parse(jsonText)
  } catch {
    // 如果包含模板语法，将模板语法替换为字符串占位符后再解析
    try {
      let placeholderJson = jsonText
      
      // 先处理 NUM() 和 STR() 格式（优先级最高）
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
      
      // 处理 $API[N].path 语法
      placeholderJson = placeholderJson.replace(/\$API\[(\d+)\]\.([a-zA-Z0-9_.]+)/g, (match, index, path) => {
        return `"__TEMPLATE__API[${index}].${path}__TEMPLATE__"`
      })
      // 处理 $var 语法
      placeholderJson = placeholderJson.replace(/\$([a-zA-Z_][a-zA-Z0-9_]*)/g, (match, varName) => {
        return `"__TEMPLATE__${varName}__TEMPLATE__"`
      })
      // 兼容旧的 {{ ... }} 语法
      placeholderJson = placeholderJson.replace(/\{\{\s*([^}]+)\s*\}\}/g, (match, expr) => {
        return `"__TEMPLATE__${expr.trim().replace(/"/g, '\\"')}__TEMPLATE__"`
      })
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

// 提交执行
const handleExecuteSubmit = async () => {
  if (!executeFormData.environment_id) {
    ElMessage.warning('请选择测试环境')
    return
  }

  if (!selectedEndpoint.value) {
    return
  }

  // 解析JSON参数（支持模板语法）
  try {
    if (pathParamsText.value.trim()) {
      try {
        const parsed = parseJsonWithTemplatesForExecute(pathParamsText.value.trim())
        executeFormData.path_params = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : {}
      } catch (e: any) {
        console.error('Path参数JSON解析错误:', e, '内容:', pathParamsText.value)
        ElMessage.error('Path参数JSON格式错误: ' + (e.message || '请检查输入'))
        return
      }
    }
    if (queryParamsText.value.trim()) {
      try {
        const parsed = parseJsonWithTemplatesForExecute(queryParamsText.value.trim())
        executeFormData.query_params = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : {}
      } catch (e: any) {
        console.error('Query参数JSON解析错误:', e, '内容:', queryParamsText.value)
        ElMessage.error('Query参数JSON格式错误: ' + (e.message || '请检查输入'))
        return
      }
    }
    if (headersText.value.trim()) {
      try {
        const parsed = parseJsonWithTemplatesForExecute(headersText.value.trim())
        executeFormData.headers = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : {}
      } catch (e: any) {
        console.error('Header参数JSON解析错误:', e, '内容:', headersText.value)
        ElMessage.error('Header参数JSON格式错误: ' + (e.message || '请检查输入'))
        return
      }
    }
    if (bodyText.value.trim()) {
      try {
        const parsed = parseJsonWithTemplatesForExecute(bodyText.value.trim())
        // body 可以是对象或数组
        executeFormData.body = (parsed && (typeof parsed === 'object' || Array.isArray(parsed))) ? parsed : {}
      } catch (e: any) {
        console.error('Body参数JSON解析错误:', e, '内容:', bodyText.value)
        ElMessage.error('Body参数JSON格式错误: ' + (e.message || '请检查输入'))
        return
      }
    }
    // assertions 是数组，不需要JSON解析，直接使用即可
  } catch (error: any) {
    console.error('JSON解析未知错误:', error)
    ElMessage.error('JSON格式错误: ' + (error.message || '请检查输入'))
    return
  }

  executing.value = true
  try {
    // 准备断言数据
    const assertionsToSend = assertions.value.map(a => ({
      type: a.type,
      operator: a.operator,
      target: a.target || null,
      expected: a.expected || null
    }))
    
    const payload = {
      environment_id: executeFormData.environment_id as number,
      test_data_id: executeFormData.test_data_id,
      path_params: executeFormData.path_params,
      query_params: executeFormData.query_params,
      headers: executeFormData.headers,
      body: executeFormData.body,
      assertions: assertionsToSend
    }
    executionResult.value = await apitestApi.executeApiEndpoint(selectedEndpoint.value.id, payload)
    ElMessage.success('执行完成')
    // 不关闭抽屉，在右侧显示响应信息
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
    executionResult.value = null
  } finally {
    executing.value = false
  }
}

const handleSave = async () => {
  if (!selectedEndpoint.value) {
    return
  }

  let pathParams: any
  let queryParams: any
  let headers: any
  let body: any

  try {
    if (pathParamsText.value.trim()) {
      const parsed = parseJsonWithTemplatesForExecute(pathParamsText.value.trim())
      pathParams = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : undefined
    }
    if (queryParamsText.value.trim()) {
      const parsed = parseJsonWithTemplatesForExecute(queryParamsText.value.trim())
      queryParams = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : undefined
    }
    if (headersText.value.trim()) {
      const parsed = parseJsonWithTemplatesForExecute(headersText.value.trim())
      headers = (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) ? parsed : undefined
    }
    if (bodyText.value.trim()) {
      const parsed = parseJsonWithTemplatesForExecute(bodyText.value.trim())
      // body 可以是对象或数组
      body = (parsed && (typeof parsed === 'object' || Array.isArray(parsed))) ? parsed : undefined
    }
  } catch (error: any) {
    ElMessage.error('JSON格式错误，请检查输入: ' + (error.message || ''))
    return
  }

  try {
    // 从断言行中抽取期望状态码
    const statusAssertion = assertions.value.find(a => a.type === 'status_code' && a.expected)
    const expectedStatus = statusAssertion && statusAssertion.expected ? Number(statusAssertion.expected) : 200

    // 保存断言列表
    const assertionsToSave = assertions.value.map(a => ({
      type: a.type,
      operator: a.operator,
      target: a.target || null,
      expected: a.expected || null
    }))

    if (executeFormData.test_data_id) {
      // 更新已有测试数据
      await apitestApi.updateApiTestData(executeFormData.test_data_id, {
        path_params: pathParams,
        query_params: queryParams,
        headers,
        body,
        expected_status: expectedStatus,
        assertions: assertionsToSave
      })
      ElMessage.success('保存成功')
    } else {
      // 新建测试数据
      const created = await apitestApi.createApiTestData({
        endpoint_id: selectedEndpoint.value.id,
        name: '测试数据#手动保存',
        path_params: pathParams,
        query_params: queryParams,
        headers,
        body,
        expected_status: expectedStatus,
        assertions: assertionsToSave
      })
      executeFormData.test_data_id = created.id
      ElMessage.success('保存成功')
    }

    // 刷新测试数据列表
    await loadTestData(selectedEndpoint.value.id)
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

// 删除接口
const handleDeleteEndpoint = async (row: ApiEndpoint) => {
  try {
    await ElMessageBox.confirm('确定删除该接口吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await apitestApi.deleteApiEndpoint(row.id)
    ElMessage.success('删除成功')
    loadEndpoints()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}


const addAssertion = (index?: number) => {
  const row: AssertionRow = { type: 'status_code', operator: 'eq', expected: '200' }
  if (index === undefined || index < 0 || index >= assertions.value.length) {
    assertions.value.push(row)
  } else {
    assertions.value.splice(index + 1, 0, row)
  }
}

const removeAssertion = (index: number) => {
  if (assertions.value.length <= 1) {
    assertions.value = [{ type: 'status_code', operator: 'eq', expected: '200' }]
    return
  }
  assertions.value.splice(index, 1)
}


// 工具函数
const getMethodTag = (method: string) => {
  const map: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
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

// 格式化空对象的辅助函数
const formatEmptyObject = () => '{\n\n}'

// 格式化JSON对象，空对象返回格式化字符串
const formatJsonObject = (obj: any) => {
  if (!obj || (typeof obj === 'object' && !Array.isArray(obj) && Object.keys(obj).length === 0)) {
    return formatEmptyObject()
  }
  return JSON.stringify(obj, null, 2)
}

// 格式化响应体为JSON
const formatResponseBody = (body: any) => {
  if (!body) return '-'
  try {
    // 尝试解析为JSON
    const parsed = typeof body === 'string' ? JSON.parse(body) : body
    // 如果是空对象，返回格式化的字符串
    if (typeof parsed === 'object' && !Array.isArray(parsed) && Object.keys(parsed).length === 0) {
      return formatEmptyObject()
    }
    return JSON.stringify(parsed, null, 2)
  } catch {
    // 如果不是JSON，直接返回
    return body
  }
}


// 监听分页变化，重新布局表格
watch(() => pagination.currentPage, async () => {
  await nextTick()
  if (endpointsTableRef.value) {
    endpointsTableRef.value.doLayout()
  }
})

// 初始化
// 监听项目切换事件
const handleProjectChanged = () => {
  // 项目切换后，自动刷新数据
  loadEndpoints()
}

onMounted(async () => {
  // 确保项目上下文已初始化
  await ensureInitialized()
  // 如果有选中的项目，自动设置过滤器
  if (hasProjectSelected.value && getCurrentProjectId.value) {
    filters.project_id = getCurrentProjectId.value
  }
  loadProjects()
  loadEnvironments()
  loadEndpoints()
  
  // 监听项目切换事件
  const cleanup = onProjectChanged(() => {
    if (hasProjectSelected.value && getCurrentProjectId.value) {
      filters.project_id = getCurrentProjectId.value
    }
    loadProjects()
    loadEndpoints()
  })
  
  // 组件卸载时清理监听
  onUnmounted(() => {
    cleanup()
  })
})
</script>

<style scoped>
.api-test-page {
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

/* 确保按钮之间的间距一致 */
.filter-left > * {
  margin: 0;
}

.filter-right {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;
}

.filter-row :deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.filter-row :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.filter-row :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
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
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.table-card :deep(.el-table__body td) {
  padding: 16px 0;
  border-bottom: 1px solid #f0f2f5;
}

pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.5;
  margin: 0;
}

.flow-step-editor {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.flow-endpoints {
  margin-bottom: 16px;
}

.flow-endpoints :deep(.el-input) {
  margin-bottom: 12px;
}

.flow-endpoints :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.param-tabs {
  margin-top: 12px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.param-textarea :deep(textarea) {
  font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 13px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  transition: border-color 0.3s ease;
}

.param-textarea :deep(textarea:focus) {
  border-color: #409eff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
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

/* 执行接口抽屉布局 */
.env-form {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.env-form :deep(.el-form-item__label) {
  display: flex;
  align-items: center;
  height: 40px;
  line-height: 40px;
  justify-content: flex-start;
  font-weight: 500;
  color: #555;
}

.env-form :deep(.el-select) {
  vertical-align: middle;
}

.execute-drawer-content {
  display: flex;
  gap: 24px;
  height: calc(100vh - 120px);
  overflow: hidden;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f0f4f8 100%);
}

.execute-left {
  flex: 1;
  overflow-y: auto;
  padding-right: 16px;
  min-width: 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.execute-right {
  flex: 1;
  overflow-y: auto;
  padding-left: 16px;
  min-width: 0;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.no-response {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
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

/* 自定义滚动条 */
.execute-left::-webkit-scrollbar,
.execute-right::-webkit-scrollbar {
  width: 6px;
}

.execute-left::-webkit-scrollbar-thumb,
.execute-right::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.execute-left::-webkit-scrollbar-thumb:hover,
.execute-right::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}
/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from, .slide-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .api-test-page {
    padding: 10px;
  }
  
  .execute-drawer-content {
    flex-direction: column;
  }
  
  .execute-left, .execute-right {
    margin-bottom: 20px;
  }
}

/* Element Plus 组件美化 */
:deep(.el-tag) {
  border-radius: 4px;
  transition: all 0.3s ease;
}

:deep(.el-tag:hover) {
  transform: scale(1.05);
}

:deep(.el-card) {
  border: none;
  transition: box-shadow 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e4e7ed;
}

:deep(.el-tabs__item) {
  font-weight: 500;
  transition: color 0.3s ease;
}

:deep(.el-tabs__item:hover) {
  color: #409eff;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

:deep(.el-divider) {
  margin: 20px 0;
  background-color: #e4e7ed;
}

:deep(.el-button) {
  border-radius: 6px;
}

/* 对话框和抽屉美化 */
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

:deep(.el-dialog__header) {
  background: linear-gradient(90deg, #f5f9ff, #f0f7ff);
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__title) {
  font-weight: 600;
  color: #333;
}

:deep(.el-drawer) {
  border-radius: 12px 0 0 12px;
  overflow: hidden;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
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

/* 抽屉底部按钮样式 */
:deep(.el-drawer__footer .el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
  color: #ffffff !important;
}

:deep(.el-drawer__footer .el-button--primary:hover) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
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
