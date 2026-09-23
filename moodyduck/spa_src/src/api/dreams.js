import { api } from './client'
import { b64encode } from '@/keystore/util'

export const getDreams    = (page=1) => api.get(`/dreams/?page=${page}`)
export const getAllDreams  = ()       => api.getAll('/dreams/')
export const getDream     = (id)     => api.get(`/dreams/${id}/`)
export const createDream  = (d)      => api.post('/dreams/', d)
export const updateDream  = (id, d)  => api.patch(`/dreams/${id}/`, d)
export const deleteDream  = (id)     => api.delete(`/dreams/${id}/`)

export async function uploadDreamAttachment(dreamId, file, dataKey, isPrivate = false) {
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
  const res = await fetch(`/api/dreams/${dreamId}/attachments/`, {
    method: 'POST',
    headers: token ? { Authorization: `Token ${token}` } : {},
    body: form,
  })
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export const deleteDreamAttachment = (dreamId, attachmentId) =>
  api.delete(`/dreams/${dreamId}/attachments/${attachmentId}/`)

export const getThemes   = ()       => api.getAll('/dream-themes/')
export const createTheme = (d)      => api.post('/dream-themes/', d)
export const updateTheme = (id, d)  => api.patch(`/dream-themes/${id}/`, d)
export const deleteTheme = (id)     => api.delete(`/dream-themes/${id}/`)
