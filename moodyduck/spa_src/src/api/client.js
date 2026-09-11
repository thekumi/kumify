const BASE = '/api'

function getToken() {
  return localStorage.getItem('authToken')
}

function getHeaders(extra = {}) {
  const h = { 'Content-Type': 'application/json', ...extra }
  const tok = getToken()
  if (tok) h['Authorization'] = `Token ${tok}`
  return h
}

async function request(method, path, body, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: getHeaders(opts.headers),
    body: body != null ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401) {
    localStorage.removeItem('authToken')
    window.location.href = '/login'
    return
  }
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw Object.assign(new Error('API error'), { data, status: res.status })
  return data
}

export const api = {
  get:    (path)         => request('GET',    path),
  post:   (path, body)   => request('POST',   path, body),
  patch:  (path, body)   => request('PATCH',  path, body),
  put:    (path, body)   => request('PUT',    path, body),
  delete: (path)         => request('DELETE', path),

  async getAll(path) {
    const results = []
    let url = `${BASE}${path}`
    while (url) {
      const res = await fetch(url, { headers: getHeaders() })
      if (!res.ok) throw new Error('API error')
      const data = await res.json()
      if (Array.isArray(data)) { results.push(...data); break }
      results.push(...(data.results ?? []))
      url = data.next
    }
    return results
  },
}
