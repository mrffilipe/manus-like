import type { PropsWithChildren, ReactNode } from 'react'
import { Paper, Stack, Typography } from '@mui/material'

interface SectionCardProps extends PropsWithChildren {
  title?: string
  subtitle?: string
  actions?: ReactNode
}

export function SectionCard({ title, subtitle, actions, children }: SectionCardProps) {
  return (
    <Paper sx={{ p: { xs: 2, sm: 3 } }}>
      <Stack spacing={2.5}>
        {title || subtitle || actions ? (
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1}
            sx={{ alignItems: { sm: 'center' }, justifyContent: 'space-between' }}
          >
            <Stack spacing={0.5}>
              {title ? (
                <Typography variant="h6" component="h2">
                  {title}
                </Typography>
              ) : null}
              {subtitle ? (
                <Typography variant="body2" color="text.secondary">
                  {subtitle}
                </Typography>
              ) : null}
            </Stack>
            {actions ? <Stack direction="row" spacing={1}>{actions}</Stack> : null}
          </Stack>
        ) : null}
        {children}
      </Stack>
    </Paper>
  )
}
