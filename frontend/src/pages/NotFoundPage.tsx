import { Button, Stack, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router'
import { PageHeader, SectionCard } from '../components/ui'

export function NotFoundPage() {
  return (
    <Stack spacing={3}>
      <PageHeader title="Page not found" description="The page you requested does not exist." />
      <SectionCard>
        <Stack spacing={2}>
          <Typography variant="body1" color="text.secondary">
            Check the URL or return to the dashboard.
          </Typography>
          <Button component={RouterLink} to="/" variant="contained">
            Go to dashboard
          </Button>
        </Stack>
      </SectionCard>
    </Stack>
  )
}
