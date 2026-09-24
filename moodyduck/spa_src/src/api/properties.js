import { api } from './client'

export const getProperties    = ()      => api.getAll('/properties/')
export const createProperty   = (d)     => api.post('/properties/', d)
export const updateProperty   = (id, d) => api.patch(`/properties/${id}/`, d)
export const deleteProperty   = (id)    => api.delete(`/properties/${id}/`)
