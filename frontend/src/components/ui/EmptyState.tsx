import type { ReactNode } from 'react'
import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined'
import { Box, Typography, useTheme } from '@mui/material'

interface EmptyStateProps {
  title?: string
  description?: string
  icon?: ReactNode
}

export function EmptyState({
  title = 'Nenhum registro encontrado',
  description,
  icon,
}: EmptyStateProps) {
  const theme = useTheme()

  return (
    <Box
      sx={{
        py: 6,
        px: 2,
        textAlign: 'center',
        color: 'text.secondary',
      }}
    >
      <Box
        sx={{
          mb: 1.5,
          display: 'inline-flex',
          color: 'primary.main',
          opacity: theme.palette.mode === 'dark' ? 0.85 : 0.7,
          '& svg': { fontSize: 48 },
        }}
      >
        {icon ?? <InboxOutlinedIcon />}
      </Box>
      <Typography variant="subtitle1" color="text.primary" gutterBottom>
        {title}
      </Typography>
      {description ? (
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      ) : null}
    </Box>
  )
}
