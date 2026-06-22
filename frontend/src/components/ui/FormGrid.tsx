import type { PropsWithChildren } from 'react'
import { Grid } from '@mui/material'
import { formSpacing } from '../../theme/tokens'

export function FormGrid({ children }: PropsWithChildren) {
  return (
    <Grid container spacing={formSpacing.grid}>
      {children}
    </Grid>
  )
}

interface FormGridItemProps extends PropsWithChildren {
  xs?: number
  md?: number
}

export function FormGridItem({ children, xs = 12, md = 6 }: FormGridItemProps) {
  return (
    <Grid size={{ xs, md }}>
      {children}
    </Grid>
  )
}
