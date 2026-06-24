import { Stack } from '@mui/material'
import { useEffect, useRef } from 'react'
import { GhostScrollBox } from '../ui/GhostScrollBox'
import { ChatMessage } from './ChatMessage'
import type { ChatMessage as ChatMessageType } from '../../types'
import { chat } from '../../theme/tokens'

interface ChatThreadProps {
  messages: ChatMessageType[]
  bottomPadding?: number
  pendingAssistantMessage?: {
    executionId: string
    content: string
  } | null
}

export function ChatThread({
  messages,
  bottomPadding = 0,
  pendingAssistantMessage = null,
}: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const showPendingAssistant =
    pendingAssistantMessage &&
    !messages.some(
      (message) =>
        message.execution_id === pendingAssistantMessage.executionId &&
        message.role === 'assistant',
    )

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, pendingAssistantMessage])

  return (
    <GhostScrollBox
      sx={{
        position: 'absolute',
        inset: 0,
        overflow: 'auto',
        px: { xs: 2, sm: 3 },
        py: { xs: 2.5, sm: 3 },
      }}
    >
      <Stack
        spacing={0}
        sx={{
          maxWidth: chat.threadMaxWidth,
          mx: 'auto',
          width: '100%',
          pb: `${bottomPadding}px`,
        }}
      >
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {showPendingAssistant ? (
          <ChatMessage
            key={`pending-${pendingAssistantMessage.executionId}`}
            message={{
              id: `pending-${pendingAssistantMessage.executionId}`,
              role: 'assistant',
              content: pendingAssistantMessage.content,
              created_at: new Date().toISOString(),
              execution_id: pendingAssistantMessage.executionId,
            }}
          />
        ) : null}
      </Stack>
      <div ref={bottomRef} />
    </GhostScrollBox>
  )
}
