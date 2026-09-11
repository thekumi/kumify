import { api } from './client'

export const getDreams   = (page=1) => api.get(`/dreams/?page=${page}`)
export const getDream    = (id)     => api.get(`/dreams/${id}/`)
export const createDream = (d)      => api.post('/dreams/', d)
export const updateDream = (id, d)  => api.patch(`/dreams/${id}/`, d)
export const deleteDream = (id)     => api.delete(`/dreams/${id}/`)

export const getThemes   = ()       => api.getAll('/dream-themes/')
export const createTheme = (d)      => api.post('/dream-themes/', d)
export const updateTheme = (id, d)  => api.patch(`/dream-themes/${id}/`, d)
export const deleteTheme = (id)     => api.delete(`/dream-themes/${id}/`)
