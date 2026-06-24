import { BarCompareChart, type BarCompareMetric } from './BarCompareChart'
import { FunnelChart, type FunnelStage } from './FunnelChart'
import { FunnelCompareChart, type FunnelSeries } from './FunnelCompareChart'
import { KpiStrip, type KpiItem } from './KpiStrip'
import { ProjectionChart, type ProjectionScenario } from './ProjectionChart'

interface ChartBlockProps {
  data: Record<string, unknown>
}

export function ChartBlock({ data }: ChartBlockProps) {
  const type = data.type as string | undefined

  if (type === 'funnel') {
    const stages = (data.stages as FunnelStage[]) || []
    const title = data.title as string | undefined
    return <FunnelChart title={title} stages={stages} />
  }

  if (type === 'kpi') {
    const items = (data.items as KpiItem[]) || []
    return <KpiStrip items={items} />
  }

  if (type === 'funnel_compare') {
    const series = (data.series as FunnelSeries[]) || []
    const title = data.title as string | undefined
    return <FunnelCompareChart title={title} series={series} />
  }

  if (type === 'bar_compare') {
    const metrics = (data.metrics as BarCompareMetric[]) || []
    const title = data.title as string | undefined
    const yAxisLabel = data.yAxisLabel as string | undefined
    return <BarCompareChart title={title} yAxisLabel={yAxisLabel} metrics={metrics} />
  }

  if (type === 'projection') {
    const scenarios = (data.scenarios as ProjectionScenario[]) || []
    const title = data.title as string | undefined
    const unit = data.unit as string | undefined
    return <ProjectionChart title={title} unit={unit} scenarios={scenarios} />
  }

  return null
}

export function parseBlockJson(raw: string): Record<string, unknown> | null {
  try {
    const parsed = JSON.parse(raw.trim()) as Record<string, unknown>
    return parsed && typeof parsed === 'object' ? parsed : null
  } catch {
    return null
  }
}
