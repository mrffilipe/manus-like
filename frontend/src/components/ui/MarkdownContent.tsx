import {
  Box,
  Link,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  useTheme,
} from '@mui/material'
import type { Components } from 'react-markdown'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MarkdownContentProps {
  content: string
}

export function MarkdownContent({ content }: MarkdownContentProps) {
  const theme = useTheme()

  const components: Components = {
    h1: ({ children }) => (
      <Typography variant="h4" component="h1" sx={{ mt: 2, mb: 1.25, fontWeight: 700, letterSpacing: '-0.02em' }}>
        {children}
      </Typography>
    ),
    h2: ({ children }) => (
      <Typography variant="h5" component="h2" sx={{ mt: 1.75, mb: 1.25, fontWeight: 700, letterSpacing: '-0.02em' }}>
        {children}
      </Typography>
    ),
    h3: ({ children }) => (
      <Typography variant="h6" component="h3" sx={{ mt: 1.5, mb: 0.75, fontWeight: 600, letterSpacing: '-0.01em' }}>
        {children}
      </Typography>
    ),
    h4: ({ children }) => (
      <Typography variant="subtitle1" component="h4" sx={{ mt: 1.25, mb: 0.75, fontWeight: 600 }}>
        {children}
      </Typography>
    ),
    p: ({ children }) => (
      <Typography variant="body1" component="p" sx={{ mb: 1.25, lineHeight: 1.75, fontSize: '0.9375rem' }}>
        {children}
      </Typography>
    ),
    ul: ({ children }) => (
      <Box component="ul" sx={{ pl: 3, mb: 1.5, '& li': { mb: 0.5 } }}>
        {children}
      </Box>
    ),
    ol: ({ children }) => (
      <Box component="ol" sx={{ pl: 3, mb: 1.5, '& li': { mb: 0.5 } }}>
        {children}
      </Box>
    ),
    li: ({ children }) => (
      <Typography component="li" variant="body1" sx={{ lineHeight: 1.75, fontSize: '0.9375rem' }}>
        {children}
      </Typography>
    ),
    a: ({ href, children }) => (
      <Link href={href} target="_blank" rel="noopener noreferrer" underline="hover">
        {children}
      </Link>
    ),
    strong: ({ children }) => (
      <Box component="strong" sx={{ fontWeight: 700 }}>
        {children}
      </Box>
    ),
    em: ({ children }) => (
      <Box component="em" sx={{ fontStyle: 'italic' }}>
        {children}
      </Box>
    ),
    blockquote: ({ children }) => (
      <Box
        component="blockquote"
        sx={{
          borderLeft: 3,
          borderColor: 'primary.main',
          pl: 2,
          py: 0.5,
          my: 1.5,
          color: 'text.secondary',
        }}
      >
        {children}
      </Box>
    ),
    hr: () => (
      <Box
        component="hr"
        sx={{
          border: 0,
          borderTop: 1,
          borderColor: 'divider',
          my: 2,
        }}
      />
    ),
    pre: ({ children }) => (
      <Box
        component="pre"
        sx={{
          bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
          border: 1,
          borderColor: 'divider',
          borderRadius: 1,
          p: 1.5,
          mb: 1.5,
          overflowX: 'auto',
          fontFamily: 'monospace',
          fontSize: '0.875rem',
        }}
      >
        {children}
      </Box>
    ),
    code: ({ className, children }) => {
      if (className) {
        return <code className={className}>{children}</code>
      }
      return (
        <Box
          component="code"
          sx={{
            bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100',
            px: 0.75,
            py: 0.25,
            borderRadius: 0.5,
            fontFamily: 'monospace',
            fontSize: '0.875em',
          }}
        >
          {children}
        </Box>
      )
    },
    table: ({ children }) => (
      <TableContainer sx={{ mb: 2, border: 1, borderColor: 'divider', borderRadius: 1 }}>
        <Table size="small">{children}</Table>
      </TableContainer>
    ),
    thead: ({ children }) => <TableHead>{children}</TableHead>,
    tbody: ({ children }) => <TableBody>{children}</TableBody>,
    tr: ({ children }) => <TableRow>{children}</TableRow>,
    th: ({ children }) => (
      <TableCell sx={{ fontWeight: 700, bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50' }}>
        {children}
      </TableCell>
    ),
    td: ({ children }) => <TableCell>{children}</TableCell>,
  }

  return (
    <Box
      sx={{
        '& > :first-of-type': { mt: 0 },
        '& > :last-child': { mb: 0 },
      }}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </Box>
  )
}
