import request from './index'
import type { User } from './types'

export const getUsers = (params?: any) => {
  return request.get<any, { total: number; items: User[]; page: number; page_size: number }>('/users', { params })
}

export const getUser = (id: number) => {
  return request.get<any, User>(`/users/${id}`)
}

export const createUser = (data: Partial<User>) => {
  return request.post<any, User>('/users', data)
}

export const updateUser = (id: number, data: Partial<User>) => {
  return request.put<any, User>(`/users/${id}`, data)
}

export const deleteUser = (id: number) => {
  return request.delete(`/users/${id}`)
}

