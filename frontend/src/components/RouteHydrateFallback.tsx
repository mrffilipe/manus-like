import { Box, CircularProgress, Typography } from '@mui/material'

export function RouteHydrateFallback() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
      }}
    >
      <CircularProgress size={36} />
      <Typography variant="body2" color="text.secondary">
        Carregando...
      </Typography>
    </Box>
  )
}
