import { Box, Typography, useTheme } from '@mui/material'
import { BarChart } from '@mui/x-charts/BarChart'
import { stageColor, type StageHighlight } from './chartTheme'

export interface FunnelStage {
  label: string
  pct: number
  absolute?: number | null
  highlight?: StageHighlight
}

interface FunnelChartProps {
  title?: string
  stages: FunnelStage[]
  compact?: boolean
}

export function FunnelChart({ title, stages, compact = false }: FunnelChartProps) {
  const theme = useTheme()

  if (stages.length === 0) {
    return null
  }

  const labels = stages.map((s) => s.label)
  const data = stages.map((s) => s.pct)
  const colors = stages.map((s, i) => stageColor(theme, s.highlight, i))

  return (
    <Box sx={{ my: compact ? 0 : 2 }}>
      {title ? (
        <Typography variant={compact ? 'subtitle2' : 'subtitle1'} sx={{ fontWeight: 600, mb: 1.5 }}>
          {title}
        </Typography>
      ) : null}
      <Box sx={{ width: '100%', height: Math.max(compact ? 180 : 220, stages.length * (compact ? 40 : 48)) }}>
        <BarChart
          layout="horizontal"
          yAxis={[{ scaleType: 'band', data: labels, width: compact ? 96 : 120 }]}
          xAxis={[{ min: 0, max: 100, valueFormatter: (v: number) => `${v}%` }]}
          series={[
            {
              data,
              valueFormatter: (value, context) => {
                const stage = stages[context.dataIndex]
                if (stage?.absolute != null) {
                  return `${value}% (${stage.absolute})`
                }
                return `${value}%`
              },
            },
          ]}
          colors={colors}
          margin={{ left: 8, right: 24, top: 4, bottom: 4 }}
          grid={{ vertical: true }}
          hideLegend
        />
      </Box>
    </Box>
  )
}
