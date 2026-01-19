import request from './index'
import type { Bug, Comment, Statistics } from './types'

export const getBugs = (params?: any) => {
  return request.get<any, Bug[]>('/bugs', { params })
}

export const getBug = (id: number) => {
  return request.get<any, Bug>(`/bugs/${id}`)
}

export const createBug = (data: Partial<Bug>) => {
  return request.post<any, Bug>('/bugs', data)
}

export const updateBug = (id: number, data: Partial<Bug>) => {
  return request.put<any, Bug>(`/bugs/${id}`, data)
}

export const deleteBug = (id: number) => {
  return request.delete(`/bugs/${id}`)
}

export const getBugComments = (bugId: number) => {
  return request.get<any, Comment[]>(`/bugs/${bugId}/comments`)
}

export const createComment = (data: Partial<Comment>) => {
  return request.post<any, Comment>('/comments', data)
}

export const getStatistics = (projectId?: number) => {
  return request.get<any, Statistics>('/statistics', { params: { project_id: projectId } })
}

