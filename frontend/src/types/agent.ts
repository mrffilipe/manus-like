export type ExecutionStatus = 'Running' | 'WaitingHumanInput' | 'Completed' | 'Failed'

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

export interface RunAgentRequest {
  goal: string
  user_id?: string
  conversation_id?: string
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
  question: string | null
  options: string[] | null
  error_message: string | null
  result: string | null
}

export interface ConversationSummary {
  id: string
  title: string | null
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
  messages: ChatMessage[]
}

export interface StoredExecution {
  execution_id: string
  goal: string
  status: ExecutionStatus
  created_at: string
}
