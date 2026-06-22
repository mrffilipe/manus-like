export function parseApiBody<T = unknown>(data: unknown): T {
  if (typeof data !== 'string') {
    return data as T
  }

  const trimmed = data.trim()
  if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) {
    return data as T
  }

  try {
    return JSON.parse(trimmed) as T
  } catch {
    return data as T
  }
}
