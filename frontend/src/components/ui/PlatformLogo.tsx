import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import { Box, type SxProps, type Theme } from '@mui/material'

interface PlatformLogoProps {
  size?: number
  sx?: SxProps<Theme>
}

export function PlatformLogo({ size = 56, sx }: PlatformLogoProps) {
  return (
    <Box
      sx={[
        {
          width: size,
          height: size,
          borderRadius: '50%',
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        },
        ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
      ]}
    >
      <SmartToyOutlinedIcon sx={{ fontSize: size * 0.55 }} />
    </Box>
  )
}
