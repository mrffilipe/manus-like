import { Stack } from '@mui/material'
import { useEffect, useRef } from 'react'
import { GhostScrollBox } from '../ui/GhostScrollBox'
import { ChatMessage } from './ChatMessage'
import type { ChatMessage as ChatMessageType } from '../../types'
import { chat } from '../../theme/tokens'

interface ChatThreadProps {
  messages: ChatMessageType[]
  bottomPadding?: number
}

export function ChatThread({ messages, bottomPadding = 0 }: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, bottomPadding])

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
      </Stack>
      <div ref={bottomRef} />
    </GhostScrollBox>
  )
}
