import { Box, Grid, Typography } from '@mui/material'
import { FunnelChart, type FunnelStage } from './FunnelChart'

export interface FunnelSeries {
  name: string
  stages: FunnelStage[]
}

interface FunnelCompareChartProps {
  title?: string
  series: FunnelSeries[]
}

export function FunnelCompareChart({ title, series }: FunnelCompareChartProps) {
  if (series.length === 0) {
    return null
  }

  return (
    <Box sx={{ my: 2 }}>
      {title ? (
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
          {title}
        </Typography>
      ) : null}
      <Grid container spacing={2}>
        {series.map((item) => (
          <Grid key={item.name} size={{ xs: 12, md: 6 }}>
            <FunnelChart title={item.name} stages={item.stages} compact />
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
