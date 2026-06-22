import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward'
import { Box, IconButton, InputBase } from '@mui/material'
import { useState } from 'react'
import { floatingSurfaceSx } from '../../theme/chatStyles'

interface ChatComposerProps {
  onSend: (text: string) => Promise<void>
  disabled?: boolean
  placeholder?: string
}

export function ChatComposer({
  onSend,
  disabled = false,
  placeholder = 'Envie uma mensagem…',
}: ChatComposerProps) {
  const [text, setText] = useState('')
  const [sending, setSending] = useState(false)
  const [focused, setFocused] = useState(false)

  async function handleSubmit() {
    const trimmed = text.trim()
    if (!trimmed || disabled || sending) {
      return
    }

    setSending(true)
    try {
      await onSend(trimmed)
      setText('')
    } finally {
      setSending(false)
    }
  }

  function handleKeyDown(event: React.KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void handleSubmit()
    }
  }

  const canSend = !disabled && !sending && text.trim().length > 0

  return (
    <Box
      sx={{
        pt: 2,
        pb: { xs: 2.5, sm: 3 },
        pointerEvents: 'auto',
      }}
    >
      <Box
        sx={[
          {
            display: 'flex',
            alignItems: 'flex-end',
            gap: 1,
            px: 2,
            py: 1.25,
          },
          floatingSurfaceSx(focused),
        ]}
      >
        <InputBase
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={placeholder}
          multiline
          maxRows={6}
          fullWidth
          disabled={disabled || sending}
          sx={{
            fontSize: '0.9375rem',
            lineHeight: 1.5,
            '& .MuiInputBase-input': {
              py: 0.5,
              '&::placeholder': {
                color: 'text.disabled',
                opacity: 1,
              },
            },
          }}
        />
        <IconButton
          onClick={() => void handleSubmit()}
          disabled={!canSend}
          size="small"
          sx={{
            width: 36,
            height: 36,
            flexShrink: 0,
            bgcolor: canSend ? 'primary.main' : 'action.disabledBackground',
            color: canSend ? 'primary.contrastText' : 'text.disabled',
            transition: 'background-color 0.15s ease, transform 0.15s ease',
            '&:hover': {
              bgcolor: canSend ? 'primary.dark' : 'action.disabledBackground',
            },
            '&:active': {
              transform: canSend ? 'scale(0.94)' : 'none',
            },
            '&.Mui-disabled': {
              bgcolor: 'action.disabledBackground',
              color: 'text.disabled',
            },
          }}
        >
          <ArrowUpwardIcon sx={{ fontSize: 18 }} />
        </IconButton>
      </Box>
    </Box>
  )
}
