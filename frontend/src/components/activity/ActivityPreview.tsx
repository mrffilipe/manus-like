import { Box, Link, Stack, Typography } from '@mui/material'
import { MarkdownContent } from '../ui'
import type { ActivityEvent } from '../../types'

interface ActivityPreviewProps {
  activity: ActivityEvent
}

function MarkdownBlock({ content }: { content: string }) {
  return (
    <Box sx={{ mt: 1, maxHeight: 320, overflow: 'auto' }}>
      <MarkdownContent content={content} />
    </Box>
  )
}

export function ActivityPreview({ activity }: ActivityPreviewProps) {
  const { preview_type: previewType, preview_data: data } = activity
  if (!previewType || !data) {
    return null
  }

  if (previewType === 'search_results') {
    const results = (data.results as Array<{ title?: string; url?: string }> | undefined) ?? []
    const query = typeof data.query === 'string' ? data.query : null
    return (
      <Stack spacing={1} sx={{ mt: 1 }}>
        {query ? (
          <Typography variant="caption" color="text.secondary">
            Busca: {query}
          </Typography>
        ) : null}
        {results.map((item) => (
          <Box key={`${item.url}-${item.title}`}>
            {item.url ? (
              <Link href={item.url} target="_blank" rel="noopener noreferrer" variant="body2">
                {item.title || item.url}
              </Link>
            ) : (
              <Typography variant="body2">{item.title}</Typography>
            )}
          </Box>
        ))}
      </Stack>
    )
  }

  if (previewType === 'webpage') {
    const url = typeof data.url === 'string' ? data.url : ''
    const title = typeof data.title === 'string' ? data.title : ''
    const excerpt = typeof data.excerpt === 'string' ? data.excerpt : ''
    const screenshot = typeof data.screenshot_base64 === 'string' ? data.screenshot_base64 : null
    const mime = typeof data.screenshot_mime === 'string' ? data.screenshot_mime : 'image/jpeg'
    const action = typeof data.action === 'string' ? data.action : ''
    if (action && action !== 'error') {
      return null
    }
    return (
      <Stack spacing={1.5} sx={{ mt: 1 }}>
        {screenshot ? (
          <Box
            component="img"
            src={`data:${mime};base64,${screenshot}`}
            alt={title || url || 'Page preview'}
            sx={{
              width: '100%',
              maxHeight: 220,
              objectFit: 'cover',
              objectPosition: 'top',
              borderRadius: 1,
              border: 1,
              borderColor: 'divider',
            }}
          />
        ) : null}
        <Stack spacing={0.5}>
          {title ? <Typography variant="subtitle2">{title}</Typography> : null}
          {url ? (
            <Link href={url} target="_blank" rel="noopener noreferrer" variant="caption">
              {url}
            </Link>
          ) : null}
          {excerpt ? <MarkdownBlock content={excerpt} /> : null}
        </Stack>
      </Stack>
    )
  }

  const content = typeof data.content === 'string' ? data.content : ''
  if (!content) {
    return null
  }

  if (previewType === 'markdown' || previewType === 'text') {
    return <MarkdownBlock content={content} />
  }

  return (
    <Typography variant="body2" color="text.secondary" sx={{ mt: 1, whiteSpace: 'pre-wrap' }}>
      {content}
    </Typography>
  )
}

export function getPreviewText(activity: ActivityEvent): string | null {
  const data = activity.preview_data
  if (!data) {
    return null
  }
  if (typeof data.content === 'string') {
    return data.content
  }
  if (activity.preview_type === 'search_results' && typeof data.query === 'string') {
    return data.query
  }
  if (activity.preview_type === 'webpage') {
    const url = typeof data.url === 'string' ? data.url : ''
    const excerpt = typeof data.excerpt === 'string' ? data.excerpt : ''
    return excerpt || url || null
  }
  return null
}

export function shouldShowSummary(activity: ActivityEvent): boolean {
  if (!activity.summary) {
    return false
  }
  const previewText = getPreviewText(activity)
  if (!previewText) {
    return true
  }
  const summary = activity.summary.trim()
  const preview = previewText.trim()
  if (summary === preview) {
    return false
  }
  if (preview.startsWith(summary) || summary.startsWith(preview)) {
    return false
  }
  if (summary.length > 20 && preview.includes(summary.slice(0, Math.min(summary.length, 80)))) {
    return false
  }
  return true
}
