import { api } from './client'

export const getHabits    = ()      => api.getAll('/habits/')
export const createHabit  = (d)     => api.post('/habits/', d)
export const updateHabit  = (id, d) => api.patch(`/habits/${id}/`, d)
export const deleteHabit  = (id)    => api.delete(`/habits/${id}/`)

export const getHabitLogs   = (page=1) => api.get(`/habit-logs/?page=${page}`)
export const createHabitLog = (d)      => api.post('/habit-logs/', d)
export const deleteHabitLog = (id)     => api.delete(`/habit-logs/${id}/`)
