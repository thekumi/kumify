import { api } from './client'
import { b64encode } from '@/keystore/util'

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

export async function uploadAttachment(statusId, file, dataKey, isPrivate = false) {
  const fileBytes = await file.arrayBuffer()
  const fileIv = crypto.getRandomValues(new Uint8Array(12))
  const encryptedFile = await crypto.subtle.encrypt({ name: 'AES-GCM', iv: fileIv }, dataKey, fileBytes)

  const metaBytes = new TextEncoder().encode(JSON.stringify({ mime: file.type || 'application/octet-stream', private: isPrivate, name: file.name }))
  const metaIv = crypto.getRandomValues(new Uint8Array(12))
  const encryptedMeta = await crypto.subtle.encrypt({ name: 'AES-GCM', iv: metaIv }, dataKey, metaBytes)

  const ep = { v: 2, iv: b64encode(fileIv), meta_iv: b64encode(metaIv), meta_ct: b64encode(encryptedMeta) }

  const token = localStorage.getItem('authToken')
  const form = new FormData()
  form.append('file', new Blob([encryptedFile], { type: 'application/octet-stream' }), file.name)
  form.append('encrypted_payload', JSON.stringify(ep))
  const res = await fetch(`/api/statuses/${statusId}/attachments/`, {
    method: 'POST',
    headers: token ? { Authorization: `Token ${token}` } : {},
    body: form,
  })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export const deleteAttachment = (statusId, attachmentId) =>
  api.delete(`/statuses/${statusId}/attachments/${attachmentId}/`)
