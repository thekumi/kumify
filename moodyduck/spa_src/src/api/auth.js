import { api } from './client'

export async function login(username, password) {
  const res = await fetch('/api/auth/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  const data = await res.json()
  if (!res.ok) throw Object.assign(new Error('Login failed'), { data })
  localStorage.setItem('authToken', data.token)
  return data
}

export function logout() {
  localStorage.removeItem('authToken')
}

export function isLoggedIn() {
  return !!localStorage.getItem('authToken')
}

export const getMe = () => api.get('/me/')

export async function getServerInfo() {
  const res = await fetch('/api/auth/server-info/')
  if (!res.ok) throw new Error('Could not fetch server info')
  return res.json()
}

export async function register(fields) {
  const res = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  })
  const data = await res.json()
  if (!res.ok) throw Object.assign(new Error('Registration failed'), { data })
  return data
}

export const changePassword = (currentPassword, newPassword) =>
  api.post('/auth/password/change/', {
    current_password: currentPassword,
    new_password: newPassword,
  })
