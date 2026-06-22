import { Alert, Stack } from '@mui/material'

interface FeedbackAlertsProps {
  success?: string | null
  error?: string | null
  info?: string | null
  onDismissSuccess?: () => void
  onDismissError?: () => void
}

export function FeedbackAlerts({
  success,
  error,
  info,
  onDismissSuccess,
  onDismissError,
}: FeedbackAlertsProps) {
  if (!success && !error && !info) {
    return null
  }

  return (
    <Stack spacing={1.5}>
      {success ? (
        <Alert severity="success" onClose={onDismissSuccess}>
          {success}
        </Alert>
      ) : null}
      {error ? (
        <Alert severity="error" onClose={onDismissError}>
          {error}
        </Alert>
      ) : null}
      {info ? <Alert severity="info">{info}</Alert> : null}
    </Stack>
  )
}
