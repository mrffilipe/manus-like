import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router'
import { continueExecution, getExecutionStatus, runAgent, runAgentWithFiles } from '../services'
import { getConversationMessages } from '../services/conversationService'
import type { AgentStatusResponse, ChatMessage, ExecutionStatus } from '../types'
import { getApiErrorMessage } from '../utils/apiError'

const TERMINAL_STATUSES = new Set<ExecutionStatus>(['Completed', 'Failed'])
const ACTIVE_STATUSES = new Set<ExecutionStatus>(['Running', 'WaitingHumanInput'])

interface UseChatOptions {
  conversationId?: string
  clientId?: string | null
  onConversationCreated?: (conversationId: string) => void
  onMessagesUpdated?: () => void
}

function findLatestExecutionId(messages: ChatMessage[]): string | null {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index].execution_id) {
      return messages[index].execution_id
    }
  }
  return null
}

function hasAssistantMessageForExecution(messages: ChatMessage[], executionId: string): boolean {
  return messages.some(
    (message) => message.execution_id === executionId && message.role === 'assistant',
  )
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

export function useChat({
  conversationId,
  clientId,
  onConversationCreated,
  onMessagesUpdated,
}: UseChatOptions) {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [conversationClientId, setConversationClientId] = useState<string | null>(null)
  const [loading, setLoading] = useState(Boolean(conversationId))
  const [error, setError] = useState<string | null>(null)
  const [activeExecutionId, setActiveExecutionId] = useState<string | null>(null)
  const [executionStatus, setExecutionStatus] = useState<AgentStatusResponse | null>(null)
  const [sending, setSending] = useState(false)
  const activeExecutionRef = useRef<string | null>(null)

  const loadMessages = useCallback(async (silent = false): Promise<ChatMessage[]> => {
    if (!conversationId) {
      setMessages([])
      setConversationClientId(null)
      setLoading(false)
      return []
    }

    if (!silent) {
      setLoading(true)
    }
    try {
      const response = await getConversationMessages(conversationId)
      setMessages(response.messages)
      setConversationClientId(response.client_id)
      setError(null)

      const latestExecutionId = findLatestExecutionId(response.messages)
      if (latestExecutionId) {
        const status = await getExecutionStatus(latestExecutionId)
        if (ACTIVE_STATUSES.has(status.status)) {
          setActiveExecutionId(latestExecutionId)
          setExecutionStatus(status)
        } else {
          setActiveExecutionId(null)
          setExecutionStatus(null)
        }
      } else {
        setActiveExecutionId(null)
        setExecutionStatus(null)
      }

      return response.messages
    } catch (err) {
      setError(getApiErrorMessage(err))
      return []
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }, [conversationId])

  useEffect(() => {
    void loadMessages()
  }, [loadMessages])

  useEffect(() => {
    activeExecutionRef.current = activeExecutionId
  }, [activeExecutionId])

  useEffect(() => {
    if (!activeExecutionId) {
      return
    }

    let cancelled = false
    let intervalId: number | undefined

    async function pollStatus() {
      const executionId = activeExecutionId
      if (!executionId) {
        return
      }

      try {
        const status = await getExecutionStatus(executionId)
        if (cancelled) {
          return
        }

        setExecutionStatus(status)

        if (TERMINAL_STATUSES.has(status.status)) {
          let loadedMessages = await loadMessages(true)

          if (status.status === 'Completed') {
            for (let attempt = 0; attempt < 5; attempt += 1) {
              if (hasAssistantMessageForExecution(loadedMessages, executionId)) {
                break
              }
              await sleep(500)
              loadedMessages = await loadMessages(true)
            }
          }

          onMessagesUpdated?.()

          const hasAssistant = hasAssistantMessageForExecution(loadedMessages, executionId)
          if (status.status === 'Failed' || hasAssistant) {
            setActiveExecutionId(null)
            setExecutionStatus(null)
          } else if (status.status === 'Completed') {
            setActiveExecutionId(null)
          }

          if (intervalId !== undefined) {
            window.clearInterval(intervalId)
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(getApiErrorMessage(err))
        }
      }
    }

    void pollStatus()
    intervalId = window.setInterval(() => {
      void pollStatus()
    }, 2000)

    return () => {
      cancelled = true
      if (intervalId !== undefined) {
        window.clearInterval(intervalId)
      }
    }
  }, [activeExecutionId, loadMessages, onMessagesUpdated])

  const sendMessage = useCallback(
    async (text: string, files: File[] = []) => {
      setSending(true)
      setError(null)

      try {
        const response =
          files.length > 0
            ? await runAgentWithFiles(text, files, {
                conversation_id: conversationId,
                client_id: clientId ?? undefined,
                agent_mode: clientId ? 'marketing_consultant' : undefined,
              })
            : await runAgent({
                goal: text,
                conversation_id: conversationId,
                client_id: clientId ?? undefined,
                agent_mode: clientId ? 'marketing_consultant' : undefined,
              })

        setActiveExecutionId(response.execution_id)
        activeExecutionRef.current = response.execution_id
        onConversationCreated?.(response.conversation_id)
        onMessagesUpdated?.()

        if (!conversationId) {
          navigate(`/c/${response.conversation_id}`, { replace: true })
        } else {
          await loadMessages(true)
        }

        const status = await getExecutionStatus(response.execution_id)
        setExecutionStatus(status)
      } catch (err) {
        setError(getApiErrorMessage(err))
        throw err
      } finally {
        setSending(false)
      }
    },
    [clientId, conversationId, loadMessages, navigate, onConversationCreated, onMessagesUpdated],
  )

  const continueWithAnswer = useCallback(
    async (answer: string) => {
      if (!activeExecutionId) {
        return
      }

      setSending(true)
      setError(null)

      try {
        await continueExecution(activeExecutionId, answer)
        setExecutionStatus((current) =>
          current ? { ...current, status: 'Running', question: null, options: null } : current,
        )
        await loadMessages()
        onMessagesUpdated?.()
      } catch (err) {
        setError(getApiErrorMessage(err))
        throw err
      } finally {
        setSending(false)
      }
    },
    [activeExecutionId, loadMessages, onMessagesUpdated],
  )

  const isRunning = executionStatus?.status === 'Running'
  const isWaitingHumanInput = executionStatus?.status === 'WaitingHumanInput'
  const composerDisabled = sending || isRunning

  return {
    messages,
    conversationClientId,
    loading,
    error,
    sending,
    activeExecutionId,
    executionStatus,
    isRunning,
    isWaitingHumanInput,
    composerDisabled,
    sendMessage,
    continueWithAnswer,
    reloadMessages: loadMessages,
    setError,
  }
}
