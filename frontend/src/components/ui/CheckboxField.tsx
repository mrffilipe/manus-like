import { Checkbox, FormControlLabel, type FormControlLabelProps } from '@mui/material'

type CheckboxFieldProps = Omit<FormControlLabelProps, 'control'> & {
  checked: boolean
  onCheckedChange: (checked: boolean) => void
  disabled?: boolean
}

export function CheckboxField({ checked, onCheckedChange, disabled, ...props }: CheckboxFieldProps) {
  return (
    <FormControlLabel
      {...props}
      control={
        <Checkbox checked={checked} disabled={disabled} onChange={(_, value) => onCheckedChange(value)} />
      }
    />
  )
}
