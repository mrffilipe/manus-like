import { createBrowserRouter, Navigate } from 'react-router'
import { AppLayout } from './components/AppLayout'
import { ChatPage, NotFoundPage } from './pages'

export const router = createBrowserRouter([
  {
    path: '/',
    Component: AppLayout,
    children: [
      { index: true, Component: ChatPage },
      { path: 'c/:conversationId', Component: ChatPage },
      { path: 'executions', element: <Navigate to="/" replace /> },
      { path: 'executions/:executionId', element: <Navigate to="/" replace /> },
      { path: '*', Component: NotFoundPage },
    ],
  },
  {
    path: '*',
    Component: NotFoundPage,
  },
])
