import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import { Box, Typography } from '@mui/material'
import { MarkdownContent } from '../ui/MarkdownContent'
import { MessageCopyActions } from './MessageCopyActions'
import type { ChatMessage as ChatMessageType } from '../../types'
import { chat } from '../../theme/tokens'
import { userPillSx } from '../../theme/chatStyles'

interface ChatMessageProps {
  message: ChatMessageType
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <Box className="message-block" sx={{ mb: chat.messageGap }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
          <Typography variant="body1" sx={[userPillSx(), { whiteSpace: 'pre-wrap', fontSize: '0.9375rem' }]}>
            {message.content}
          </Typography>
          <MessageCopyActions content={message.content} align="right" />
        </Box>
      </Box>
    )
  }

  return (
    <Box className="message-block" sx={{ mb: 3.5, pl: { xs: 0, sm: 0.5 } }}>
      <Box sx={{ display: 'flex', gap: 1.5 }}>
        <Box
          sx={{
            width: 24,
            height: 24,
            borderRadius: '50%',
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            display: { xs: 'none', sm: 'flex' },
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            mt: 0.25,
            opacity: 0.9,
          }}
        >
          <SmartToyOutlinedIcon sx={{ fontSize: 14 }} />
        </Box>

        <Box sx={{ flex: 1, minWidth: 0, color: 'text.primary' }}>
          <MarkdownContent content={message.content} />
          <MessageCopyActions content={message.content} align="left" />
        </Box>
      </Box>
    </Box>
  )
}
