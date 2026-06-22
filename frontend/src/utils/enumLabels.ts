import type { ExecutionStatus } from '../types'

export function executionStatusLabel(status: ExecutionStatus): string {
  const labels: Record<ExecutionStatus, string> = {
    Running: 'Running',
    WaitingHumanInput: 'Waiting for input',
    Completed: 'Completed',
    Failed: 'Failed',
  }
  return labels[status]
}

export function executionStatusVariant(status: ExecutionStatus): 'default' | 'success' | 'warning' | 'error' | 'info' | 'primary' {
  switch (status) {
    case 'Running':
      return 'info'
    case 'WaitingHumanInput':
      return 'warning'
    case 'Completed':
      return 'success'
    case 'Failed':
      return 'error'
    default:
      return 'default'
  }
}

export function executionStepLabel(step: string | null | undefined): string {
  if (!step) {
    return '—'
  }
  return step.replace(/_/g, ' ')
}
