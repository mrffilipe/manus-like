import CircleIcon from '@mui/icons-material/Circle'
import LanguageIcon from '@mui/icons-material/Language'
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Chip,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { useEffect, useMemo, useState } from 'react'
import type { ActivityEvent } from '../../types'
import { activityStepLabel } from '../../utils/enumLabels'

interface BrowserLivePreviewProps {
  activities: ActivityEvent[]
  isLast?: boolean
}

function formatTime(value: string): string {
  try {
    return new Date(value).toLocaleTimeString()
  } catch {
    return ''
  }
}

function actionLabel(action: string | undefined): string {
  switch (action) {
    case 'loading':
      return 'Carregando…'
    case 'loaded':
      return 'Página aberta'
    case 'scroll':
      return 'Rolando…'
    case 'done':
      return 'Leitura concluída'
    default:
      return 'Navegando…'
  }
}

export function BrowserLivePreview({ activities, isLast = false }: BrowserLivePreviewProps) {
  const latest = activities[activities.length - 1]
  const latestData = latest.preview_data ?? {}

  const frames = useMemo(
    () =>
      activities
        .map((activity) => {
          const shot = activity.preview_data?.screenshot_base64
          return typeof shot === 'string' ? shot : null
        })
        .filter((shot): shot is string => Boolean(shot)),
    [activities],
  )

  const [frameIndex, setFrameIndex] = useState(Math.max(frames.length - 1, 0))

  useEffect(() => {
    if (frames.length === 0) {
      return
    }
    const target = frames.length - 1
    if (target === frameIndex) {
      return
    }
    const timer = window.setTimeout(() => {
      setFrameIndex(target)
    }, 80)
    return () => window.clearTimeout(timer)
  }, [frameIndex, frames.length])

  const url = typeof latestData.url === 'string' ? latestData.url : ''
  const title = typeof latestData.title === 'string' ? latestData.title : ''
  const excerpt = typeof latestData.excerpt === 'string' ? latestData.excerpt : ''
  const action = typeof latestData.action === 'string' ? latestData.action : 'loading'
  const progress =
    typeof latestData.scroll_progress === 'number'
      ? Math.round(latestData.scroll_progress * 100)
      : action === 'done'
        ? 100
        : action === 'loaded'
          ? 10
          : 0
  const mime = typeof latestData.screenshot_mime === 'string' ? latestData.screenshot_mime : 'image/jpeg'
  const currentFrame = frames[frameIndex] ?? frames[frames.length - 1]
  const isActive = isLast && action !== 'done'

  return (
    <Stack direction="row" spacing={1.5} sx={{ alignItems: 'flex-start' }}>
      <Stack sx={{ alignItems: 'center', pt: 0.5, minWidth: 16 }}>
        <CircleIcon
          sx={{
            fontSize: 10,
            color: isLast ? 'primary.main' : 'text.disabled',
          }}
        />
        {!isLast ? (
          <Box sx={{ width: 2, flex: 1, minHeight: 24, bgcolor: 'divider', mt: 0.5 }} />
        ) : null}
      </Stack>

      <Box sx={{ flex: 1, pb: 2 }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', mb: 1 }}>
          <Typography variant="subtitle2">Navegando na web</Typography>
          <Typography variant="caption" color="text.secondary">
            {activityStepLabel('browser')} · {formatTime(latest.created_at)}
          </Typography>
          <Chip
            size="small"
            label={actionLabel(action)}
            color={isActive ? 'primary' : 'default'}
            variant={isActive ? 'filled' : 'outlined'}
            sx={{ height: 22 }}
          />
        </Stack>

        <Box
          sx={{
            border: 1,
            borderColor: 'divider',
            borderRadius: 2,
            overflow: 'hidden',
            bgcolor: 'background.paper',
            boxShadow: 1,
          }}
        >
          <Stack
            direction="row"
            spacing={1}
            sx={{
              alignItems: 'center',
              px: 1.5,
              py: 1,
              bgcolor: (theme) => (theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100'),
              borderBottom: 1,
              borderColor: 'divider',
            }}
          >
            <Stack direction="row" spacing={0.5}>
              <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#ff5f57' }} />
              <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#febc2e' }} />
              <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#28c840' }} />
            </Stack>
            <Stack
              direction="row"
              spacing={0.75}
              sx={{
                flex: 1,
                alignItems: 'center',
                px: 1.25,
                py: 0.5,
                borderRadius: 1,
                bgcolor: 'background.paper',
                minWidth: 0,
              }}
            >
              <LanguageIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
              <Typography variant="caption" noWrap sx={{ flex: 1 }}>
                {url || 'about:blank'}
              </Typography>
            </Stack>
          </Stack>

          <Box
            sx={{
              position: 'relative',
              bgcolor: '#0a0a0f',
              width: '100%',
              aspectRatio: { xs: '9 / 16', md: '16 / 9' },
              overflow: 'hidden',
            }}
          >
            {currentFrame ? (
              <Box
                key={frameIndex}
                component="img"
                src={`data:${mime};base64,${currentFrame}`}
                alt={title || url || 'Prévia da página'}
                sx={{
                  position: 'absolute',
                  inset: 0,
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  objectPosition: 'top center',
                  animation: 'browserFrameFade 0.45s ease',
                  '@keyframes browserFrameFade': {
                    from: { opacity: 0.2, transform: 'translateY(6px)' },
                    to: { opacity: 1, transform: 'translateY(0)' },
                  },
                }}
              />
            ) : (
              <Stack
                sx={{
                  position: 'absolute',
                  inset: 0,
                  alignItems: 'center',
                  justifyContent: 'center',
                  p: 3,
                }}
              >
                <LinearProgress sx={{ width: '60%', mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  Carregando página…
                </Typography>
              </Stack>
            )}

            {isActive ? (
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  pointerEvents: 'none',
                  background:
                    'linear-gradient(180deg, transparent 55%, rgba(0,0,0,0.35) 100%)',
                }}
              />
            ) : null}
          </Box>

          <Box sx={{ px: 1.5, py: 1 }}>
            <LinearProgress
              variant={isActive ? 'indeterminate' : 'determinate'}
              value={progress}
              sx={{ mb: 1, borderRadius: 1, height: 4 }}
            />
            <Typography variant="caption" color="text.secondary">
              {latest.title}
              {title ? ` — ${title}` : ''}
            </Typography>
          </Box>
        </Box>

        {excerpt && action === 'done' ? (
          <Accordion
            disableGutters
            elevation={0}
            sx={{
              mt: 1,
              border: 1,
              borderColor: 'divider',
              borderRadius: '8px !important',
              '&:before': { display: 'none' },
            }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="body2">Texto extraído da página</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                {excerpt}
              </Typography>
            </AccordionDetails>
          </Accordion>
        ) : null}
      </Box>
    </Stack>
  )
}
