export type ExecutionStatus = 'Running' | 'WaitingHumanInput' | 'Completed' | 'Failed'

export interface RunAgentRequest {
  goal: string
  user_id?: string
  conversation_id?: string
}

export interface RunAgentResponse {
  execution_id: string
  status: ExecutionStatus
}

export interface ContinueAgentRequest {
  answer: string
}

export interface AgentStatusResponse {
  execution_id: string
  status: ExecutionStatus
  current_step: string | null
  goal: string
  question: string | null
  options: string[] | null
  error_message: string | null
  result: string | null
}

export interface StoredExecution {
  execution_id: string
  goal: string
  status: ExecutionStatus
  created_at: string
}
