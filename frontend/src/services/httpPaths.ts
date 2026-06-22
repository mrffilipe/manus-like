export const apiPaths = {
  health: '/health',
  agentRun: '/agent/run',
  agentStatus: (id: string) => `/agent/status/${id}`,
  agentResume: (id: string) => `/agent/resume/${id}`,
  agentContinue: (id: string) => `/agent/continue/${id}`,
} as const
