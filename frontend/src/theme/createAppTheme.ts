import { alpha, createTheme, type Theme } from '@mui/material/styles'
import { ptBR } from '@mui/material/locale'
import type { PaletteMode } from '@mui/material'
import { paletteTokens, radius } from './tokens'
import { scrollbarStyleOverrides } from './scrollbarStyles'

function borderColor(mode: PaletteMode): string {
  return mode === 'dark' ? alpha('#f4f4f8', 0.08) : alpha('#0b0d12', 0.08)
}

export function createAppTheme(mode: PaletteMode): Theme {
  const tokens = mode === 'dark' ? paletteTokens.dark : paletteTokens.light
  const divider = borderColor(mode)
  const scrollbarStyles = scrollbarStyleOverrides(mode)

  return createTheme(
    ptBR,
    {
      palette: {
        mode,
        primary: tokens.primary,
        secondary: tokens.secondary,
        text: tokens.text,
        background: tokens.background,
        divider,
        action: {
          active: tokens.text.secondary,
          disabled: tokens.text.disabled,
        },
      },
      shape: {
        borderRadius: radius.md,
      },
      typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        fontSize: 14,
        h4: { fontWeight: 700, letterSpacing: '-0.02em' },
        h5: { fontWeight: 600, letterSpacing: '-0.01em' },
        h6: { fontWeight: 600 },
        button: {
          fontWeight: 600,
          textTransform: 'none',
        },
        allVariants: {
          letterSpacing: '0.01em',
        },
      },
      components: {
        MuiCssBaseline: {
          styleOverrides: {
            html: {
              scrollBehavior: 'smooth',
            },
            body: {
              margin: 0,
              minHeight: '100vh',
              backgroundColor: tokens.background.default,
              backgroundImage: 'none',
              ...scrollbarStyles,
            },
          },
        },
        MuiPaper: {
          defaultProps: {
            elevation: 0,
          },
          styleOverrides: {
            root: {
              backgroundImage: 'none',
              border: `1px solid ${divider}`,
              ...(mode === 'dark' && {
                boxShadow: '0 1px 0 rgba(255, 255, 255, 0.04) inset',
              }),
            },
          },
        },
        MuiCard: {
          defaultProps: {
            elevation: 0,
          },
          styleOverrides: {
            root: {
              transition: 'border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease',
            },
          },
        },
        MuiCardActionArea: {
          styleOverrides: {
            root: {
              transition: 'background-color 0.2s ease, transform 0.15s ease',
              '&:active': {
                transform: 'scale(0.995)',
              },
            },
          },
        },
        MuiButton: {
          defaultProps: {
            variant: 'outlined',
            disableElevation: true,
            size: 'medium',
          },
          styleOverrides: {
            root: {
              borderRadius: radius.sm,
              boxShadow: 'none',
              fontSize: '0.875rem',
              lineHeight: 1.5,
              transition:
                'color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease',
              '&:hover': {
                boxShadow: 'none',
              },
              '&:active': {
                transform: 'scale(0.98)',
              },
            },
            sizeSmall: {
              fontSize: '0.8125rem',
              padding: '4px 12px',
            },
            sizeMedium: {
              fontSize: '0.875rem',
              padding: '6px 16px',
            },
            sizeLarge: {
              fontSize: '0.9375rem',
              padding: '10px 22px',
            },
            outlined: {
              borderWidth: '1.5px',
              '&:hover': {
                borderWidth: '1.5px',
                backgroundColor: alpha(tokens.primary.main, mode === 'dark' ? 0.1 : 0.06),
              },
              '&:active': {
                backgroundColor: alpha(tokens.primary.main, mode === 'dark' ? 0.16 : 0.1),
              },
            },
            outlinedPrimary: {
              color: tokens.primary.main,
              borderColor: alpha(tokens.primary.main, mode === 'dark' ? 0.55 : 0.45),
              '&:hover': {
                borderColor: tokens.primary.main,
                color: tokens.primary.main,
              },
            },
            contained: {
              '&:hover': {
                boxShadow: mode === 'dark' ? '0 4px 14px rgba(129, 140, 248, 0.22)' : '0 4px 14px rgba(79, 70, 229, 0.2)',
              },
            },
            text: {
              border: 'none',
              '&:hover': {
                border: 'none',
                backgroundColor: mode === 'dark' ? alpha('#c5c8d3', 0.1) : alpha('#0b0d12', 0.05),
              },
            },
          },
        },
        MuiFormControlLabel: {
          styleOverrides: {
            root: {
              alignItems: 'center',
              marginLeft: 0,
              marginRight: 0,
              gap: 4,
            },
            label: {
              lineHeight: 1.45,
            },
          },
        },
        MuiCheckbox: {
          styleOverrides: {
            root: {
              padding: 6,
            },
          },
        },
        MuiFormHelperText: {
          styleOverrides: {
            root: {
              textAlign: 'left',
              marginLeft: 0,
              marginRight: 0,
            },
          },
        },
        MuiOutlinedInput: {
          styleOverrides: {
            root: {
              borderRadius: radius.sm,
              ...(mode === 'dark' && {
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: alpha('#c5c8d3', 0.2),
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: alpha('#c5c8d3', 0.32),
                },
              }),
            },
          },
        },
        MuiTableContainer: {
          styleOverrides: {
            root: {
              borderRadius: radius.sm,
              border: `1px solid ${divider}`,
            },
          },
        },
        MuiTableHead: {
          styleOverrides: {
            root: {
              '& .MuiTableCell-head': {
                fontWeight: 600,
                backgroundColor: mode === 'dark' ? alpha('#c5c8d3', 0.06) : alpha('#0b0d12', 0.04),
              },
            },
          },
        },
        MuiTableRow: {
          styleOverrides: {
            root: {
              '&:last-child td': {
                borderBottom: 0,
              },
              '&:hover': {
                backgroundColor:
                  mode === 'dark' ? alpha(tokens.primary.main, 0.06) : alpha(tokens.primary.main, 0.04),
              },
            },
          },
        },
        MuiDrawer: {
          styleOverrides: {
            paper: {
              borderRight: `1px solid ${divider}`,
              backgroundImage: 'none',
              ...(mode === 'dark' && {
                backgroundColor: tokens.background.paper,
              }),
            },
          },
        },
        MuiListItemIcon: {
          styleOverrides: {
            root: {
              minWidth: 40,
              color: 'inherit',
            },
          },
        },
        MuiListItemButton: {
          styleOverrides: {
            root: {
              borderRadius: radius.sm,
              marginBottom: 4,
              color: tokens.text.primary,
              '& .MuiListItemText-primary': {
                color: 'inherit',
              },
              '&:hover': {
                backgroundColor: mode === 'dark' ? alpha('#c5c8d3', 0.08) : alpha('#0b0d12', 0.04),
              },
              '&.Mui-selected': {
                backgroundColor: alpha(tokens.primary.main, mode === 'dark' ? 0.18 : 0.1),
                color: tokens.primary.main,
                '&:hover': {
                  backgroundColor: alpha(tokens.primary.main, mode === 'dark' ? 0.24 : 0.14),
                },
                '& .MuiListItemIcon-root': {
                  color: tokens.primary.main,
                },
                '& .MuiListItemText-primary': {
                  color: 'inherit',
                },
              },
            },
          },
        },
        MuiIconButton: {
          styleOverrides: {
            root: {
              color: 'inherit',
              transition: 'background-color 0.2s ease, color 0.2s ease, transform 0.15s ease',
              '&:hover': {
                backgroundColor: mode === 'dark' ? alpha('#c5c8d3', 0.1) : alpha('#0b0d12', 0.06),
              },
              '&:active': {
                transform: 'scale(0.94)',
              },
            },
          },
        },
        MuiDialog: {
          styleOverrides: {
            paper: {
              backgroundImage: 'none',
            },
          },
        },
        MuiDialogContent: {
          styleOverrides: {
            root: {
              backgroundColor: tokens.background.paper,
              ...scrollbarStyles,
            },
            dividers: {
              borderColor: divider,
            },
          },
        },
        MuiAppBar: {
          defaultProps: {
            color: 'inherit',
            elevation: 0,
          },
          styleOverrides: {
            root: {
              borderBottom: `1px solid ${divider}`,
              backgroundImage: 'none',
              color: tokens.text.primary,
              ...(mode === 'dark' && {
                backgroundColor: alpha(tokens.background.paper, 0.92),
                backdropFilter: 'blur(8px)',
              }),
            },
          },
        },
        MuiChip: {
          styleOverrides: {
            root: {
              fontWeight: 500,
              transition: 'background-color 0.2s ease, border-color 0.2s ease',
            },
            outlined: {
              ...(mode === 'dark' && {
                borderColor: alpha('#c5c8d3', 0.24),
              }),
            },
          },
        },
        MuiAlert: {
          styleOverrides: {
            root: {
              borderRadius: radius.sm,
            },
            standardWarning: {
              ...(mode === 'dark' && {
                backgroundColor: alpha('#f59e0b', 0.12),
                color: '#fcd34d',
              }),
            },
          },
        },
        MuiStepper: {
          styleOverrides: {
            root: {
              background: 'transparent',
            },
          },
        },
        MuiStepConnector: {
          styleOverrides: {
            line: {
              borderColor: alpha(tokens.primary.main, mode === 'dark' ? 0.2 : 0.16),
              borderTopWidth: 2,
            },
          },
        },
        MuiStepIcon: {
          styleOverrides: {
            root: {
              color: mode === 'dark' ? alpha('#8a8e9c', 0.35) : alpha('#0b0d12', 0.2),
              '&.Mui-active': {
                color: tokens.primary.main,
              },
              '&.Mui-completed': {
                color: tokens.primary.main,
              },
            },
          },
        },
      },
    },
  )
}

export function getAuthBackground(mode: PaletteMode): string {
  const tokens = mode === 'dark' ? paletteTokens.dark : paletteTokens.light
  return tokens.background.default
}
