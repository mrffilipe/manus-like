export type ExecutionStatus = 'Running' | 'WaitingHumanInput' | 'Completed' | 'Failed'

export type AgentMode = 'general' | 'marketing_consultant'

export type ActivityKind = 'step_start' | 'step_done' | 'preview' | 'error'

export type ActivityPreviewType = 'text' | 'markdown' | 'search_results' | 'webpage' | 'screenshot'

export interface ActivityEvent {
  id: string
  execution_id: string
  step: string
  kind: ActivityKind
  title: string
  summary: string | null
  preview_type: ActivityPreviewType | null
  preview_data: Record<string, unknown> | null
  created_at: string
}

export interface ActivityListResponse {
  execution_id: string
  activities: ActivityEvent[]
}

export interface AttachmentInput {
  filename: string
  extracted_text: string
  content_type?: string
}

export interface RunAgentRequest {
  goal: string
  user_id?: string
  conversation_id?: string
  client_id?: string
  agent_mode?: AgentMode
  attachments?: AttachmentInput[]
}

export interface RunAgentResponse {
  execution_id: string
  conversation_id: string
  status: ExecutionStatus
}

export interface ContinueAgentRequest {
  answer: string
}

export interface AgentStatusResponse {
  execution_id: string
  conversation_id: string | null
  status: ExecutionStatus
  current_step: string | null
  goal: string
  client_id: string | null
  agent_mode: string | null
  question: string | null
  options: string[] | null
  error_message: string | null
  result: string | null
}

export interface ConversationSummary {
  id: string
  title: string | null
  client_id: string | null
  updated_at: string
  last_message_preview: string | null
}

export interface ConversationListResponse {
  conversations: ConversationSummary[]
}

export interface ChatMessage {
  id: string
  role: string
  content: string
  created_at: string
  execution_id: string | null
}

export interface ConversationMessagesResponse {
  conversation_id: string
  client_id: string | null
  messages: ChatMessage[]
}

export interface StoredExecution {
  execution_id: string
  goal: string
  status: ExecutionStatus
  created_at: string
}

export interface ClientSummary {
  id: string
  slug: string
  name: string
  product: string
  description: string
  resource_count: number
  is_active: boolean
}

export interface ClientListResponse {
  clients: ClientSummary[]
}

export interface ClientResource {
  id: string
  client_id: string
  resource_type: 'file' | 'link' | 'prompt' | 'text'
  category: string | null
  title: string
  content: string | null
  url: string | null
  extracted_text: string | null
  scraped_at: string | null
  metadata: Record<string, unknown> | null
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ClientDetail {
  id: string
  slug: string
  name: string
  product: string
  description: string
  profile: Record<string, unknown> | null
  is_active: boolean
  resources: ClientResource[]
  created_at: string
  updated_at: string
}

export interface CreateClientPayload {
  name: string
  product: string
  description?: string
  slug?: string
  profile?: Record<string, unknown>
}

export interface UpdateClientPayload {
  name?: string
  product?: string
  description?: string
  slug?: string
  profile?: Record<string, unknown>
  is_active?: boolean
}

export interface CreateResourcePayload {
  resource_type: 'link' | 'prompt' | 'text'
  title: string
  category?: string
  content?: string
  url?: string
  metadata?: Record<string, unknown>
}

export interface UpdateResourcePayload {
  title?: string
  category?: string
  content?: string
  url?: string
  metadata?: Record<string, unknown>
  sort_order?: number
}

export interface AgentSettings {
  marketing_system_prompt: string
}

export interface UpdateAgentSettingsPayload {
  marketing_system_prompt: string
}
