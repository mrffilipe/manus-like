import axios from 'axios'
import { env } from './env'
import { parseApiBody } from '../utils/apiResponse'

export const api = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: env.apiTimeoutMs,
  headers: {
    Accept: 'application/json',
  },
  maxRedirects: 0,
})

api.interceptors.response.use(
  (response) => {
    if (typeof response.data === 'string') {
      const trimmed = response.data.trim()
      if (trimmed.startsWith('<!DOCTYPE') || trimmed.startsWith('<html')) {
        return Promise.reject(new Error('The API returned an HTML response instead of JSON.'))
      }
    }

    response.data = parseApiBody(response.data)
    return response
  },
  (error) => Promise.reject(error),
)
