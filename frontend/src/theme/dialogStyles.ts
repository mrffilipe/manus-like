import type { DialogProps } from '@mui/material'
import { layout } from './tokens'

export const standardDialogProps: Pick<DialogProps, 'maxWidth' | 'fullWidth' | 'scroll' | 'slotProps'> = {
  maxWidth: false,
  fullWidth: true,
  scroll: 'paper',
  slotProps: {
    paper: {
      sx: {
        maxWidth: layout.dialogMaxWidth,
        width: '100%',
        mx: 2,
      },
    },
  },
}
