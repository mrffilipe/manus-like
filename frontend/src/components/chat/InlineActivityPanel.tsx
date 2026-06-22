import { Collapse, Stack } from '@mui/material'
import { ActivityTimeline } from '../activity/ActivityTimeline'
import type { ActivityEvent } from '../../types'
import { subtleSurfaceSx } from '../../theme/chatStyles'

interface InlineActivityPanelProps {
  activities: ActivityEvent[]
  loading?: boolean
  expanded?: boolean
}

export function InlineActivityPanel({
  activities,
  loading = false,
  expanded = true,
}: InlineActivityPanelProps) {
  if (activities.length === 0 && !loading) {
    return null
  }

  return (
    <Collapse in={expanded}>
      <Stack
        spacing={1.5}
        sx={[
          {
            my: 2,
            py: 2,
            px: 2,
          },
          subtleSurfaceSx(),
        ]}
      >
        <ActivityTimeline activities={activities} loading={loading} />
      </Stack>
    </Collapse>
  )
}
