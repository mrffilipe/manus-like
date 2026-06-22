import DarkModeOutlinedIcon from '@mui/icons-material/DarkModeOutlined'
import LightModeOutlinedIcon from '@mui/icons-material/LightModeOutlined'
import { IconButton, Tooltip, type IconButtonProps } from '@mui/material'
import { useThemeMode } from '../contexts/ThemeModeContext'

interface ThemeModeToggleProps {
  color?: IconButtonProps['color']
}

export function ThemeModeToggle({ color = 'inherit' }: ThemeModeToggleProps) {
  const { mode, toggleMode } = useThemeMode()

  return (
    <Tooltip title={mode === 'light' ? 'Modo escuro' : 'Modo claro'}>
      <IconButton color={color} onClick={toggleMode} aria-label="Alternar tema">
        {mode === 'light' ? <DarkModeOutlinedIcon /> : <LightModeOutlinedIcon />}
      </IconButton>
    </Tooltip>
  )
}
