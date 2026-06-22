import { Chip, Stack } from '@mui/material'
import { SectionCard } from '../ui'
import type { ActivityEvent } from '../../types'
import { ActivityTimeline } from './ActivityTimeline'

interface ActivityPreviewPanelProps {
  activities: ActivityEvent[]
  loading?: boolean
  connected?: boolean
  show?: boolean
}

export function ActivityPreviewPanel({
  activities,
  loading = false,
  connected = false,
  show = true,
}: ActivityPreviewPanelProps) {
  if (!show) {
    return null
  }

  const statusLabel = connected ? 'Ao vivo' : loading && activities.length === 0 ? 'Conectando…' : 'Sincronizando…'
  const statusColor = connected ? 'success' : 'default'

  return (
    <SectionCard
      title="Atividade ao vivo"
      actions={
        <Chip label={statusLabel} color={statusColor} size="small" variant="outlined" />
      }
    >
      <Stack spacing={2}>
        <ActivityTimeline activities={activities} loading={loading} />
      </Stack>
    </SectionCard>
  )
}
