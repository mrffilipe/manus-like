import { Box, Typography, useTheme } from '@mui/material'
import { BarChart } from '@mui/x-charts/BarChart'
import { compareSeriesColors } from './chartTheme'

export interface BarCompareSeries {
  name: string
  value: number
  note?: string
}

export interface BarCompareMetric {
  label: string
  series: BarCompareSeries[]
}

interface BarCompareChartProps {
  title?: string
  yAxisLabel?: string
  metrics: BarCompareMetric[]
}

export function BarCompareChart({ title, yAxisLabel = '%', metrics }: BarCompareChartProps) {
  const theme = useTheme()
  const [colorA, colorB] = compareSeriesColors(theme)

  if (metrics.length === 0) {
    return null
  }

  const seriesNames = metrics[0]?.series.map((s) => s.name) ?? []
  const labels = metrics.map((m) => m.label)
  const chartSeries = seriesNames.map((name, seriesIndex) => ({
    label: name,
    data: metrics.map((m) => m.series[seriesIndex]?.value ?? 0),
    color: seriesIndex === 0 ? colorA : colorB,
    valueFormatter: (value: number | null, context: { dataIndex: number }) => {
      const note = metrics[context.dataIndex]?.series[seriesIndex]?.note
      const formatted = value != null ? `${value}%` : '—'
      return note ? `${formatted} — ${note}` : formatted
    },
  }))

  return (
    <Box sx={{ my: 2 }}>
      {title ? (
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
          {title}
        </Typography>
      ) : null}
      <Box sx={{ width: '100%', height: Math.max(280, metrics.length * 56 + 80) }}>
        <BarChart
          xAxis={[{ scaleType: 'band', data: labels }]}
          yAxis={[{ label: yAxisLabel, valueFormatter: (v: number) => `${v}%` }]}
          series={chartSeries}
          margin={{ left: 48, right: 16, top: 32, bottom: 64 }}
          grid={{ horizontal: true }}
          slotProps={{
            legend: { position: { vertical: 'top', horizontal: 'end' } },
          }}
        />
      </Box>
    </Box>
  )
}
