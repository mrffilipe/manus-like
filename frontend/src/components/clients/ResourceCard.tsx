import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined'
import RefreshIcon from '@mui/icons-material/Refresh'
import { Box, Chip, IconButton, Stack, Typography } from '@mui/material'
import type { ClientResource } from '../../types'
import { subtleSurfaceSx } from '../../theme/chatStyles'
import { ResourceTypeBadge } from './ResourceTypeBadge'

const RESOURCE_LABELS: Record<string, string> = {
  file: 'Arquivo',
  link: 'Link',
  prompt: 'Prompt',
  text: 'Texto',
}

const EXTRACTED_PREVIEW_LIMIT = 120

interface ResourceCardProps {
  resource: ClientResource
  onRefresh?: () => void
  onDelete: () => void
}

function truncateText(text: string, limit: number): string {
  if (text.length <= limit) {
    return text
  }
  return `${text.slice(0, limit).trimEnd()}…`
}

export function ResourceCard({ resource, onRefresh, onDelete }: ResourceCardProps) {
  return (
    <Box
      sx={{
        border: 1,
        borderColor: 'divider',
        borderRadius: 2,
        p: 2,
      }}
    >
      <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Stack
            direction="row"
            spacing={1}
            sx={{ alignItems: 'center', mb: 0.75, flexWrap: 'wrap' }}
            useFlexGap
          >
            <Typography variant="subtitle2" noWrap sx={{ flex: 1, minWidth: 0 }}>
              {resource.title}
            </Typography>
            <ResourceTypeBadge resourceType={resource.resource_type} />
            {resource.category ? <Chip size="small" variant="outlined" label={resource.category} /> : null}
          </Stack>

          {resource.url ? (
            <Typography
              variant="body2"
              color="text.secondary"
              noWrap
              title={resource.url}
              sx={{ display: 'block' }}
            >
              {resource.url}
            </Typography>
          ) : null}

          {resource.content ? (
            <Box
              sx={[
                subtleSurfaceSx(),
                {
                  mt: 1,
                  px: 1.5,
                  py: 1,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  whiteSpace: 'pre-wrap',
                },
              ]}
            >
              <Typography variant="body2" component="div">
                {resource.content}
              </Typography>
            </Box>
          ) : null}

          {resource.extracted_text ? (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }} noWrap>
              Conteúdo extraído: {truncateText(resource.extracted_text, EXTRACTED_PREVIEW_LIMIT)}
            </Typography>
          ) : null}
        </Box>

        <Stack direction="row" spacing={0.5} sx={{ flexShrink: 0 }}>
          {resource.resource_type === 'link' && onRefresh ? (
            <IconButton size="small" onClick={onRefresh} title="Atualizar scrape">
              <RefreshIcon fontSize="small" />
            </IconButton>
          ) : null}
          <IconButton size="small" onClick={onDelete} title="Excluir recurso">
            <DeleteOutlinedIcon fontSize="small" />
          </IconButton>
        </Stack>
      </Stack>
    </Box>
  )
}

export { RESOURCE_LABELS }
