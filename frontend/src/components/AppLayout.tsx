import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined'
import SmartToyOutlinedIcon from '@mui/icons-material/SmartToyOutlined'
import MenuIcon from '@mui/icons-material/Menu'
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from '@mui/material'
import type { ReactElement } from 'react'
import { useMemo, useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router'
import { ThemeModeToggle } from './ThemeModeToggle'
import { PlatformBrand } from './ui/PlatformBrand'
import { layout } from '../theme'

const appBarHeight = 64

interface NavItem {
  to: string
  label: string
  icon: ReactElement
}

interface NavGroup {
  label: string
  items: NavItem[]
}

const navGroups: NavGroup[] = [
  {
    label: 'General',
    items: [{ to: '/', label: 'Dashboard', icon: <DashboardOutlinedIcon /> }],
  },
  {
    label: 'Agent',
    items: [{ to: '/executions', label: 'Executions', icon: <SmartToyOutlinedIcon /> }],
  },
]

function isNavActive(pathname: string, to: string): boolean {
  if (to === '/') {
    return pathname === '/'
  }
  return pathname === to || pathname.startsWith(`${to}/`)
}

export function AppLayout() {
  const location = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const drawerContent = useMemo(
    () => (
      <Box sx={{ py: 1 }}>
        {navGroups.map((group) => (
          <Box key={group.label} sx={{ mb: 1 }}>
            <Typography
              variant="overline"
              sx={{ px: 2, py: 1, display: 'block', color: 'text.secondary' }}
            >
              {group.label}
            </Typography>
            <List dense disablePadding>
              {group.items.map((item) => {
                const active = isNavActive(location.pathname, item.to)
                return (
                  <ListItemButton
                    key={item.to}
                    component={Link}
                    to={item.to}
                    selected={active}
                    onClick={() => setMobileOpen(false)}
                    sx={{ mx: 1, borderRadius: 2 }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.label} />
                  </ListItemButton>
                )
              })}
            </List>
          </Box>
        ))}
      </Box>
    ),
    [location.pathname],
  )

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          height: appBarHeight,
          bgcolor: 'background.paper',
          color: 'text.primary',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ minHeight: `${appBarHeight}px !important`, gap: 1 }}>
          <IconButton edge="start" onClick={() => setMobileOpen(true)} sx={{ display: { md: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <PlatformBrand />
          <Box sx={{ flexGrow: 1 }} />
          <ThemeModeToggle />
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': { width: layout.sidebarWidth, boxSizing: 'border-box' },
        }}
      >
        {drawerContent}
      </Drawer>

      <Box
        component="main"
        sx={{
          pt: `${appBarHeight + 24}px`,
          pb: 6,
          px: { xs: 2, sm: 3 },
        }}
      >
        <Box sx={{ maxWidth: layout.contentMaxWidth, mx: 'auto' }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  )
}
