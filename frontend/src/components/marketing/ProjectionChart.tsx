import { Box, Typography, useTheme } from '@mui/material'
import { BarChart } from '@mui/x-charts/BarChart'

export interface ProjectionScenario {
  label: string
  value: number
  range?: [number, number]
}

interface ProjectionChartProps {
  title?: string
  unit?: string
  scenarios: ProjectionScenario[]
}

function formatScenarioLabel(scenario: ProjectionScenario, unit: string): string {
  if (scenario.range) {
    return `${scenario.label}\n(${scenario.range[0]}–${scenario.range[1]} ${unit})`
  }
  return scenario.label
}

export function ProjectionChart({ title, unit = 'leads', scenarios }: ProjectionChartProps) {
  const theme = useTheme()

  if (scenarios.length === 0) {
    return null
  }

  const labels = scenarios.map((s) => formatScenarioLabel(s, unit))
  const data = scenarios.map((s) => s.value)
  const maxValue = Math.max(...data, 1)

  return (
    <Box sx={{ my: 2 }}>
      {title ? (
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
          {title}
        </Typography>
      ) : null}
      <Box sx={{ width: '100%', height: Math.max(260, scenarios.length * 48 + 100) }}>
        <BarChart
          xAxis={[{ scaleType: 'band', data: labels }]}
          yAxis={[{ min: 0, max: Math.ceil(maxValue * 1.2), label: unit }]}
          series={[
            {
              data,
              color: theme.palette.secondary.main,
              valueFormatter: (value, context) => {
                const scenario = scenarios[context.dataIndex]
                if (scenario?.range) {
                  return `${scenario.range[0]}–${scenario.range[1]} ${unit}`
                }
                return `${value} ${unit}`
              },
            },
          ]}
          margin={{ left: 48, right: 16, top: 16, bottom: 80 }}
          grid={{ horizontal: true }}
          hideLegend
        />
      </Box>
    </Box>
  )
}
