import { Box, type BoxProps } from '@mui/material'
import type { PropsWithChildren } from 'react'
import { layout } from '../../theme/tokens'

interface PageContainerProps extends PropsWithChildren, Pick<BoxProps, 'sx'> {}

export function PageContainer({ children, sx }: PageContainerProps) {
  return (
    <Box
      sx={[
        {
          maxWidth: layout.pageMaxWidth,
          mx: 'auto',
          px: { xs: 2, sm: 3 },
          py: 3,
          width: '100%',
        },
        ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
      ]}
    >
      {children}
    </Box>
  )
}
