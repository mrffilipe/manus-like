import AttachFileIcon from '@mui/icons-material/AttachFile'
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward'
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import { Box, Chip, IconButton, InputBase } from '@mui/material'
import { useRef, useState } from 'react'
import { GhostScrollBox } from '../ui/GhostScrollBox'
import { ACCEPTED_FILE_TYPES } from '../../constants/acceptedFiles'
import { floatingSurfaceSx } from '../../theme/chatStyles'
import { FileAttachmentPreview } from './FileAttachmentPreview'

interface ChatComposerProps {
  onSend: (text: string, files?: File[]) => Promise<void>
  disabled?: boolean
  placeholder?: string
  lockedClientName?: string | null
}

export function ChatComposer({
  onSend,
  disabled = false,
  placeholder = 'Envie uma mensagem…',
  lockedClientName = null,
}: ChatComposerProps) {
  const [text, setText] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [sending, setSending] = useState(false)
  const [focused, setFocused] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleSubmit() {
    const trimmed = text.trim()
    if ((!trimmed && files.length === 0) || disabled || sending) {
      return
    }

    setSending(true)
    try {
      await onSend(trimmed || 'Analise os arquivos anexados.', files)
      setText('')
      setFiles([])
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

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files ? Array.from(event.target.files) : []
    if (selected.length > 0) {
      setFiles((current) => [...current, ...selected])
    }
    event.target.value = ''
  }

  function removeFile(index: number) {
    setFiles((current) => current.filter((_, fileIndex) => fileIndex !== index))
  }

  const canSend = !disabled && !sending && (text.trim().length > 0 || files.length > 0)

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
            flexDirection: 'column',
            gap: 1,
            px: 2,
            py: 1.25,
          },
          floatingSurfaceSx(focused),
        ]}
      >
        {lockedClientName ? (
          <Box sx={{ py: 0.5, px: 0.5 }}>
            <Chip
              icon={<BusinessOutlinedIcon />}
              label={lockedClientName}
              size="small"
              variant="outlined"
              sx={{ fontWeight: 500, maxWidth: '100%', px: 0.5 }}
            />
          </Box>
        ) : null}

        {files.length > 0 ? (
          <GhostScrollBox
            sx={{
              display: 'flex',
              flexDirection: 'row',
              gap: 1,
              overflowX: 'auto',
              overflowY: 'hidden',
              flexWrap: 'nowrap',
              maxWidth: '100%',
              pb: 0.5,
            }}
          >
            {files.map((file, index) => (
              <FileAttachmentPreview
                key={`${file.name}-${index}`}
                file={file}
                onRemove={() => removeFile(index)}
              />
            ))}
          </GhostScrollBox>
        ) : null}

        <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
          <input
            ref={fileInputRef}
            type="file"
            hidden
            multiple
            accept={ACCEPTED_FILE_TYPES}
            onChange={handleFileChange}
          />
          <IconButton
            size="small"
            disabled={disabled || sending}
            onClick={() => fileInputRef.current?.click()}
            sx={{ flexShrink: 0, mb: 0.25 }}
            aria-label="Anexar arquivo"
          >
            <AttachFileIcon sx={{ fontSize: 20 }} />
          </IconButton>
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
    </Box>
  )
}
