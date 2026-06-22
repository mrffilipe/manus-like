import { Box, Chip, keyframes } from '@mui/material'

const pulse = keyframes`
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
`

interface ExecutionStatusPillProps {
  connected?: boolean
  loading?: boolean
}

export function ExecutionStatusPill({ connected = false, loading = false }: ExecutionStatusPillProps) {
  const label = connected ? 'Agente trabalhando…' : loading ? 'Conectando…' : 'Sincronizando…'

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        pb: 1,
        maxWidth: 720,
        mx: 'auto',
        width: '100%',
        px: { xs: 2, sm: 3 },
      }}
    >
      <Chip
        size="small"
        label={
          <Box component="span" sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
            <Box
              component="span"
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                bgcolor: connected ? 'success.main' : 'text.disabled',
                animation: connected ? `${pulse} 1.5s ease-in-out infinite` : 'none',
              }}
            />
            {label}
          </Box>
        }
        sx={{
          height: 28,
          fontSize: '0.75rem',
          fontWeight: 500,
          bgcolor: 'action.hover',
          border: 'none',
          '& .MuiChip-label': { px: 1.5 },
        }}
      />
    </Box>
  )
}
