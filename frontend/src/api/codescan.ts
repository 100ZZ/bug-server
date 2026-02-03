import request from './index'
import type { CodeScan } from './types'

export const getCodeScans = (params?: { project_id?: number; keyword?: string }) => {
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

// 执行扫描并查询 SonarQube 状态
export interface ScanCondition {
  metric_key: string
  metric_name: string
  actual_value: string
  error_threshold: string
  comparator: string
}

export interface ScanExecuteResult {
  message: string
  result: 'passed' | 'failed' | null
  scan_time: string | null
  sonar_status?: string
  error_message?: string | null
  conditions?: ScanCondition[]
}

export const executeCodeScan = (id: number) => {
  return request.post<any, ScanExecuteResult>(`/code-scans/${id}/execute`)
}

// 获取扫描状态
export interface ScanStatusResult {
  result: 'passed' | 'failed' | null
  scan_time: string | null
  sonar_status?: string
  message?: string
}

export const getCodeScanStatus = (id: number) => {
  return request.get<any, ScanStatusResult>(`/code-scans/${id}/status`)
}

// 获取扫描历史记录
export interface CodeScanResultHistory {
  id: number
  status: 'pending' | 'completed' | 'failed'
  error_message?: string | null
  created_at?: string | null
  updated_at?: string | null
}

export const getCodeScanResults = (id: number) => {
  return request.get<any, CodeScanResultHistory[]>(`/code-scans/${id}/results`)
}
