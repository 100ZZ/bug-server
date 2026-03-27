import request from './index'

export interface RequirementCreate {
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

export interface RequirementUpdate {
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

export interface RequirementChild {
  id: number
  parent_id?: number | null
  title: string
  project?: { id: number; name: string }
  sprint?: { id: number; name: string }
  priority: string
  status: string
  due_date?: string | null
  assignee_id?: number | null
  assignee?: { id: number; username: string; display_name?: string }
  created_at: string
  updated_at: string
}

export interface Requirement {
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
  children?: RequirementChild[]
}

export function getRequirements(params?: {
  project_id?: number
  sprint_id?: number
  status?: string
  priority?: string
  keyword?: string
  page?: number
  page_size?: number
}): Promise<{ total: number; items: Requirement[]; page: number; page_size: number }> {
  return request.get('/requirements', { params })
}

export function getRequirement(id: number): Promise<Requirement> {
  return request.get(`/requirements/${id}`)
}

export function createRequirement(data: RequirementCreate): Promise<Requirement> {
  return request.post('/requirements', data)
}

export function updateRequirement(id: number, data: RequirementUpdate): Promise<Requirement> {
  return request.put(`/requirements/${id}`, data)
}

export function deleteRequirement(id: number): Promise<void> {
  return request.delete(`/requirements/${id}`)
}
