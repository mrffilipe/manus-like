import type { PropsWithChildren } from 'react'
import { Divider, Stack, Typography } from '@mui/material'
import { formSpacing } from '../../theme/tokens'

interface FormSectionProps extends PropsWithChildren {
  title: string
  description?: string
  /** Exibe um divisor acima da seção (útil a partir da segunda seção em modais). */
  dividerBefore?: boolean
}

export function FormSection({ title, description, dividerBefore = false, children }: FormSectionProps) {
  return (
    <Stack spacing={formSpacing.section}>
      {dividerBefore ? <Divider sx={{ mb: 0.5 }} /> : null}
      <Stack spacing={0.25}>
        <Typography variant="subtitle2" component="h3" sx={{ fontWeight: 600, letterSpacing: '0.01em' }}>
          {title}
        </Typography>
        {description ? (
          <Typography variant="caption" color="text.secondary" sx={{ lineHeight: 1.45 }}>
            {description}
          </Typography>
        ) : null}
      </Stack>
      {children}
    </Stack>
  )
}
