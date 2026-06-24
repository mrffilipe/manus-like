import { api } from '../config'
import type { RunAgentRequest, RunAgentResponse } from '../types'
import { apiPaths } from './httpPaths'

export async function runAgent(payload: RunAgentRequest): Promise<RunAgentResponse> {
  const response = await api.post<RunAgentResponse>(apiPaths.agentRun, payload)
  return response.data
}

export async function runAgentWithFiles(
  goal: string,
  files: File[],
  options?: {
    conversation_id?: string
    client_id?: string
    agent_mode?: string
    user_id?: string
  },
): Promise<RunAgentResponse> {
  const formData = new FormData()
  formData.append('goal', goal)
  if (options?.conversation_id) {
    formData.append('conversation_id', options.conversation_id)
  }
  if (options?.client_id) {
    formData.append('client_id', options.client_id)
  }
  if (options?.agent_mode) {
    formData.append('agent_mode', options.agent_mode)
  }
  if (options?.user_id) {
    formData.append('user_id', options.user_id)
  }
  for (const file of files) {
    formData.append('files', file)
  }

  const response = await api.post<RunAgentResponse>(apiPaths.agentRunUpload, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getExecutionStatus(executionId: string) {
  const response = await api.get(apiPaths.agentStatus(executionId))
  return response.data
}

export async function getExecutionActivity(executionId: string, since?: string) {
  const response = await api.get(apiPaths.agentActivity(executionId), {
    params: since ? { since } : undefined,
  })
  return response.data
}

export async function resumeExecution(executionId: string): Promise<RunAgentResponse> {
  const response = await api.post<RunAgentResponse>(apiPaths.agentResume(executionId))
  return response.data
}

export async function continueExecution(executionId: string, answer: string): Promise<RunAgentResponse> {
  const response = await api.post<RunAgentResponse>(apiPaths.agentContinue(executionId), { answer })
  return response.data
}

export async function exportExecutionPdf(executionId: string): Promise<Blob> {
  const response = await api.get(apiPaths.agentExportPdf(executionId), {
    responseType: 'blob',
  })
  return response.data
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await api.get<{ status: string }>(apiPaths.health)
  return response.data
}
