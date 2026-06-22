import type { ExecutionStatus, StoredExecution } from '../types'

const STORAGE_KEY = 'manus-recent-executions'
const MAX_ITEMS = 50

export function getStoredExecutions(): StoredExecution[] {
  if (typeof window === 'undefined') {
    return []
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      return []
    }
    const parsed = JSON.parse(raw) as StoredExecution[]
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveStoredExecution(execution: StoredExecution): void {
  const current = getStoredExecutions().filter((item) => item.execution_id !== execution.execution_id)
  const next = [execution, ...current].slice(0, MAX_ITEMS)
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}

export function updateStoredExecutionStatus(executionId: string, status: ExecutionStatus): void {
  const current = getStoredExecutions()
  const next = current.map((item) =>
    item.execution_id === executionId ? { ...item, status } : item,
  )
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
}

export function getStoredExecution(executionId: string): StoredExecution | undefined {
  return getStoredExecutions().find((item) => item.execution_id === executionId)
}
