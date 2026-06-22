export const apiPaths = {
  health: '/health',
  agentRun: '/agent/run',
  agentStatus: (id: string) => `/agent/status/${id}`,
  agentActivity: (id: string) => `/agent/activity/${id}`,
  agentEvents: (id: string) => `/agent/events/${id}`,
  agentResume: (id: string) => `/agent/resume/${id}`,
  agentContinue: (id: string) => `/agent/continue/${id}`,
} as const
