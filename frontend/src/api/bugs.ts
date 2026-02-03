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

// 缺陷图片管理
export interface BugImageUploadResponse {
  url: string
  filename: string
  size: number
  content_type: string
}

export interface BugImageListResponse {
  images: Array<{
    url: string
    filename: string
    size: number
  }>
}

/**
 * 上传缺陷截图
 * @param bugKey 缺陷编号（如 BUG-001）
 * @param file 图片文件
 */
export const uploadBugImage = (bugKey: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<any, BugImageUploadResponse>(`/bugs/${bugKey}/images`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取缺陷的所有截图
 * @param bugKey 缺陷编号
 */
export const getBugImages = (bugKey: string) => {
  return request.get<any, BugImageListResponse>(`/bugs/${bugKey}/images`)
}

/**
 * 删除缺陷截图
 * @param bugKey 缺陷编号
 * @param filename 图片文件名
 */
export const deleteBugImage = (bugKey: string, filename: string) => {
  return request.delete(`/bugs/${bugKey}/images/${filename}`)
}

