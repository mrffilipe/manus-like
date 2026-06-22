import { alpha, type Theme } from '@mui/material/styles'

const SCROLLBAR_HIDE_MS = 1500
const SCROLLBAR_SIZE = 6

export function ghostScrollbarSx(active: boolean): (theme: Theme) => Record<string, unknown> {
  return (theme) => {
    const thumb = alpha(theme.palette.text.primary, theme.palette.mode === 'dark' ? 0.28 : 0.22)
    const thumbHover = alpha(theme.palette.text.primary, theme.palette.mode === 'dark' ? 0.42 : 0.32)

    return {
      scrollbarGutter: 'stable',
      scrollbarWidth: 'thin' as const,
      scrollbarColor: active ? `${thumb} transparent` : 'transparent transparent',
      '&::-webkit-scrollbar': {
        width: SCROLLBAR_SIZE,
        height: SCROLLBAR_SIZE,
      },
      '&::-webkit-scrollbar-track': {
        backgroundColor: 'transparent',
      },
      '&::-webkit-scrollbar-thumb': {
        backgroundColor: active ? thumb : 'transparent',
        borderRadius: 999,
        '&:hover': {
          backgroundColor: active ? thumbHover : 'transparent',
        },
      },
    }
  }
}

export { SCROLLBAR_HIDE_MS, SCROLLBAR_SIZE }
