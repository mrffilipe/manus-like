import { CssBaseline, ThemeProvider } from '@mui/material'
import type { PaletteMode } from '@mui/material'
import { createContext, useCallback, useContext, useMemo, useState, type PropsWithChildren } from 'react'
import { createAppTheme } from '../theme/createAppTheme'

const STORAGE_KEY = 'manus-theme-mode'

interface ThemeModeContextValue {
  mode: PaletteMode
  toggleMode: () => void
  setMode: (mode: PaletteMode) => void
}

const ThemeModeContext = createContext<ThemeModeContextValue | undefined>(undefined)

function readStoredMode(): PaletteMode {
  if (typeof window === 'undefined') {
    return 'light'
  }
  const stored = window.localStorage.getItem(STORAGE_KEY)
  return stored === 'dark' ? 'dark' : 'light'
}

export function ThemeModeProvider({ children }: PropsWithChildren) {
  const [mode, setModeState] = useState<PaletteMode>(readStoredMode)

  const setMode = useCallback((nextMode: PaletteMode) => {
    setModeState(nextMode)
    window.localStorage.setItem(STORAGE_KEY, nextMode)
    document.documentElement.style.colorScheme = nextMode
  }, [])

  const toggleMode = useCallback(() => {
    setModeState((prev) => {
      const nextMode: PaletteMode = prev === 'light' ? 'dark' : 'light'
      window.localStorage.setItem(STORAGE_KEY, nextMode)
      document.documentElement.style.colorScheme = nextMode
      return nextMode
    })
  }, [])

  const theme = useMemo(() => createAppTheme(mode), [mode])

  const value = useMemo(
    () => ({
      mode,
      toggleMode,
      setMode,
    }),
    [mode, setMode, toggleMode],
  )

  return (
    <ThemeModeContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  )
}

export function useThemeMode(): ThemeModeContextValue {
  const context = useContext(ThemeModeContext)
  if (!context) {
    throw new Error('useThemeMode must be used within ThemeModeProvider')
  }
  return context
}
