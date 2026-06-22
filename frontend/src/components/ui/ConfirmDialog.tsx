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
      <DialogTitle sx={{ pb: 1 }}>{title}</DialogTitle>
      <DialogContent sx={{ px: 3, pt: 0, pb: 2.5 }}>
        <Typography variant="body2" color="text.secondary">
          {message}
        </Typography>
      </DialogContent>
      <DialogActions
        sx={{
          px: 3,
          pt: 2.5,
          pb: 3,
          gap: 1.5,
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
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
