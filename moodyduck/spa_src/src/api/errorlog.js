import { apiClient } from './client'

export async function getErrorLogs(resolved = null) {
  const params = {}
  if (resolved !== null) params.resolved = resolved ? 'true' : 'false'
  const res = await apiClient.get('/error-logs/', { params })
  return res.data
}

export async function patchErrorLog(id, data) {
  const res = await apiClient.patch(`/error-logs/${id}/`, data)
  return res.data
}
