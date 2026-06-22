import { api } from '../config'
import type { ActivityListResponse, AgentStatusResponse, RunAgentRequest, RunAgentResponse } from '../types'
import { apiPaths } from './httpPaths'

export async function runAgent(payload: RunAgentRequest): Promise<RunAgentResponse> {
  const response = await api.post<RunAgentResponse>(apiPaths.agentRun, payload)
  return response.data
}

export async function getExecutionStatus(executionId: string): Promise<AgentStatusResponse> {
  const response = await api.get<AgentStatusResponse>(apiPaths.agentStatus(executionId))
  return response.data
}

export async function getExecutionActivity(
  executionId: string,
  since?: string,
): Promise<ActivityListResponse> {
  const response = await api.get<ActivityListResponse>(apiPaths.agentActivity(executionId), {
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

export async function checkHealth(): Promise<{ status: string }> {
  const response = await api.get<{ status: string }>(apiPaths.health)
  return response.data
}
