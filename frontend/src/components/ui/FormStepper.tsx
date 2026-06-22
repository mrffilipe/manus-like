import { Step, StepLabel, Stepper } from '@mui/material'

interface FormStepperProps {
  steps: readonly string[]
  activeStep: number
}

export function FormStepper({ steps, activeStep }: FormStepperProps) {
  return (
    <Stepper
      activeStep={activeStep}
      alternativeLabel
      sx={{
        px: 0,
        pt: 0,
        pb: 0.5,
        '& .MuiStepLabel-label': {
          typography: 'caption',
          mt: 0.5,
        },
        '& .MuiStepLabel-label.Mui-active': {
          fontWeight: 600,
        },
        '& .MuiStepIcon-root': {
          width: 28,
          height: 28,
        },
      }}
    >
      {steps.map((label) => (
        <Step key={label}>
          <StepLabel>{label}</StepLabel>
        </Step>
      ))}
    </Stepper>
  )
}
