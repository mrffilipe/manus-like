import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined'
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import InsertDriveFileOutlinedIcon from '@mui/icons-material/InsertDriveFileOutlined'
import LinkOutlinedIcon from '@mui/icons-material/LinkOutlined'
import { Chip, type ChipProps } from '@mui/material'
import type { SvgIconComponent } from '@mui/icons-material'

const RESOURCE_TYPE_CONFIG: Record<
  string,
  { label: string; color: ChipProps['color']; icon: SvgIconComponent }
> = {
  file: { label: 'Arquivo', color: 'info', icon: InsertDriveFileOutlinedIcon },
  link: { label: 'Link', color: 'primary', icon: LinkOutlinedIcon },
  prompt: { label: 'Prompt', color: 'secondary', icon: AutoAwesomeOutlinedIcon },
  text: { label: 'Texto', color: 'default', icon: ArticleOutlinedIcon },
}

interface ResourceTypeBadgeProps {
  resourceType: string
}

export function ResourceTypeBadge({ resourceType }: ResourceTypeBadgeProps) {
  const config = RESOURCE_TYPE_CONFIG[resourceType] ?? {
    label: resourceType,
    color: 'default' as const,
    icon: ArticleOutlinedIcon,
  }
  const Icon = config.icon

  return (
    <Chip
      size="small"
      variant="outlined"
      color={config.color}
      icon={<Icon sx={{ fontSize: '16px !important' }} />}
      label={config.label}
      sx={{ flexShrink: 0 }}
    />
  )
}
