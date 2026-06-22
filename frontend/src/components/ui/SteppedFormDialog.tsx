import { Button, Dialog, DialogContent, DialogTitle, Stack, Typography, type DialogProps } from '@mui/material'
import type { FormEvent, PropsWithChildren, ReactNode } from 'react'
import { FormStepper } from './FormStepper'
import { BackButton } from './BackButton'
import { FormActions } from './FormActions'
import { formSpacing } from '../../theme/tokens'

interface SteppedFormDialogProps extends PropsWithChildren {
  open: boolean
  onClose: () => void
  title: string
  description?: string
  steps: readonly string[]
  activeStep: number
  maxWidth?: DialogProps['maxWidth']
  loading?: boolean
  submitLabel?: string
  onBack: () => void
  onNext: () => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void | Promise<void>
  disableNext?: boolean
  disableSubmit?: boolean
  footer?: ReactNode
}

export function SteppedFormDialog({
  open,
  onClose,
  title,
  description,
  steps,
  activeStep,
  maxWidth = 'sm',
  loading = false,
  submitLabel = 'Concluir',
  onBack,
  onNext,
  onSubmit,
  disableNext = false,
  disableSubmit = false,
  footer,
  children,
}: SteppedFormDialogProps) {
  const isFirstStep = activeStep === 0
  const isLastStep = activeStep === steps.length - 1

  function handleSubmit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    if (!isLastStep) {
      onNext()
      return
    }
    void onSubmit(event)
  }

  function handleBack(): void {
    if (isFirstStep) {
      onClose()
      return
    }
    onBack()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth={maxWidth} fullWidth scroll="paper">
      <DialogTitle sx={{ pb: description ? 0.5 : 1 }}>{title}</DialogTitle>
      {description ? (
        <Typography variant="body2" color="text.secondary" sx={{ px: 3, pb: 1 }}>
          {description}
        </Typography>
      ) : null}
      <DialogContent dividers>
        <Stack component="form" spacing={formSpacing.stack} onSubmit={handleSubmit}>
          <FormStepper steps={steps} activeStep={activeStep} />
          {children}
          {footer ?? (
            <FormActions>
              <BackButton disabled={loading} onClick={handleBack}>
                {isFirstStep ? 'Cancelar' : 'Voltar'}
              </BackButton>
              {isLastStep ? (
                <Button type="submit" color="primary" size="large" disabled={disableSubmit || loading} sx={{ py: 1.25, px: 3 }}>
                  {loading ? 'Salvando...' : submitLabel}
                </Button>
              ) : (
                <Button type="submit" color="primary" size="large" disabled={disableNext || loading} sx={{ py: 1.25, px: 3 }}>
                  Continuar
                </Button>
              )}
            </FormActions>
          )}
        </Stack>
      </DialogContent>
    </Dialog>
  )
}
