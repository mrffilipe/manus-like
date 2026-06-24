import { Card, CardContent, Stack, Typography } from '@mui/material'

export interface KpiItem {
  label: string
  value: string
}

interface KpiStripProps {
  items: KpiItem[]
}

export function KpiStrip({ items }: KpiStripProps) {
  if (items.length === 0) {
    return null
  }

  return (
    <Stack
      direction="row"
      spacing={1.5}
      sx={{ flexWrap: 'wrap', gap: 1.5, my: 2 }}
      useFlexGap
    >
      {items.map((item) => (
        <Card key={item.label} variant="outlined" sx={{ minWidth: 140, flex: '1 1 140px' }}>
          <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
              {item.label}
            </Typography>
            <Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
              {item.value}
            </Typography>
          </CardContent>
        </Card>
      ))}
    </Stack>
  )
}
