import request from './index'

export interface WorkTaskCreate {
  project_id: number
  sprint_id?: number | null
  title: string
  content?: string
  priority?: string
  status?: string
  assignee_id?: number | null
  parent_id?: number | null
  start_date?: string | null
  due_date?: string | null
}

export interface WorkTaskUpdate {
  sprint_id?: number | null
  title?: string
  content?: string
  priority?: string
  status?: string
  assignee_id?: number | null
  parent_id?: number | null
  start_date?: string | null
  due_date?: string | null
}

export interface WorkTaskChild {
  id: number
  parent_id?: number | null
  title: string
  priority: string
  status: string
  due_date?: string | null
  assignee_id?: number | null
  assignee?: { id: number; username: string; display_name?: string }
  project?: { id: number; name: string }
  sprint?: { id: number; name: string }
  created_at: string
  updated_at: string
}

export interface WorkTask {
  id: number
  project_id: number
  sprint_id?: number | null
  parent_id?: number | null
  title: string
  content?: string
  priority: string
  status: string
  assignee_id?: number | null
  created_by: number
  start_date?: string | null
  due_date?: string | null
  created_at: string
  updated_at: string
  project?: { id: number; name: string }
  sprint?: { id: number; name: string }
  assignee?: { id: number; username: string; display_name?: string }
  creator?: { id: number; username: string; display_name?: string }
  children?: WorkTaskChild[]
}

export function getWorkTasks(params?: {
  project_id?: number
  sprint_id?: number
  status?: string
  priority?: string
  keyword?: string
  page?: number
  page_size?: number
}): Promise<{ total: number; items: WorkTask[]; page: number; page_size: number }> {
  return request.get('/worktasks', { params })
}

export function getWorkTask(id: number): Promise<WorkTask> {
  return request.get(`/worktasks/${id}`)
}

export function createWorkTask(data: WorkTaskCreate): Promise<WorkTask> {
  return request.post('/worktasks', data)
}

export function updateWorkTask(id: number, data: WorkTaskUpdate): Promise<WorkTask> {
  return request.put(`/worktasks/${id}`, data)
}

export function deleteWorkTask(id: number): Promise<void> {
  return request.delete(`/worktasks/${id}`)
}
