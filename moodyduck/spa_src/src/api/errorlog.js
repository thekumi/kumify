import { api } from './client'

export async function getErrorLogs(resolved = null) {
  const qs = resolved !== null ? `?resolved=${resolved ? 'true' : 'false'}` : ''
  return api.getAll(`/error-logs/${qs}`)
}

export async function patchErrorLog(id, data) {
  return api.patch(`/error-logs/${id}/`, data)
}
