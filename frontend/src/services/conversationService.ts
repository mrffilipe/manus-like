import { api } from '../config'
import type { ConversationListResponse, ConversationMessagesResponse } from '../types'
import { apiPaths } from './httpPaths'

export async function listConversations(): Promise<ConversationListResponse> {
  const response = await api.get<ConversationListResponse>(apiPaths.conversations)
  return response.data
}

export async function getConversationMessages(conversationId: string): Promise<ConversationMessagesResponse> {
  const response = await api.get<ConversationMessagesResponse>(apiPaths.conversationMessages(conversationId))
  return response.data
}

export async function deleteConversation(conversationId: string): Promise<{ conversation_id: string; deleted: boolean }> {
  const response = await api.delete<{ conversation_id: string; deleted: boolean }>(
    apiPaths.conversationDelete(conversationId),
  )
  return response.data
}
