import { api } from './client'

export const getProfile          = ()  => api.get('/profile/')
export const updateProfile       = (d) => api.patch('/profile/', d)
export const getEmergencyProfile = ()  => api.get('/emergency-profile/')
export const updateEmergencyProfile = (d) => api.patch('/emergency-profile/', d)
export const getDevices    = ()  => api.getAll('/devices/')
export const deleteDevice  = (deviceId) => api.delete(`/devices/${deviceId}/`)
