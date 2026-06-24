import { api } from '../config'
import { apiPaths } from './httpPaths'
import type { AgentSettings, UpdateAgentSettingsPayload } from '../types'

export async function getSettings(): Promise<AgentSettings> {
  const response = await api.get<AgentSettings>(apiPaths.settings)
  return response.data
}

export async function updateSettings(payload: UpdateAgentSettingsPayload): Promise<AgentSettings> {
  const response = await api.patch<AgentSettings>(apiPaths.settings, payload)
  return response.data
}

export async function resetSettings(): Promise<AgentSettings> {
  const response = await api.post<AgentSettings>(apiPaths.settingsReset)
  return response.data
}
