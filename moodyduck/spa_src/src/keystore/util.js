export function b64encode(buffer) {
  const bytes = new Uint8Array(buffer)
  let str = ''
  for (const b of bytes) str += String.fromCharCode(b)
  return btoa(str)
}

export function b64decode(str) {
  const bin = atob(str)
  const buf = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
  return buf.buffer
}

export async function apiFetch(method, path, body = null) {
  const token = localStorage.getItem('authToken')
  const isFormData = body instanceof FormData
  const opts = {
    method,
    headers: {
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    },
  }
  if (body !== null) opts.body = isFormData ? body : JSON.stringify(body)
  return fetch(path, opts)
}
