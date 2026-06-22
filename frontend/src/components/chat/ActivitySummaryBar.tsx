import ExpandLessIcon from '@mui/icons-material/ExpandLess'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import LanguageIcon from '@mui/icons-material/Language'
import {
  Box,
  CircularProgress,
  Collapse,
  keyframes,
  Stack,
  Typography,
} from '@mui/material'
import { useMemo, useState } from 'react'
import type { ActivityEvent } from '../../types'
import { floatingSurfaceSx } from '../../theme/chatStyles'
import {
  getActivityStepProgress,
  getActivitySummaryText,
  getLatestActivityThumbnail,
} from '../activity/activitySummary'
import { ActivityTimeline } from '../activity/ActivityTimeline'

const pulse = keyframes`
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
`

interface ActivitySummaryBarProps {
  activities: ActivityEvent[]
  loading?: boolean
  connected?: boolean
  isRunning?: boolean
}

export function ActivitySummaryBar({
  activities,
  loading = false,
  connected = false,
  isRunning = false,
}: ActivitySummaryBarProps) {
  const [expanded, setExpanded] = useState(false)

  const summaryText = useMemo(
    () => getActivitySummaryText(activities, loading),
    [activities, loading],
  )
  const thumbnail = useMemo(() => getLatestActivityThumbnail(activities), [activities])
  const progress = useMemo(
    () => getActivityStepProgress(activities, isRunning),
    [activities, isRunning],
  )

  if (activities.length === 0 && !loading) {
    return null
  }

  return (
    <Box sx={{ pb: 1, pointerEvents: 'auto' }}>
      <Collapse in={expanded}>
        <Box
          sx={[
            {
              mb: 1,
              px: 2,
              py: 1.5,
              maxHeight: 420,
              overflowY: 'auto',
            },
            floatingSurfaceSx(false),
          ]}
        >
          <ActivityTimeline activities={activities} loading={loading} linear />
        </Box>
      </Collapse>

      <Box
        role="button"
        tabIndex={0}
        onClick={() => setExpanded((value) => !value)}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            setExpanded((value) => !value)
          }
        }}
        sx={[
          {
            display: 'flex',
            alignItems: 'center',
            gap: 1.25,
            px: 1.25,
            py: 1,
            cursor: 'pointer',
            userSelect: 'none',
            transition: 'box-shadow 0.2s ease',
            '&:hover': {
              boxShadow: (theme) =>
                `0 4px 20px ${theme.palette.mode === 'dark' ? 'rgba(0,0,0,0.35)' : 'rgba(0,0,0,0.08)'}`,
            },
          },
          floatingSurfaceSx(false),
        ]}
      >
        <Box
          sx={{
            width: 52,
            height: 40,
            flexShrink: 0,
            borderRadius: 1,
            overflow: 'hidden',
            border: 1,
            borderColor: 'divider',
            bgcolor: 'background.default',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {loading && activities.length === 0 ? (
            <CircularProgress size={16} />
          ) : thumbnail ? (
            <Box
              component="img"
              src={thumbnail.src}
              alt={thumbnail.alt}
              sx={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top center' }}
            />
          ) : (
            <LanguageIcon sx={{ fontSize: 18, color: 'text.disabled' }} />
          )}
        </Box>

        <Stack sx={{ flex: 1, minWidth: 0 }} spacing={0.25}>
          <Stack direction="row" spacing={0.75} sx={{ alignItems: 'center' }}>
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                flexShrink: 0,
                bgcolor: connected ? 'success.main' : 'text.disabled',
                animation: connected ? `${pulse} 1.5s ease-in-out infinite` : 'none',
              }}
            />
            <Typography variant="body2" noWrap sx={{ fontWeight: 500 }}>
              {summaryText}
            </Typography>
          </Stack>
        </Stack>

        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center', flexShrink: 0 }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
            {progress.current}/{progress.total}
          </Typography>
          {expanded ? (
            <ExpandLessIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          ) : (
            <ExpandMoreIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
          )}
        </Stack>
      </Box>
    </Box>
  )
}
