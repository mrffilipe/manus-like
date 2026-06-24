import { Box } from '@mui/material'
import { useEffect, useRef } from 'react'
import { chat } from '../../theme/tokens'
import { ActivitySummaryBar } from './ActivitySummaryBar'
import { ChatComposer } from './ChatComposer'
import type { ActivityEvent } from '../../types'

interface ChatFooterProps {
  onSend: (text: string, files?: File[]) => Promise<void>
  composerDisabled?: boolean
  composerPlaceholder?: string
  showActivity?: boolean
  activities?: ActivityEvent[]
  activityLoading?: boolean
  connected?: boolean
  isRunning?: boolean
  overlay?: boolean
  onHeightChange?: (height: number) => void
  lockedClientName?: string | null
}

const footerColumnSx = {
  width: '100%',
  maxWidth: chat.threadMaxWidth,
  mx: 'auto',
  px: { xs: 2, sm: 3 },
} as const

export function ChatFooter({
  onSend,
  composerDisabled = false,
  composerPlaceholder,
  showActivity = false,
  activities = [],
  activityLoading = false,
  connected = false,
  isRunning = false,
  overlay = true,
  onHeightChange,
  lockedClientName,
}: ChatFooterProps) {
  const footerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!overlay) {
      return
    }

    const element = footerRef.current
    if (!element) {
      return
    }

    const reportHeight = () => {
      onHeightChange?.(element.getBoundingClientRect().height)
    }

    const observer = new ResizeObserver(reportHeight)
    observer.observe(element)
    reportHeight()

    return () => observer.disconnect()
  }, [onHeightChange, overlay, showActivity, activities.length, activityLoading])

  const column = (
    <Box
      ref={footerRef}
      sx={[
        footerColumnSx,
        overlay
          ? (theme) => ({
              pt: 3,
              background: `linear-gradient(to bottom, transparent 0%, ${theme.palette.background.default} 28%)`,
            })
          : { flexShrink: 0 },
      ]}
    >
      {showActivity ? (
        <ActivitySummaryBar
          activities={activities}
          loading={activityLoading}
          connected={connected}
          isRunning={isRunning}
        />
      ) : null}
      <ChatComposer
        onSend={onSend}
        disabled={composerDisabled}
        placeholder={composerPlaceholder}
        lockedClientName={lockedClientName}
      />
    </Box>
  )

  if (!overlay) {
    return column
  }

  return (
    <Box
      sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 2,
        pointerEvents: 'none',
      }}
    >
      {column}
    </Box>
  )
}
