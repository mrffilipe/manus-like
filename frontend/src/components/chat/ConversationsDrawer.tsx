import AddIcon from '@mui/icons-material/Add'
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined'
import ForumOutlinedIcon from '@mui/icons-material/ForumOutlined'
import MoreHorizIcon from '@mui/icons-material/MoreHoriz'
import {
  Box,
  Button,
  CircularProgress,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Typography,
} from '@mui/material'
import type { ReactNode } from 'react'
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import { ConfirmDialog, GhostScrollBox } from '../ui'
import { deleteConversation } from '../../services/conversationService'
import type { ConversationSummary } from '../../types'
import { getApiErrorMessage } from '../../utils/apiError'
import { sidebarItemSx } from '../../theme/chatStyles'

interface ConversationsDrawerProps {
  conversations: ConversationSummary[]
  loading?: boolean
  onNavigate?: () => void
  onConversationDeleted?: () => void
  headerSlot?: ReactNode
}

function conversationLabel(conversation: ConversationSummary): string {
  if (conversation.title?.trim()) {
    return conversation.title
  }
  if (conversation.last_message_preview?.trim()) {
    return conversation.last_message_preview
  }
  return 'Nova conversa'
}

function truncateLabel(text: string, maxLength = 70): string {
  const trimmed = text.trim()
  if (trimmed.length <= maxLength) {
    return trimmed
  }
  return `${trimmed.slice(0, maxLength).trimEnd()}...`
}

export function ConversationsDrawer({
  conversations,
  loading = false,
  onNavigate,
  onConversationDeleted,
  headerSlot,
}: ConversationsDrawerProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const [menuAnchor, setMenuAnchor] = useState<HTMLElement | null>(null)
  const [menuConversationId, setMenuConversationId] = useState<string | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<ConversationSummary | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  function openMenu(event: React.MouseEvent<HTMLElement>, conversationId: string) {
    event.preventDefault()
    event.stopPropagation()
    setMenuAnchor(event.currentTarget)
    setMenuConversationId(conversationId)
  }

  function closeMenu() {
    setMenuAnchor(null)
    setMenuConversationId(null)
  }

  async function handleConfirmDelete() {
    if (!deleteTarget) {
      return
    }

    setDeleting(true)
    setDeleteError(null)

    try {
      await deleteConversation(deleteTarget.id)
      closeMenu()
      setDeleteTarget(null)
      onConversationDeleted?.()

      if (location.pathname === `/c/${deleteTarget.id}`) {
        navigate('/')
      }
    } catch (err) {
      setDeleteError(getApiErrorMessage(err))
    } finally {
      setDeleting(false)
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {headerSlot}

      <Box sx={{ px: 1.5, py: 1.5 }}>
        <Button
          component={Link}
          to="/"
          variant="text"
          fullWidth
          startIcon={<AddIcon sx={{ fontSize: 18 }} />}
          onClick={onNavigate}
          sx={{
            justifyContent: 'flex-start',
            px: 1.5,
            py: 1,
            borderRadius: 2,
            color: 'text.primary',
            fontWeight: 500,
            '&:hover': { bgcolor: 'action.hover' },
          }}
        >
          Nova conversa
        </Button>
      </Box>

      <Typography
        variant="overline"
        sx={{ px: 2.5, py: 0.5, display: 'block', color: 'text.disabled', letterSpacing: '0.08em' }}
      >
        Conversas
      </Typography>

      <GhostScrollBox sx={{ flex: 1, overflow: 'auto', pb: 2 }}>
        {loading && conversations.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={22} />
          </Box>
        ) : null}

        {!loading && conversations.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ px: 2.5, py: 2 }}>
            Nenhuma conversa ainda
          </Typography>
        ) : null}

        <List dense disablePadding>
          {conversations.map((conversation) => {
            const to = `/c/${conversation.id}`
            const active = location.pathname === to
            return (
              <ListItemButton
                key={conversation.id}
                component={Link}
                to={to}
                selected={active}
                onClick={onNavigate}
                sx={[
                  sidebarItemSx(active),
                  {
                    position: 'relative',
                    '&:hover .conversation-menu-btn': { opacity: 1 },
                  },
                ]}
              >
                <ListItemIcon sx={{ minWidth: 32, color: active ? 'primary.main' : 'text.disabled' }}>
                  <ForumOutlinedIcon sx={{ fontSize: 18 }} />
                </ListItemIcon>
                <ListItemText
                  primary={conversationLabel(conversation)}
                  slotProps={{
                    primary: { noWrap: true, sx: { fontSize: '0.875rem', fontWeight: active ? 500 : 400, pr: 3 } },
                  }}
                />
                <IconButton
                  className="conversation-menu-btn"
                  size="small"
                  onClick={(event) => openMenu(event, conversation.id)}
                  sx={{
                    position: 'absolute',
                    right: 8,
                    opacity: menuConversationId === conversation.id ? 1 : 0,
                    transition: 'opacity 0.15s ease',
                  }}
                >
                  <MoreHorizIcon sx={{ fontSize: 18 }} />
                </IconButton>
              </ListItemButton>
            )
          })}
        </List>
      </GhostScrollBox>

      <Menu anchorEl={menuAnchor} open={Boolean(menuAnchor)} onClose={closeMenu}>
        <MenuItem
          onClick={() => {
            const target = conversations.find((item) => item.id === menuConversationId)
            closeMenu()
            if (target) {
              setDeleteTarget(target)
            }
          }}
          sx={{ color: 'error.main', gap: 1 }}
        >
          <DeleteOutlinedIcon sx={{ fontSize: 18 }} />
          Excluir
        </MenuItem>
      </Menu>

      <ConfirmDialog
        open={Boolean(deleteTarget)}
        title="Excluir conversa"
        message={
          deleteTarget
            ? `Tem certeza que deseja excluir "${truncateLabel(conversationLabel(deleteTarget))}"? Esta ação remove permanentemente todas as mensagens, execuções e memórias associadas.${deleteError ? `\n\n${deleteError}` : ''}`
            : ''
        }
        confirmLabel="Excluir"
        confirmColor="error"
        loading={deleting}
        onClose={() => {
          if (!deleting) {
            setDeleteTarget(null)
            setDeleteError(null)
          }
        }}
        onConfirm={handleConfirmDelete}
      />
    </Box>
  )
}
