import type { PropsWithChildren } from 'react'
import { Stack } from '@mui/material'
import { formSpacing } from '../../theme/tokens'

interface FormActionsProps extends PropsWithChildren {
  /** Alinha o grupo à direita do container (padrão). Use `false` só em ações isoladas centralizadas (ex.: etapa 1 do bootstrap). */
  alignEnd?: boolean
}

export function FormActions({ children, alignEnd = true }: FormActionsProps) {
  return (
    <Stack
      direction="row"
      spacing={formSpacing.grid}
      sx={{
        pt: formSpacing.actionsTop,
        width: '100%',
        alignItems: 'center',
        justifyContent: alignEnd ? 'flex-end' : 'center',
      }}
    >
      {children}
    </Stack>
  )
}
