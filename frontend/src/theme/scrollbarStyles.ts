import { alpha, type PaletteMode } from '@mui/material'

export function scrollbarStyleOverrides(mode: PaletteMode) {
  const track = mode === 'dark' ? alpha('#c5c8d3', 0.08) : alpha('#0b0d12', 0.06)
  const thumb = mode === 'dark' ? alpha('#c5c8d3', 0.28) : alpha('#0b0d12', 0.22)
  const thumbHover = mode === 'dark' ? alpha('#c5c8d3', 0.4) : alpha('#0b0d12', 0.32)

  return {
    scrollbarWidth: 'thin' as const,
    scrollbarColor: `${thumb} ${track}`,
    '&::-webkit-scrollbar': {
      width: 8,
      height: 8,
    },
    '&::-webkit-scrollbar-track': {
      backgroundColor: track,
      borderRadius: 8,
    },
    '&::-webkit-scrollbar-thumb': {
      backgroundColor: thumb,
      borderRadius: 8,
      border: `2px solid ${track}`,
      '&:hover': {
        backgroundColor: thumbHover,
      },
    },
  }
}
