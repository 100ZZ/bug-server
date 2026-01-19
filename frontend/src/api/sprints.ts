import request from './index'
import type { Sprint } from './types'

export interface SprintCreate {
  project_id: number
  name: string
  goal?: string
  owner?: string
  start_date: string
  end_date: string
}

export interface SprintUpdate {
  name?: string
  goal?: string
  owner?: string
  start_date?: string
  end_date?: string
}

export function getSprints(params?: { project_id?: number; skip?: number; limit?: number }): Promise<Sprint[]> {
  return request.get('/sprints', { params })
}

export function getSprint(id: number): Promise<Sprint> {
  return request.get(`/sprints/${id}`)
}

export function createSprint(data: SprintCreate): Promise<Sprint> {
  return request.post('/sprints', data)
}

export function updateSprint(id: number, data: SprintUpdate): Promise<Sprint> {
  return request.put(`/sprints/${id}`, data)
}

export function deleteSprint(id: number): Promise<void> {
  return request.delete(`/sprints/${id}`)
}
