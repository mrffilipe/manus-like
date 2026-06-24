import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined'
import {
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useEffect, useState } from 'react'
import { FeedbackAlerts, PageContainer } from '../components/ui'
import { getSettings, resetSettings, updateSettings } from '../services'
import { getApiErrorMessage } from '../utils/apiError'

export function SettingsPage() {
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function load() {
    setLoading(true)
    try {
      const data = await getSettings()
      setPrompt(data.marketing_system_prompt)
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleSave() {
    setSaving(true)
    setSuccess(null)
    try {
      const data = await updateSettings({ marketing_system_prompt: prompt })
      setPrompt(data.marketing_system_prompt)
      setSuccess('Persona salva com sucesso.')
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  async function handleReset() {
    if (!window.confirm('Restaurar a persona padrão do sistema?')) {
      return
    }
    setSaving(true)
    setSuccess(null)
    try {
      const data = await resetSettings()
      setPrompt(data.marketing_system_prompt)
      setSuccess('Persona restaurada para o padrão.')
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageContainer>
      <Stack spacing={1} sx={{ mb: 3 }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <SettingsOutlinedIcon color="action" />
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Configurações do agente
          </Typography>
        </Stack>
        <Typography variant="body2" color="text.secondary">
          Define a persona global do consultor de marketing B2B. Vale para todas as conversas com cliente
          selecionado.
        </Typography>
      </Stack>

      <FeedbackAlerts
        error={error}
        success={success}
        onDismissError={() => setError(null)}
        onDismissSuccess={() => setSuccess(null)}
      />

      {loading ? (
        <Stack sx={{ alignItems: 'center', py: 6 }}>
          <CircularProgress size={28} />
        </Stack>
      ) : (
        <Stack spacing={2}>
          <TextField
            label="Persona do consultor (system prompt)"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            fullWidth
            multiline
            minRows={18}
            helperText="Mínimo 100 caracteres. Descreva identidade, comportamento, métricas e formato de entrega."
          />
          <Stack direction="row" spacing={1}>
            <Button variant="contained" onClick={() => void handleSave()} disabled={saving}>
              Salvar
            </Button>
            <Button variant="outlined" onClick={() => void handleReset()} disabled={saving}>
              Restaurar padrão
            </Button>
          </Stack>
        </Stack>
      )}
    </PageContainer>
  )
}
