import { api } from './client'

export const getPeople      = ()       => api.getAll('/friends/')
export const getPerson      = (id)     => api.get(`/friends/${id}/`)
export const createPerson   = (d)      => api.post('/friends/', d)
export const updatePerson   = (id, d)  => api.patch(`/friends/${id}/`, d)
export const deletePerson   = (id)     => api.delete(`/friends/${id}/`)
