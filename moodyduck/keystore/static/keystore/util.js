export function b64encode(buffer) {
  const bytes = new Uint8Array(buffer);
  let str = "";
  for (const b of bytes) str += String.fromCharCode(b);
  return btoa(str);
}

export function b64decode(str) {
  const bin = atob(str);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return buf.buffer;
}

export function getCsrfToken() {
  return (
    document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith("csrftoken="))
      ?.split("=")[1] ?? ""
  );
}

export async function apiFetch(method, path, body = null) {
  const isFormData = body instanceof FormData;
  const opts = {
    method,
    headers: {
      "X-CSRFToken": getCsrfToken(),
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
    },
    credentials: "same-origin",
  };
  if (body !== null) opts.body = isFormData ? body : JSON.stringify(body);
  return fetch(path, opts);
}
