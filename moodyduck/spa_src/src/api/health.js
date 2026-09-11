import { api } from './client'

export const getParameters      = ()      => api.getAll('/health/parameters/')
export const createParameter    = (d)     => api.post('/health/parameters/', d)
export const updateParameter    = (id, d) => api.patch(`/health/parameters/${id}/`, d)
export const deleteParameter    = (id)    => api.delete(`/health/parameters/${id}/`)

export const getLogs            = (page=1) => api.get(`/health/logs/?page=${page}`)
export const getLog             = (id)    => api.get(`/health/logs/${id}/`)
export const createLog          = (d)     => api.post('/health/logs/', d)
export const updateLog          = (id, d) => api.patch(`/health/logs/${id}/`, d)
export const deleteLog          = (id)    => api.delete(`/health/logs/${id}/`)

export const getMedications     = ()      => api.getAll('/health/medications/')
export const createMedication   = (d)     => api.post('/health/medications/', d)
export const updateMedication   = (id, d) => api.patch(`/health/medications/${id}/`, d)
export const deleteMedication   = (id)    => api.delete(`/health/medications/${id}/`)

export const getVaccinations    = ()      => api.getAll('/health/vaccinations/')
export const createVaccination  = (d)     => api.post('/health/vaccinations/', d)
export const updateVaccination  = (id, d) => api.patch(`/health/vaccinations/${id}/`, d)
export const deleteVaccination  = (id)    => api.delete(`/health/vaccinations/${id}/`)
