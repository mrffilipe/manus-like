import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
  type ButtonProps,
} from '@mui/material'
import { BackButton } from './BackButton'

interface ConfirmDialogProps {
  open: boolean
  onClose: () => void
  onConfirm: () => void | Promise<void>
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  confirmColor?: ButtonProps['color']
  loading?: boolean
}

export function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = 'Confirmar',
  cancelLabel = 'Cancelar',
  confirmColor = 'primary',
  loading = false,
}: ConfirmDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth scroll="paper">
      <DialogTitle>{title}</DialogTitle>
      <DialogContent dividers>
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2.5, pt: 0, gap: 1 }}>
        <BackButton disabled={loading} onClick={onClose}>
          {cancelLabel}
        </BackButton>
        <Button
          variant="contained"
          color={confirmColor}
          size="large"
          disabled={loading}
          onClick={() => void onConfirm()}
          sx={{ py: 1.25, px: 3 }}
        >
          {loading ? 'Aguarde…' : confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
