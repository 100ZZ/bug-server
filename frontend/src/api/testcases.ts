import request from './index'
import type { TestCase } from './types'

export interface TestCaseDirectory {
  id: number
  project_id: number
  path: string
  name: string
  created_at?: string
}

export const getTestCases = (params?: any) => {
  return request.get<any, { total: number; items: TestCase[]; page: number; page_size: number }>('/testcases', { params })
}

// 目录 API
export const getTestCaseDirectories = (project_id: number) =>
  request.get<any, TestCaseDirectory[]>('/testcase-directories', { params: { project_id } })

export const createTestCaseDirectory = (data: { project_id: number; path: string; name: string }) =>
  request.post<any, TestCaseDirectory>('/testcase-directories', data)

export const updateTestCaseDirectory = (id: number, data: { path?: string; name?: string }) =>
  request.put<any, TestCaseDirectory>(`/testcase-directories/${id}`, data)

export const deleteTestCaseDirectory = (id: number) =>
  request.delete(`/testcase-directories/${id}`)

export const getTestCase = (id: number) => {
  return request.get<any, TestCase>(`/testcases/${id}`)
}

export const createTestCase = (data: Partial<TestCase>) => {
  return request.post<any, TestCase>('/testcases', data)
}

export const updateTestCase = (id: number, data: Partial<TestCase>) => {
  return request.put<any, TestCase>(`/testcases/${id}`, data)
}

export const deleteTestCase = (id: number) => {
  return request.delete(`/testcases/${id}`)
}

export const exportTestCases = (params: any) => {
  return request.get<Blob, Blob>('/testcases/export', {
    params,
    responseType: 'blob' as any
  })
}

export const importTestCases = (projectId: number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<any, { message: string; imported: number; skipped: number; errors: string[] }>(
    '/testcases/import',
    formData,
    {
      params: { project_id: projectId },
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  )
}

export const batchDeleteTestCases = (ids: number[]) => {
  return request.post('/testcases/batch-delete', ids)
}

export const generateTestCasesFromImage = (projectId: number, imageFile: File, modelId?: number) => {
  const formData = new FormData()
  formData.append('project_id', projectId.toString())
  formData.append('image', imageFile)
  if (modelId) {
    formData.append('model_id', modelId.toString())
  }
  return request.post<any, TestCase[]>('/testcases/generate-from-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
