import { alpha, type Theme } from '@mui/material/styles'
import { chat } from './tokens'

type StyleFn = (theme: Theme) => Record<string, unknown>

export function sidebarNavButtonSx(active: boolean): StyleFn {
  return (theme) => ({
    justifyContent: 'flex-start',
    px: 1.5,
    py: 1,
    borderRadius: 2,
    color: 'text.primary',
    fontWeight: 500,
    minWidth: 0,
    overflow: 'hidden',
    transition: 'background-color 0.15s ease',
    '& .MuiButton-startIcon': { flexShrink: 0 },
    '&:hover': { bgcolor: 'action.hover' },
    ...(active && {
      bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.12 : 0.08),
    }),
  })
}

export function sidebarItemSx(active: boolean): StyleFn {
  return (theme) => ({
    borderRadius: `${chat.sidebarItemRadius}px`,
    mx: 1.5,
    py: 1.25,
    px: 1.5,
    mb: 0.5,
    transition: 'background-color 0.15s ease',
    ...(active && {
      bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.12 : 0.08),
      '& .MuiListItemText-primary': {
        fontWeight: 500,
        color: theme.palette.text.primary,
      },
    }),
  })
}

export function userPillSx(): StyleFn {
  return (theme) => ({
    display: 'inline-block',
    maxWidth: '70%',
    px: 2,
    py: 1,
    borderRadius: '16px',
    bgcolor: alpha(theme.palette.primary.main, theme.palette.mode === 'dark' ? 0.16 : 0.1),
    color: theme.palette.mode === 'dark' ? theme.palette.primary.light : theme.palette.primary.main,
  })
}

export function floatingSurfaceSx(focused = false): StyleFn {
  return (theme) => ({
    borderRadius: `${chat.composerRadius}px`,
    border: `1px solid ${alpha(theme.palette.divider, theme.palette.mode === 'dark' ? 0.35 : 0.6)}`,
    bgcolor: alpha(theme.palette.background.paper, theme.palette.mode === 'dark' ? 0.72 : 0.88),
    backdropFilter: 'blur(12px)',
    boxShadow: focused
      ? `0 0 0 2px ${alpha(theme.palette.primary.main, 0.2)}, 0 8px 32px ${alpha(theme.palette.common.black, 0.12)}`
      : `0 4px 24px ${alpha(theme.palette.common.black, theme.palette.mode === 'dark' ? 0.2 : 0.06)}`,
    transition: 'box-shadow 0.2s ease, border-color 0.2s ease',
  })
}

export function subtleSurfaceSx(): StyleFn {
  return (theme) => ({
    borderRadius: `${chat.sidebarItemRadius}px`,
    bgcolor: alpha(theme.palette.text.primary, theme.palette.mode === 'dark' ? 0.04 : 0.03),
  })
}

export function threadFadeSx(): StyleFn {
  return (theme) => ({
    position: 'relative',
    '&::after': {
      content: '""',
      position: 'sticky',
      bottom: 0,
      left: 0,
      right: 0,
      height: 48,
      pointerEvents: 'none',
      background: `linear-gradient(to bottom, transparent, ${theme.palette.background.default})`,
    },
  })
}
