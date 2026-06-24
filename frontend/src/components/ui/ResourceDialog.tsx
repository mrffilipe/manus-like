import {
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from '@mui/material'
import type { FormEvent, PropsWithChildren, ReactNode } from 'react'
import { BackButton } from './BackButton'
import { FormActions } from './FormActions'
import { formSpacing } from '../../theme/tokens'
import { standardDialogProps } from '../../theme/dialogStyles'

interface ResourceDialogProps extends PropsWithChildren {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  loading?: boolean
  submitLabel?: string
  cancelLabel?: string
  onSubmit: (event: FormEvent<HTMLFormElement>) => void | Promise<void>
  disableSubmit?: boolean
  footer?: ReactNode
}

export function ResourceDialog({
  open,
  onClose,
  title,
  description,
  loading = false,
  submitLabel = 'Salvar',
  cancelLabel = 'Cancelar',
  onSubmit,
  disableSubmit = false,
  footer,
  children,
}: ResourceDialogProps) {
  return (
    <Dialog open={open} onClose={onClose} {...standardDialogProps}>
      <DialogTitle sx={{ pb: description ? 0.5 : 1 }}>{title}</DialogTitle>
      {description ? (
        <Typography variant="body2" color="text.secondary" sx={{ px: 3, pb: 1 }}>
          {description}
        </Typography>
      ) : null}
      <DialogContent dividers>
        <Stack
          component="form"
          spacing={formSpacing.stack}
          onSubmit={(event) => {
            event.preventDefault()
            void onSubmit(event)
          }}
        >
          {children}
          {footer ?? (
            <FormActions>
              <BackButton disabled={loading} onClick={onClose}>
                {cancelLabel}
              </BackButton>
              <Button type="submit" color="primary" size="large" disabled={disableSubmit || loading} sx={{ py: 1.25, px: 3 }}>
                {loading ? 'Salvando...' : submitLabel}
              </Button>
            </FormActions>
          )}
        </Stack>
      </DialogContent>
    </Dialog>
  )
}
