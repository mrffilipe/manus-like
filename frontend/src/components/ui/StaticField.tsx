import { Box, Typography } from '@mui/material'
import type { ReactNode } from 'react'

export interface StaticFieldProps {
  label: string
  value: ReactNode
  monospace?: boolean
}

export function StaticField({ label, value, monospace = false }: StaticFieldProps) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
        {label}
      </Typography>
      <Typography
        variant="body2"
        sx={monospace ? { fontFamily: 'monospace', fontSize: '0.8125rem', wordBreak: 'break-all' } : undefined}
      >
        {value || '—'}
      </Typography>
    </Box>
  )
}
