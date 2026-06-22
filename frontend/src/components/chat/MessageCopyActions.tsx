import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import TextFieldsIcon from '@mui/icons-material/TextFields'
import { Box, IconButton, Tooltip } from '@mui/material'
import { useState } from 'react'
import { copyToClipboard, markdownToPlainText } from '../../utils/clipboard'

interface MessageCopyActionsProps {
  content: string
  align?: 'left' | 'right'
}

export function MessageCopyActions({ content, align = 'left' }: MessageCopyActionsProps) {
  const [copied, setCopied] = useState<'markdown' | 'plain' | null>(null)

  async function handleCopy(mode: 'markdown' | 'plain') {
    const text = mode === 'markdown' ? content : markdownToPlainText(content)
    await copyToClipboard(text)
    setCopied(mode)
    window.setTimeout(() => setCopied(null), 1600)
  }

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 0.25,
        justifyContent: align === 'right' ? 'flex-end' : 'flex-start',
        mt: 0.5,
        opacity: 0.55,
        transition: 'opacity 0.15s ease',
        '.message-block:hover &': { opacity: 1 },
      }}
    >
      <Tooltip title={copied === 'markdown' ? 'Copiado!' : 'Copiar markdown'}>
        <IconButton size="small" onClick={() => void handleCopy('markdown')} sx={{ p: 0.5 }}>
          <ContentCopyIcon sx={{ fontSize: 14 }} />
        </IconButton>
      </Tooltip>
      <Tooltip title={copied === 'plain' ? 'Copiado!' : 'Copiar texto puro'}>
        <IconButton size="small" onClick={() => void handleCopy('plain')} sx={{ p: 0.5 }}>
          <TextFieldsIcon sx={{ fontSize: 14 }} />
        </IconButton>
      </Tooltip>
    </Box>
  )
}
