import { Box, CircularProgress, Stack, Typography } from '@mui/material'
import { useEffect, useMemo, useRef } from 'react'
import type { ActivityEvent } from '../../types'
import { ActivityItem } from './ActivityItem'
import { BrowserLivePreview } from './BrowserLivePreview'
import { groupActivityTimeline } from './groupActivityTimeline'

interface ActivityTimelineProps {
  activities: ActivityEvent[]
  loading?: boolean
  /** When true, activities flow linearly without an inner scroll container. */
  linear?: boolean
}

export function ActivityTimeline({ activities, loading = false, linear = false }: ActivityTimelineProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null)
  const entries = useMemo(() => groupActivityTimeline(activities), [activities])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activities.length, entries.length])

  if (loading && activities.length === 0) {
    return (
      <Stack sx={{ alignItems: 'center', py: 4 }}>
        <CircularProgress size={28} />
      </Stack>
    )
  }

  if (activities.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        O agente está iniciando. As atualizações aparecerão aqui em tempo real.
      </Typography>
    )
  }

  const content = (
    <>
      {entries.map((entry, index) => {
        const isLast = index === entries.length - 1
        if (entry.type === 'browser') {
          return (
            <BrowserLivePreview
              key={`browser-${entry.activities[0]?.id ?? index}`}
              activities={entry.activities}
              isLast={isLast}
            />
          )
        }
        return (
          <ActivityItem
            key={entry.activity.id}
            activity={entry.activity}
            isLast={isLast}
            linear={linear}
          />
        )
      })}
      <div ref={bottomRef} />
    </>
  )

  if (linear) {
    return <Box>{content}</Box>
  }

  return (
    <Box sx={{ maxHeight: 520, overflowY: 'auto', pr: 0.5 }}>
      {content}
    </Box>
  )
}
