import request from './index'
import type { TestCase } from './types'

export const getTestCases = (params?: any) => {
  return request.get<any, TestCase[]>('/testcases', { params })
}

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
