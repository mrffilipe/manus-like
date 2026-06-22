import { useCallback, useEffect, useRef, useState } from 'react'
import { env } from '../config'
import { getExecutionActivity } from '../services'
import { apiPaths } from '../services/httpPaths'
import type { ActivityEvent, ExecutionStatus } from '../types'

interface SsePayload {
  event?: string
  activity?: ActivityEvent
  error?: string
}

interface UseExecutionActivityOptions {
  enabled?: boolean
  terminalStatuses?: Set<ExecutionStatus>
}

const DEFAULT_TERMINAL_STATUSES = new Set<ExecutionStatus>(['Completed', 'Failed'])
const POLL_INTERVAL_MS = 3000
const LIVE_DEBOUNCE_MS = 2500

function mergeActivities(current: ActivityEvent[], incoming: ActivityEvent[]): ActivityEvent[] {
  const map = new Map(current.map((item) => [item.id, item]))
  for (const item of incoming) {
    map.set(item.id, item)
  }
  return Array.from(map.values()).sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  )
}

export function useExecutionActivity(
  executionId: string,
  status: ExecutionStatus | null,
  options: UseExecutionActivityOptions = {},
) {
  const terminalStatuses = options.terminalStatuses ?? DEFAULT_TERMINAL_STATUSES
  const enabled = options.enabled ?? Boolean(executionId)
  const [activities, setActivities] = useState<ActivityEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [live, setLive] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const lastIdRef = useRef<string | null>(null)
  const reconnectAttemptRef = useRef(0)
  const liveDebounceRef = useRef<number | undefined>(undefined)
  const terminalStatusesRef = useRef(terminalStatuses)
  terminalStatusesRef.current = terminalStatuses

  const appendActivities = useCallback((incoming: ActivityEvent[]) => {
    if (incoming.length === 0) {
      return
    }
    setActivities((current) => {
      const merged = mergeActivities(current, incoming)
      lastIdRef.current = merged[merged.length - 1]?.id ?? lastIdRef.current
      return merged
    })
    setLive(true)
    if (liveDebounceRef.current !== undefined) {
      window.clearTimeout(liveDebounceRef.current)
      liveDebounceRef.current = undefined
    }
  }, [])

  const appendActivitiesRef = useRef(appendActivities)
  appendActivitiesRef.current = appendActivities

  const pollActivities = useCallback(async () => {
    if (!executionId) {
      return
    }
    try {
      const response = await getExecutionActivity(
        executionId,
        lastIdRef.current ?? undefined,
      )
      appendActivitiesRef.current(response.activities)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load activity')
    }
  }, [executionId])

  useEffect(() => {
    if (!enabled || !executionId) {
      return
    }

    let cancelled = false

    async function loadHistory() {
      try {
        const response = await getExecutionActivity(executionId)
        if (!cancelled) {
          appendActivitiesRef.current(response.activities)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load activity')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadHistory()

    return () => {
      cancelled = true
    }
  }, [enabled, executionId])

  const isTerminal = Boolean(status && terminalStatuses.has(status))

  useEffect(() => {
    if (!enabled || !executionId || isTerminal) {
      setLive(false)
      return
    }

    let eventSource: EventSource | null = null
    let reconnectTimer: number | undefined
    let pollTimer: number | undefined
    let cancelled = false

    function markOfflineDebounced() {
      if (liveDebounceRef.current !== undefined) {
        window.clearTimeout(liveDebounceRef.current)
      }
      liveDebounceRef.current = window.setTimeout(() => {
        if (!cancelled) {
          setLive(false)
        }
      }, LIVE_DEBOUNCE_MS)
    }

    function connect() {
      eventSource?.close()
      const url = `${env.apiBaseUrl}${apiPaths.agentEvents(executionId)}`
      eventSource = new EventSource(url)

      eventSource.onopen = () => {
        if (cancelled) {
          return
        }
        reconnectAttemptRef.current = 0
        setLive(true)
        if (liveDebounceRef.current !== undefined) {
          window.clearTimeout(liveDebounceRef.current)
          liveDebounceRef.current = undefined
        }
      }

      eventSource.onmessage = (event) => {
        if (cancelled) {
          return
        }
        try {
          const payload = JSON.parse(event.data) as SsePayload
          if (payload.event === 'activity' && payload.activity) {
            appendActivitiesRef.current([payload.activity])
          } else if (
            payload.event &&
            ['completed', 'failed', 'waiting_human_input'].includes(payload.event)
          ) {
            eventSource?.close()
          }
        } catch {
          // ignore heartbeat / malformed payloads
        }
      }

      eventSource.onerror = () => {
        if (cancelled) {
          return
        }
        markOfflineDebounced()
        eventSource?.close()
        reconnectAttemptRef.current += 1
        const delay = Math.min(1000 * 2 ** Math.min(reconnectAttemptRef.current, 4), 15000)
        reconnectTimer = window.setTimeout(() => {
          if (!cancelled) {
            connect()
          }
        }, delay)
      }
    }

    connect()
    pollTimer = window.setInterval(() => {
      void pollActivities()
    }, POLL_INTERVAL_MS)

    return () => {
      cancelled = true
      if (reconnectTimer !== undefined) {
        window.clearTimeout(reconnectTimer)
      }
      if (pollTimer !== undefined) {
        window.clearInterval(pollTimer)
      }
      if (liveDebounceRef.current !== undefined) {
        window.clearTimeout(liveDebounceRef.current)
      }
      eventSource?.close()
    }
  }, [enabled, executionId, isTerminal, pollActivities])

  return {
    activities,
    loading,
    connected: live,
    error,
  }
}
