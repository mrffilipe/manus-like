import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router/dom'
import { AppLocalizationProvider } from './components/providers/AppLocalizationProvider'
import { ThemeModeProvider } from './contexts/ThemeModeContext'
import { router } from './routes'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppLocalizationProvider>
      <ThemeModeProvider>
        <RouterProvider router={router} />
      </ThemeModeProvider>
    </AppLocalizationProvider>
  </StrictMode>,
)
