const BASE = '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) throw new Error(await errorMessage(res))
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

/**
 * The message worth showing a user, or the status line if there isn't one.
 *
 * The backend renders a rejected order line as `{"detail": "<a sentence written
 * to be read>"}`. FastAPI's own request validation puts a list of objects under
 * the same key, so only a string is safe to surface verbatim.
 */
async function errorMessage(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
  } catch {
    // No JSON body. Fall through to the status line.
  }
  return `HTTP ${res.status}: ${res.statusText}`
}

export function get<T>(path: string): Promise<T> {
  return request<T>(path)
}

export function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export function del<T>(path: string): Promise<T> {
  return request<T>(path, { method: 'DELETE' })
}
