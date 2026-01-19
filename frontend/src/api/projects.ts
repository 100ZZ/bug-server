import request from './index'
import type { Project } from './types'

export const getProjects = (params?: any) => {
  return request.get<any, Project[]>('/projects', { params })
}

export const getProject = (id: number) => {
  return request.get<any, Project>(`/projects/${id}`)
}

export const createProject = (data: Partial<Project>) => {
  return request.post<any, Project>('/projects', data)
}

export const updateProject = (id: number, data: Partial<Project>) => {
  return request.put<any, Project>(`/projects/${id}`, data)
}

export const deleteProject = (id: number) => {
  return request.delete(`/projects/${id}`)
}

