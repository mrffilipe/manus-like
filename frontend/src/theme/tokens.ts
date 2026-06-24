/**
 * Kyvo brand tokens — aligned with backend/Kyvo.API/wwwroot/css/account.css
 * and docs/Brand guideline/Brand-guideline.png
 */
export const layout = {
  sidebarWidth: 320,
  contentMaxWidth: 1200,
  pageMaxWidth: 800,
  dialogMaxWidth: 480,
  authMaxWidth: 440,
  bootstrapMaxWidth: 560,
  appBarHeight: 52,
} as const

export const chat = {
  threadMaxWidth: layout.pageMaxWidth,
  composerMaxWidth: layout.pageMaxWidth,
  sidebarItemRadius: 10,
  composerRadius: 20,
  messageGap: 3,
} as const

export const radius = {
  sm: 8,
  md: 12,
  lg: 18,
  xl: 18,
} as const

/** Espaçamento vertical padronizado entre blocos de formulário e modais. */
export const formSpacing = {
  stack: 2.5,
  section: 2,
  grid: 2,
  actionsTop: 0.5,
} as const

export const paletteTokens = {
  light: {
    primary: { main: '#4f46e5', dark: '#4338ca', light: '#7c3aed', contrastText: '#ffffff' },
    secondary: { main: '#7c3aed', dark: '#6d28d9', light: '#a78bfa', contrastText: '#ffffff' },
    text: { primary: '#0b0d12', secondary: '#4b5060', disabled: '#7a7f8e' },
    background: { default: '#f7f7fb', paper: '#ffffff' },
  },
  dark: {
    primary: { main: '#818cf8', dark: '#6366f1', light: '#a5b4fc', contrastText: '#1b1b27' },
    secondary: { main: '#7c3aed', dark: '#5b21b6', light: '#a78bfa', contrastText: '#f4f4f8' },
    text: { primary: '#f4f4f8', secondary: '#c5c8d3', disabled: '#8a8e9c' },
    background: { default: '#0a0a0f', paper: '#14141d' },
  },
} as const
