const ENV_DEFAULTS = {
  VITE_API_BASE_URL: 'http://localhost:8000',
  VITE_API_TIMEOUT_MS: '30000',
} as const

type EnvKey = keyof typeof ENV_DEFAULTS

function isUnset(value: string | undefined): boolean {
  return value === undefined || String(value).trim() === ''
}

function getBakedEnv(name: EnvKey): string | undefined {
  const value = (import.meta.env as Record<string, string | undefined>)[name]
  return isUnset(value) ? undefined : String(value)
}

function resolveApiBaseUrl(): string {
  const baked = getBakedEnv('VITE_API_BASE_URL')
  if (baked !== undefined) {
    return baked.replace(/\/$/, '')
  }

  if (typeof window !== 'undefined') {
    return window.location.origin
  }

  return ENV_DEFAULTS.VITE_API_BASE_URL
}

function getEnvWithDefault(name: EnvKey): string {
  const baked = getBakedEnv(name)
  if (baked !== undefined) {
    return baked
  }

  return ENV_DEFAULTS[name]
}

function getPositiveNumberFromEnv(name: 'VITE_API_TIMEOUT_MS'): number {
  const raw = getEnvWithDefault(name)
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    throw new Error(`Environment variable ${name} must be a positive number. Received: ${raw}`)
  }

  return parsed
}

export const env = {
  apiBaseUrl: resolveApiBaseUrl(),
  apiTimeoutMs: getPositiveNumberFromEnv('VITE_API_TIMEOUT_MS'),
}
