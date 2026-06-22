import { Box, type BoxProps } from '@mui/material'
import { useCallback, useEffect, useRef, useState } from 'react'
import { ghostScrollbarSx, SCROLLBAR_HIDE_MS } from '../../theme/ghostScrollbar'

interface GhostScrollBoxProps extends BoxProps {
  children: React.ReactNode
}

export function GhostScrollBox({ children, sx, ...props }: GhostScrollBoxProps) {
  const [scrollActive, setScrollActive] = useState(false)
  const timeoutRef = useRef<number | undefined>(undefined)

  const activateScrollbar = useCallback(() => {
    setScrollActive(true)
    if (timeoutRef.current !== undefined) {
      window.clearTimeout(timeoutRef.current)
    }
    timeoutRef.current = window.setTimeout(() => {
      setScrollActive(false)
    }, SCROLLBAR_HIDE_MS)
  }, [])

  useEffect(() => {
    return () => {
      if (timeoutRef.current !== undefined) {
        window.clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return (
    <Box
      {...props}
      onMouseMove={activateScrollbar}
      onScroll={activateScrollbar}
      sx={[ghostScrollbarSx(scrollActive), ...(Array.isArray(sx) ? sx : sx ? [sx] : [])]}
    >
      {children}
    </Box>
  )
}
