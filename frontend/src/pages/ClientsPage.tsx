import AddIcon from '@mui/icons-material/Add'
import BusinessIcon from '@mui/icons-material/Business'
import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useEffect, useState } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router'
import { FeedbackAlerts, PageContainer, PageHeader, ResourceDialog } from '../components/ui'
import { createClient, listClients } from '../services'
import type { ClientSummary } from '../types'
import { getApiErrorMessage } from '../utils/apiError'

export function ClientsPage() {
  const navigate = useNavigate()
  const [clients, setClients] = useState<ClientSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [newClientName, setNewClientName] = useState('')
  const [newClientProduct, setNewClientProduct] = useState('')

  async function load() {
    setLoading(true)
    try {
      const response = await listClients()
      setClients(response.clients)
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

  function openCreateDialog() {
    setNewClientName('')
    setNewClientProduct('')
    setCreateDialogOpen(true)
  }

  async function handleCreate() {
    const name = newClientName.trim()
    const product = newClientProduct.trim()
    if (!name || !product) {
      return
    }

    setCreating(true)
    try {
      const client = await createClient({ name, product })
      setCreateDialogOpen(false)
      navigate(`/clients/${client.id}`)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setCreating(false)
    }
  }

  return (
    <PageContainer>
      <PageHeader
        title="Clientes"
        description="Cadastre clientes, arquivos, links e prompts para o agente de marketing."
        actions={
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={openCreateDialog}
            disabled={creating}
          >
            Novo cliente
          </Button>
        }
      />

      <Box sx={{ mt: 3 }}>
        <FeedbackAlerts error={error} onDismissError={() => setError(null)} />
      </Box>

      {loading ? (
        <Stack sx={{ alignItems: 'center', py: 6 }}>
          <CircularProgress size={28} />
        </Stack>
      ) : clients.length === 0 ? (
        <Typography color="text.secondary" sx={{ mt: 3 }}>
          Nenhum cliente cadastrado ainda.
        </Typography>
      ) : (
        <Stack spacing={1.5} sx={{ mt: 3 }}>
          {clients.map((client) => (
            <Card key={client.id} variant="outlined">
              <CardActionArea component={RouterLink} to={`/clients/${client.id}`}>
                <CardContent sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                  <BusinessIcon color="action" sx={{ mt: 0.25 }} />
                  <Stack spacing={0.5} sx={{ flex: 1, minWidth: 0 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {client.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {client.product} · {client.resource_count} recursos
                    </Typography>
                    {client.description ? (
                      <Typography variant="body2" noWrap title={client.description}>
                        {client.description}
                      </Typography>
                    ) : null}
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Stack>
      )}

      <ResourceDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        title="Novo cliente"
        submitLabel="Criar cliente"
        loading={creating}
        disableSubmit={!newClientName.trim() || !newClientProduct.trim()}
        onSubmit={() => void handleCreate()}
      >
        <TextField
          label="Nome"
          value={newClientName}
          onChange={(e) => {
            const name = e.target.value
            setNewClientName(name)
            if (!newClientProduct.trim()) {
              setNewClientProduct(name)
            }
          }}
          fullWidth
          required
          autoFocus
        />
        <TextField
          label="Produto"
          value={newClientProduct}
          onChange={(e) => setNewClientProduct(e.target.value)}
          fullWidth
          required
        />
      </ResourceDialog>
    </PageContainer>
  )
}
