import type { ActivityEvent } from '../../types'

export type TimelineEntry =
  | { type: 'item'; activity: ActivityEvent }
  | { type: 'browser'; activities: ActivityEvent[] }

function isBrowserSessionEvent(activity: ActivityEvent): boolean {
  if (activity.step !== 'browser') {
    return false
  }
  if (activity.preview_type === 'webpage') {
    return true
  }
  const action = activity.preview_data?.action
  return typeof action === 'string'
}

export function groupActivityTimeline(activities: ActivityEvent[]): TimelineEntry[] {
  const entries: TimelineEntry[] = []
  let browserBuffer: ActivityEvent[] = []

  function flushBrowser() {
    if (browserBuffer.length > 0) {
      entries.push({ type: 'browser', activities: [...browserBuffer] })
      browserBuffer = []
    }
  }

  for (const activity of activities) {
    if (isBrowserSessionEvent(activity)) {
      browserBuffer.push(activity)
      continue
    }
    flushBrowser()
    entries.push({ type: 'item', activity })
  }

  flushBrowser()
  return entries
}
