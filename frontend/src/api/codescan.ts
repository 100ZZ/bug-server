import request from './index'
import type { CodeScan, CodeScanResult } from './types'

export const getCodeScans = (params?: { project_id?: number; keyword?: string; result?: string }) => {
  return request.get<any, CodeScan[]>('/code-scans', { params })
}

export const getCodeScan = (id: number) => {
  return request.get<any, CodeScan>(`/code-scans/${id}`)
}

export const createCodeScan = (data: Partial<CodeScan>) => {
  return request.post<any, CodeScan>('/code-scans', data)
}

export const updateCodeScan = (id: number, data: Partial<CodeScan>) => {
  return request.put<any, CodeScan>(`/code-scans/${id}`, data)
}

export const deleteCodeScan = (id: number) => {
  return request.delete(`/code-scans/${id}`)
}

export const executeCodeScan = (id: number) => {
  return request.post(`/code-scans/${id}/execute`)
}

export const getCodeScanResult = (id: number) => {
  return request.get<any, CodeScanResult>(`/code-scans/${id}/result`)
}

