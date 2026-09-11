import { api } from './client'

export const getMoods        = ()       => api.getAll('/moods/')
export const createMood      = (d)      => api.post('/moods/', d)
export const updateMood      = (id, d)  => api.patch(`/moods/${id}/`, d)
export const deleteMood      = (id)     => api.delete(`/moods/${id}/`)

export const getActivities   = ()       => api.getAll('/activities/')
export const createActivity  = (d)      => api.post('/activities/', d)
export const updateActivity  = (id, d)  => api.patch(`/activities/${id}/`, d)
export const deleteActivity  = (id)     => api.delete(`/activities/${id}/`)

export const getStatuses     = (page=1) => api.get(`/statuses/?page=${page}`)
export const getStatus       = (id)     => api.get(`/statuses/${id}/`)
export const createStatus    = (d)      => api.post('/statuses/', d)
export const updateStatus    = (id, d)  => api.patch(`/statuses/${id}/`, d)
export const deleteStatus    = (id)     => api.delete(`/statuses/${id}/`)

export const getDashboard    = ()       => api.get('/stats/dashboard/')
