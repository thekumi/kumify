import { api } from './client'

export const getHabits   = ()      => api.getAll('/habits/')
export const createHabit = (d)     => api.post('/habits/', d)
export const updateHabit = (id, d) => api.patch(`/habits/${id}/`, d)
export const deleteHabit = (id)    => api.delete(`/habits/${id}/`)
