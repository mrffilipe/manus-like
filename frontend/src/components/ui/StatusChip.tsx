import { Chip, type ChipProps } from '@mui/material'

type StatusVariant = 'default' | 'success' | 'warning' | 'error' | 'info' | 'primary'

interface StatusChipProps {
  label: string
  variant?: StatusVariant
  size?: ChipProps['size']
}

const colorMap: Record<StatusVariant, ChipProps['color']> = {
  default: 'default',
  success: 'success',
  warning: 'warning',
  error: 'error',
  info: 'info',
  primary: 'primary',
}

export function StatusChip({ label, variant = 'default', size = 'small' }: StatusChipProps) {
  return <Chip label={label} size={size} color={colorMap[variant]} variant="outlined" />
}
