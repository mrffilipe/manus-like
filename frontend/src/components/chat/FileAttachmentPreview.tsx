import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined'
import CloseIcon from '@mui/icons-material/Close'
import CodeOutlinedIcon from '@mui/icons-material/CodeOutlined'
import DataObjectOutlinedIcon from '@mui/icons-material/DataObjectOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import InsertDriveFileOutlinedIcon from '@mui/icons-material/InsertDriveFileOutlined'
import LanguageOutlinedIcon from '@mui/icons-material/LanguageOutlined'
import PictureAsPdfOutlinedIcon from '@mui/icons-material/PictureAsPdfOutlined'
import TableChartOutlinedIcon from '@mui/icons-material/TableChartOutlined'
import { Box, IconButton, Typography, alpha } from '@mui/material'
import type { SvgIconComponent } from '@mui/icons-material'
import { getFileExtension } from '../../constants/acceptedFiles'

interface FileTypeStyle {
  icon: SvgIconComponent
  color: string
}

const FILE_TYPE_STYLES: Record<string, FileTypeStyle> = {
  '.pdf': { icon: PictureAsPdfOutlinedIcon, color: '#e53935' },
  '.xlsx': { icon: TableChartOutlinedIcon, color: '#2e7d32' },
  '.xls': { icon: TableChartOutlinedIcon, color: '#2e7d32' },
  '.csv': { icon: TableChartOutlinedIcon, color: '#2e7d32' },
  '.tsv': { icon: TableChartOutlinedIcon, color: '#2e7d32' },
  '.md': { icon: ArticleOutlinedIcon, color: '#5c6bc0' },
  '.txt': { icon: DescriptionOutlinedIcon, color: '#5c6bc0' },
  '.log': { icon: DescriptionOutlinedIcon, color: '#5c6bc0' },
  '.docx': { icon: DescriptionOutlinedIcon, color: '#1565c0' },
  '.json': { icon: DataObjectOutlinedIcon, color: '#f57c00' },
  '.xml': { icon: DataObjectOutlinedIcon, color: '#f57c00' },
  '.yaml': { icon: DataObjectOutlinedIcon, color: '#f57c00' },
  '.yml': { icon: DataObjectOutlinedIcon, color: '#f57c00' },
  '.html': { icon: LanguageOutlinedIcon, color: '#e65100' },
  '.htm': { icon: LanguageOutlinedIcon, color: '#e65100' },
  '.js': { icon: CodeOutlinedIcon, color: '#f9a825' },
  '.ts': { icon: CodeOutlinedIcon, color: '#1976d2' },
  '.jsx': { icon: CodeOutlinedIcon, color: '#f9a825' },
  '.tsx': { icon: CodeOutlinedIcon, color: '#1976d2' },
  '.py': { icon: CodeOutlinedIcon, color: '#388e3c' },
  '.css': { icon: CodeOutlinedIcon, color: '#7b1fa2' },
}

const DEFAULT_STYLE: FileTypeStyle = {
  icon: InsertDriveFileOutlinedIcon,
  color: '#757575',
}

function getFileTypeStyle(filename: string): FileTypeStyle {
  const ext = getFileExtension(filename)
  return FILE_TYPE_STYLES[ext] ?? DEFAULT_STYLE
}

interface FileAttachmentPreviewProps {
  file: File
  onRemove: () => void
}

export function FileAttachmentPreview({ file, onRemove }: FileAttachmentPreviewProps) {
  const { icon: Icon, color } = getFileTypeStyle(file.name)

  return (
    <Box
      sx={(theme) => ({
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        px: 1,
        py: 0.75,
        borderRadius: 1.5,
        width: 200,
        flexShrink: 0,
        bgcolor: alpha(color, theme.palette.mode === 'dark' ? 0.18 : 0.12),
        boxShadow: `inset 0 0 0 1px ${alpha(color, theme.palette.mode === 'dark' ? 0.35 : 0.22)}`,
      })}
    >
      <Box
        sx={(theme) => ({
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 32,
          height: 32,
          borderRadius: 1,
          bgcolor: alpha(color, theme.palette.mode === 'dark' ? 0.28 : 0.2),
          color,
          flexShrink: 0,
        })}
      >
        <Icon sx={{ fontSize: 18 }} />
      </Box>
      <Typography
        variant="caption"
        noWrap
        title={file.name}
        sx={{ flex: 1, minWidth: 0, fontWeight: 500, lineHeight: 1.3 }}
      >
        {file.name}
      </Typography>
      <IconButton
        size="small"
        onClick={onRemove}
        aria-label={`Remover ${file.name}`}
        sx={{
          flexShrink: 0,
          color: 'text.secondary',
          '&:hover': { bgcolor: 'action.hover', color: 'text.primary' },
        }}
      >
        <CloseIcon sx={{ fontSize: 16 }} />
      </IconButton>
    </Box>
  )
}
