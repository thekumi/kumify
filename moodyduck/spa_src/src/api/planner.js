import { api } from './client'

export const getCalendars   = ()      => api.getAll('/planner/calendars/')
export const createCalendar = (d)     => api.post('/planner/calendars/', d)
export const updateCalendar = (id, d) => api.patch(`/planner/calendars/${id}/`, d)
export const deleteCalendar = (id)    => api.delete(`/planner/calendars/${id}/`)

export const getEvents = (params = {}) => {
  const qs = new URLSearchParams(params).toString()
  return api.getAll(`/planner/events/${qs ? '?' + qs : ''}`)
}
export const createEvent = (d)     => api.post('/planner/events/', d)
export const updateEvent = (id, d) => api.patch(`/planner/events/${id}/`, d)
export const deleteEvent = (id)    => api.delete(`/planner/events/${id}/`)

export const getTaskLists   = ()      => api.getAll('/planner/task-lists/')
export const createTaskList = (d)     => api.post('/planner/task-lists/', d)
export const updateTaskList = (id, d) => api.patch(`/planner/task-lists/${id}/`, d)
export const deleteTaskList = (id)    => api.delete(`/planner/task-lists/${id}/`)

export const getTasks = (params = {}) => {
  const qs = new URLSearchParams(params).toString()
  return api.getAll(`/planner/tasks/${qs ? '?' + qs : ''}`)
}
export const createTask = (d)     => api.post('/planner/tasks/', d)
export const updateTask = (id, d) => api.patch(`/planner/tasks/${id}/`, d)
export const deleteTask = (id)    => api.delete(`/planner/tasks/${id}/`)

export const getVirtual = () => api.get('/planner/virtual/')
