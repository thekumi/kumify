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
