import request from './index'
import type { Model } from './types'

export const getModels = (params?: { keyword?: string; page?: number; page_size?: number }) => {
  return request.get<any, { total: number; items: Model[]; page: number; page_size: number }>('/models', { params })
}

export const getModel = (id: number) => {
  return request.get<any, Model>(`/models/${id}`)
}

export const createModel = (data: Partial<Model>) => {
  return request.post<any, Model>('/models', data)
}

export const updateModel = (id: number, data: Partial<Model>) => {
  return request.put<any, Model>(`/models/${id}`, data)
}

export const deleteModel = (id: number) => {
  return request.delete(`/models/${id}`)
}

export const setDefaultModel = (id: number) => {
  return request.post(`/models/${id}/set-default`)
}

export const testModel = (id: number, prompt: string) => {
  return request.post<any, { response: string }>(`/models/${id}/test`, { prompt })
}

