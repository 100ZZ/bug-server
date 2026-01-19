import request from './index'
import type { TestCaseReview, TestCaseReviewItem } from './types'

export const getTestCaseReviews = (params?: any) => {
  return request.get<any, TestCaseReview[]>('/testcase_reviews', { params })
}

export const getTestCaseReview = (id: number) => {
  return request.get<any, TestCaseReview>(`/testcase_reviews/${id}`)
}

export const createTestCaseReview = (data: Partial<TestCaseReview>) => {
  return request.post<any, TestCaseReview>('/testcase_reviews', data)
}

export const updateTestCaseReview = (id: number, data: Partial<TestCaseReview>) => {
  return request.put<any, TestCaseReview>(`/testcase_reviews/${id}`, data)
}

export const deleteTestCaseReview = (id: number) => {
  return request.delete(`/testcase_reviews/${id}`)
}

// 评审用例相关API
export const getReviewItems = (reviewId: number) => {
  return request.get<any, TestCaseReviewItem[]>(`/testcase_reviews/${reviewId}/items`)
}

export const addReviewItem = (reviewId: number, data: Partial<TestCaseReviewItem>) => {
  return request.post<any, TestCaseReviewItem>(`/testcase_reviews/${reviewId}/items`, data)
}

export const updateReviewItem = (reviewId: number, itemId: number, data: Partial<TestCaseReviewItem>) => {
  return request.put<any, TestCaseReviewItem>(`/testcase_reviews/${reviewId}/items/${itemId}`, data)
}

export const deleteReviewItem = (reviewId: number, itemId: number) => {
  return request.delete(`/testcase_reviews/${reviewId}/items/${itemId}`)
}
