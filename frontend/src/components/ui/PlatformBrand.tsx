import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import { Box, Typography, type SxProps, type Theme } from '@mui/material'
import { Link } from 'react-router'

interface PlatformBrandProps {
  logoSize?: number
  to?: string
  sx?: SxProps<Theme>
}

export function PlatformBrand({ logoSize = 32, to = '/', sx }: PlatformBrandProps) {
  const inner = (
    <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
      <Box
        sx={{
          width: logoSize,
          height: logoSize,
          borderRadius: '50%',
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        <SmartToyOutlinedIcon sx={{ fontSize: logoSize * 0.55 }} />
      </Box>
      <Typography variant="subtitle1" sx={{ fontWeight: 600, letterSpacing: '-0.02em' }}>
        Agent
      </Typography>
    </Box>
  )

  const boxSx = [
    {
      display: 'inline-flex',
      alignItems: 'center',
      textDecoration: 'none',
      color: 'inherit',
    },
    ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
  ] as const

  if (to) {
    return (
      <Box component={Link} to={to} sx={boxSx}>
        {inner}
      </Box>
    )
  }

  return <Box sx={boxSx}>{inner}</Box>
}
