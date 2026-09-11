import { api } from './client'

export const getRecords   = (page=1) => api.get(`/cbt/records/?page=${page}`)
export const getRecord    = (id)     => api.get(`/cbt/records/${id}/`)
export const createRecord = (d)      => api.post('/cbt/records/', d)
export const updateRecord = (id, d)  => api.patch(`/cbt/records/${id}/`, d)
export const deleteRecord = (id)     => api.delete(`/cbt/records/${id}/`)
