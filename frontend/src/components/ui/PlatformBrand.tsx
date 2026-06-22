import { Box, type SxProps, type Theme } from '@mui/material'
import { Link } from 'react-router'
import { useThemeMode } from '../../contexts/ThemeModeContext'
import { brandLogoSrc } from '../../theme/brandAssets'
import { PlatformLogo } from './PlatformLogo'

interface PlatformBrandProps {
  logoSize?: number
  showTitle?: boolean
  to?: string
  sx?: SxProps<Theme>
}

export function PlatformBrand({ logoSize = 40, showTitle = true, to = '/', sx }: PlatformBrandProps) {
  const { mode } = useThemeMode()
  const logoSrc = brandLogoSrc(mode)

  const inner = showTitle ? (
    <Box
      component="img"
      src={logoSrc}
      alt="Kyvo"
      sx={{
        height: logoSize,
        width: 'auto',
        maxWidth: '100%',
        objectFit: 'contain',
        display: 'block',
      }}
    />
  ) : (
    <PlatformLogo size={logoSize} sx={{ mx: 0 }} />
  )

  const boxSx = [
    {
      display: 'inline-flex',
      alignItems: 'center',
      textDecoration: 'none',
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
