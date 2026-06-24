import type { Theme } from '@mui/material/styles'

export type StageHighlight = 'bottleneck' | 'success' | 'neutral'

const STAGE_PALETTE = ['#1976d2', '#2e7d32', '#ed6c02', '#9c27b0', '#d32f2f', '#0288d1']

export function stageColor(theme: Theme, highlight: StageHighlight | undefined, index: number): string {
  if (highlight === 'bottleneck') return theme.palette.error.main
  if (highlight === 'success') return theme.palette.success.main
  if (highlight === 'neutral') return theme.palette.grey[500]
  return STAGE_PALETTE[index % STAGE_PALETTE.length]
}

export function compareSeriesColors(theme: Theme): [string, string] {
  return [theme.palette.primary.main, theme.palette.success.main]
}
