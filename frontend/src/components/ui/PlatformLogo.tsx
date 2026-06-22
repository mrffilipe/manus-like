import { Box, type SxProps, type Theme } from '@mui/material'
import { brandAssets } from '../../theme/brandAssets'

interface PlatformLogoProps {
  size?: number
  sx?: SxProps<Theme>
}

/** Kyvo logomark (K icon) from brand guidelines. */
export function PlatformLogo({ size = 56, sx }: PlatformLogoProps) {
  return (
    <Box
      component="img"
      src={brandAssets.icon}
      alt=""
      aria-hidden
      sx={[
        {
          width: size,
          height: size,
          objectFit: 'contain',
          display: 'block',
          flexShrink: 0,
        },
        ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
      ]}
    />
  )
}
