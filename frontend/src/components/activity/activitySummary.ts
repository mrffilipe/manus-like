import type { ActivityEvent } from '../../types'
import { groupActivityTimeline } from './groupActivityTimeline'

export interface ActivityThumbnail {
  src: string
  alt: string
}

export interface ActivityStepProgress {
  current: number
  total: number
}

export function getLatestActivityThumbnail(activities: ActivityEvent[]): ActivityThumbnail | null {
  for (let index = activities.length - 1; index >= 0; index -= 1) {
    const data = activities[index].preview_data
    if (!data) {
      continue
    }

    const screenshot = data.screenshot_base64
    if (typeof screenshot === 'string' && screenshot.length > 0) {
      const mime = typeof data.screenshot_mime === 'string' ? data.screenshot_mime : 'image/jpeg'
      const title = typeof data.title === 'string' ? data.title : ''
      const url = typeof data.url === 'string' ? data.url : ''
      return {
        src: `data:${mime};base64,${screenshot}`,
        alt: title || url || 'Prévia da atividade',
      }
    }
  }

  return null
}

export function getActivitySummaryText(activities: ActivityEvent[], loading: boolean): string {
  if (activities.length === 0) {
    return loading ? 'Conectando ao agente…' : 'Aguardando atividade…'
  }

  const latest = activities[activities.length - 1]
  if (latest.summary?.trim()) {
    return latest.summary.trim()
  }

  return latest.title
}

export function getActivityStepProgress(
  activities: ActivityEvent[],
  isRunning = false,
): ActivityStepProgress {
  const entries = groupActivityTimeline(activities)
  const total = Math.max(entries.length, 1)
  let current = total

  if (isRunning && entries.length > 0) {
    current = Math.max(entries.length - 1, 1)
  }

  return { current, total }
}
