import MenuIcon from '@mui/icons-material/Menu'
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  Toolbar,
} from '@mui/material'
import { useState } from 'react'
import { Outlet } from 'react-router'
import { ThemeModeToggle } from './ThemeModeToggle'
import { ConversationsDrawer } from './chat/ConversationsDrawer'
import { PlatformBrand } from './ui/PlatformBrand'
import { useConversations } from '../hooks/useConversations'
import { layout } from '../theme'

const { sidebarWidth, appBarHeight } = layout

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { conversations, loading, refetch } = useConversations()

  const drawerContent = (
    <ConversationsDrawer
      conversations={conversations}
      loading={loading}
      onNavigate={() => setMobileOpen(false)}
      onConversationDeleted={() => void refetch()}
      headerSlot={
        <Box
          sx={{
            display: { xs: 'none', md: 'flex' },
            alignItems: 'center',
            justifyContent: 'space-between',
            px: 2,
            pt: 2,
            pb: 1,
          }}
        >
          <PlatformBrand logoSize={32} />
          <ThemeModeToggle />
        </Box>
      }
    />
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          height: appBarHeight,
          bgcolor: 'transparent',
          color: 'text.primary',
          borderBottom: 'none',
          display: { md: 'none' },
        }}
      >
        <Toolbar sx={{ minHeight: `${appBarHeight}px !important`, gap: 1, px: 2 }}>
          <IconButton edge="start" onClick={() => setMobileOpen(true)} size="small">
            <MenuIcon />
          </IconButton>
          <PlatformBrand logoSize={28} />
          <Box sx={{ flexGrow: 1 }} />
          <ThemeModeToggle />
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: sidebarWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              width: sidebarWidth,
              boxSizing: 'border-box',
              top: appBarHeight,
              height: `calc(100% - ${appBarHeight}px)`,
            },
          }}
        >
          {drawerContent}
        </Drawer>

        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              width: sidebarWidth,
              boxSizing: 'border-box',
              top: 0,
              height: '100%',
              borderRight: 'none',
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${sidebarWidth}px)` },
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          pt: { xs: `${appBarHeight}px`, md: 0 },
        }}
      >
        <Outlet context={{ refetchConversations: refetch }} />
      </Box>
    </Box>
  )
}

export interface AppLayoutOutletContext {
  refetchConversations: () => Promise<void>
}
