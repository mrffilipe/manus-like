import type { ExecutionStatus } from '../types'

export function executionStatusLabel(status: ExecutionStatus): string {
  const labels: Record<ExecutionStatus, string> = {
    Running: 'Em execução',
    WaitingHumanInput: 'Aguardando entrada',
    Completed: 'Concluído',
    Failed: 'Falhou',
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
  const labels: Record<string, string> = {
    planner: 'Planejamento',
    research: 'Pesquisa',
    browser: 'Navegador',
    tool_execution: 'Ferramentas',
    memory: 'Memória',
    critic: 'Avaliação',
    human_input: 'Entrada humana',
    error: 'Erro',
  }
  return labels[step] ?? step.replace(/_/g, ' ')
}

export function activityStepLabel(step: string): string {
  return executionStepLabel(step)
}
