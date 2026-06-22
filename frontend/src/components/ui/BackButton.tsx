import { Button, type ButtonProps } from '@mui/material'

export function BackButton({ children, sx, size = 'large', ...props }: ButtonProps) {
  return (
    <Button
      type="button"
      variant="text"
      color="inherit"
      size={size}
      disableElevation
      sx={[
        {
          color: 'text.secondary',
          minWidth: 'unset',
          px: 1.5,
          border: 'none',
          '&:hover': {
            border: 'none',
            backgroundColor: 'action.hover',
          },
        },
        ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
      ]}
      {...props}
    >
      {children}
    </Button>
  )
}
