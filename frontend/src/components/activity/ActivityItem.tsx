import CircleIcon from '@mui/icons-material/Circle'
import { Alert, Box, Stack, Typography } from '@mui/material'
import type { ActivityEvent } from '../../types'
import { activityStepLabel } from '../../utils/enumLabels'
import { ActivityPreview, shouldShowSummary } from './ActivityPreview'

interface ActivityItemProps {
  activity: ActivityEvent
  isLast?: boolean
  linear?: boolean
}

function formatTime(value: string): string {
  try {
    return new Date(value).toLocaleTimeString()
  } catch {
    return ''
  }
}

export function ActivityItem({ activity, isLast = false, linear = false }: ActivityItemProps) {
  const isError = activity.kind === 'error'
  const showSummary = shouldShowSummary(activity)

  return (
    <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-start' }}>
      <Stack sx={{ alignItems: 'center', pt: 0.5, minWidth: 16 }}>
        <CircleIcon
          sx={{
            fontSize: 10,
            color: isError ? 'error.main' : isLast ? 'primary.main' : 'text.disabled',
          }}
        />
        {!isLast ? (
          <Box
            sx={{
              width: 2,
              flex: 1,
              minHeight: 24,
              bgcolor: 'divider',
              mt: 0.5,
            }}
          />
        ) : null}
      </Stack>
      <Box sx={{ flex: 1, pb: 2 }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap' }}>
          <Typography variant="subtitle2">{activity.title}</Typography>
          <Typography variant="caption" color="text.secondary">
            {activityStepLabel(activity.step)} · {formatTime(activity.created_at)}
          </Typography>
        </Stack>
        {isError && activity.summary ? (
          <Alert severity="error" sx={{ mt: 1 }}>
            {activity.summary}
          </Alert>
        ) : null}
        {!isError && showSummary ? (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {activity.summary}
          </Typography>
        ) : null}
        {!isError ? <ActivityPreview activity={activity} linear={linear} /> : null}
      </Box>
    </Stack>
  )
}
