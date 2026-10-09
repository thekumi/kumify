import { api } from './client.js'

export const getModules       = ()              => api.get('/modules/')
export const setModuleVisible = (slug, visible) => api.patch(`/modules/${slug}/preference/`, { visible })
export const getNavOrder      = ()              => api.get('/nav-order/')
export const setNavOrder      = (order)         => api.put('/nav-order/', order)

export const adminGetModules  = ()              => api.get('/admin/modules/')
export const adminPatchModule = (slug, data)    => api.patch(`/admin/modules/${slug}/`, data)
