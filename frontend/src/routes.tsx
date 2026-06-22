import { createBrowserRouter } from 'react-router'
import { AppLayout } from './components/AppLayout'
import { ExecutionPage, ExecutionsPage, HomePage, NotFoundPage } from './pages'

export const router = createBrowserRouter([
  {
    path: '/',
    Component: AppLayout,
    children: [
      { index: true, Component: HomePage },
      { path: 'executions', Component: ExecutionsPage },
      { path: 'executions/:executionId', Component: ExecutionPage },
      { path: '*', Component: NotFoundPage },
    ],
  },
  {
    path: '*',
    Component: NotFoundPage,
  },
])
