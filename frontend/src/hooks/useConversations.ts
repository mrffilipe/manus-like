import { useCallback, useEffect, useState } from 'react'
import { listConversations } from '../services/conversationService'
import type { ConversationSummary } from '../types'
import { getApiErrorMessage } from '../utils/apiError'

export function useConversations() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refetch = useCallback(async () => {
    try {
      const response = await listConversations()
      setConversations(response.conversations)
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refetch()
  }, [refetch])

  return {
    conversations,
    loading,
    error,
    refetch,
  }
}
