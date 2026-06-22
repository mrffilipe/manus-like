import { isAxiosError } from 'axios'
import type { ProblemDetails } from '../types'

export function getApiErrorMessage(error: unknown): string {
  if (isAxiosError<ProblemDetails | { detail?: string | Array<{ msg?: string }> }>(error)) {
    const data = error.response?.data
    if (typeof data?.detail === 'string') {
      return data.detail
    }
    if (Array.isArray(data?.detail)) {
      return data.detail.map((item) => item.msg).filter(Boolean).join(', ') || 'Request failed.'
    }
    if (data && 'title' in data && data.title) {
      return data.title
    }
    if (error.message) {
      return error.message
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred.'
}
