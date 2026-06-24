import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import {
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useEffect, useRef, useState } from 'react'
import { Link as RouterLink, useNavigate, useParams } from 'react-router'
import { RESOURCE_LABELS, ResourceCard } from '../components/clients/ResourceCard'
import { FeedbackAlerts, FormActions, PageContainer, PageHeader, ResourceDialog } from '../components/ui'
import { ACCEPTED_FILE_TYPES } from '../constants/acceptedFiles'
import {
  createResource,
  deleteClient,
  deleteResource,
  getClient,
  refreshResourceLink,
  updateClient,
  uploadResourceFile,
} from '../services'
import type { ClientDetail, ClientResource } from '../types'
import { getApiErrorMessage } from '../utils/apiError'

type ResourceType = 'link' | 'prompt' | 'text' | 'file'

export function ClientDetailPage() {
  const { clientId = '' } = useParams()
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [client, setClient] = useState<ClientDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [dialogOpen, setDialogOpen] = useState(false)
  const [resourceType, setResourceType] = useState<ResourceType>('link')
  const [title, setTitle] = useState('')
  const [category, setCategory] = useState('')
  const [content, setContent] = useState('')
  const [url, setUrl] = useState('')
  const [promptRole, setPromptRole] = useState('knowledge')
  const [pendingFile, setPendingFile] = useState<File | null>(null)

  async function load() {
    if (!clientId) {
      return
    }
    setLoading(true)
    try {
      const data = await getClient(clientId)
      setClient(data)
      setError(null)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [clientId])

  async function handleSaveProfile() {
    if (!client) {
      return
    }
    setSaving(true)
    try {
      const updated = await updateClient(client.id, {
        name: client.name,
        product: client.product,
        description: client.description,
      })
      setClient(updated)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  async function handleDeleteClient() {
    if (!client || !window.confirm(`Excluir cliente "${client.name}"?`)) {
      return
    }
    try {
      await deleteClient(client.id)
      navigate('/clients')
    } catch (err) {
      setError(getApiErrorMessage(err))
    }
  }

  function openAddDialog(type: ResourceType) {
    setResourceType(type)
    setTitle('')
    setCategory('')
    setContent('')
    setUrl('')
    setPromptRole('knowledge')
    setPendingFile(null)
    setDialogOpen(true)
  }

  async function handleCreateResource() {
    if (!client || !title.trim()) {
      return
    }
    setSaving(true)
    try {
      if (resourceType === 'file' && pendingFile) {
        await uploadResourceFile(client.id, pendingFile, title.trim(), category || undefined)
      } else if (resourceType !== 'file') {
        await createResource(client.id, {
          resource_type: resourceType,
          title: title.trim(),
          category: category || undefined,
          content: content || undefined,
          url: url || undefined,
          metadata: resourceType === 'prompt' ? { prompt_role: promptRole } : undefined,
        })
      }
      setDialogOpen(false)
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  async function handleDeleteResource(resource: ClientResource) {
    if (!client || !window.confirm(`Excluir "${resource.title}"?`)) {
      return
    }
    try {
      await deleteResource(client.id, resource.id)
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    }
  }

  async function handleRefreshLink(resource: ClientResource) {
    if (!client) {
      return
    }
    try {
      await refreshResourceLink(client.id, resource.id)
      await load()
    } catch (err) {
      setError(getApiErrorMessage(err))
    }
  }

  if (loading || !client) {
    return (
      <PageContainer>
        <Typography>{loading ? 'Carregando…' : 'Cliente não encontrado'}</Typography>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <Button component={RouterLink} to="/clients" startIcon={<ArrowBackIcon />} sx={{ mb: 2 }}>
        Voltar
      </Button>

      <FeedbackAlerts error={error} onDismissError={() => setError(null)} />

      <Stack spacing={2} sx={{ mt: 3, mb: 4 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {client.name}
        </Typography>
        <TextField
          label="Nome"
          value={client.name}
          onChange={(e) => setClient({ ...client, name: e.target.value })}
          fullWidth
        />
        <TextField
          label="Produto"
          value={client.product}
          onChange={(e) => setClient({ ...client, product: e.target.value })}
          fullWidth
        />
        <TextField
          label="Descrição"
          value={client.description}
          onChange={(e) => setClient({ ...client, description: e.target.value })}
          fullWidth
          multiline
          minRows={3}
        />
        <FormActions>
          <Button color="error" onClick={() => void handleDeleteClient()}>
            Excluir cliente
          </Button>
          <Button variant="contained" onClick={() => void handleSaveProfile()} disabled={saving}>
            Salvar perfil
          </Button>
        </FormActions>
      </Stack>

      <PageHeader
        title="Recursos"
        actions={
          <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }} useFlexGap>
            <Button size="small" variant="outlined" onClick={() => openAddDialog('link')}>
              + Link
            </Button>
            <Button size="small" variant="outlined" onClick={() => openAddDialog('prompt')}>
              + Prompt
            </Button>
            <Button size="small" variant="outlined" onClick={() => openAddDialog('text')}>
              + Texto
            </Button>
            <Button size="small" variant="outlined" onClick={() => openAddDialog('file')}>
              + Arquivo
            </Button>
          </Stack>
        }
      />

      <Stack spacing={1.5} sx={{ mt: 3 }}>
        {client.resources.length === 0 ? (
          <Typography color="text.secondary">Nenhum recurso cadastrado.</Typography>
        ) : (
          client.resources.map((resource) => (
            <ResourceCard
              key={resource.id}
              resource={resource}
              onRefresh={
                resource.resource_type === 'link'
                  ? () => void handleRefreshLink(resource)
                  : undefined
              }
              onDelete={() => void handleDeleteResource(resource)}
            />
          ))
        )}
      </Stack>

      <ResourceDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        title={`Adicionar ${RESOURCE_LABELS[resourceType]}`}
        submitLabel="Adicionar"
        loading={saving}
        disableSubmit={!title.trim() || (resourceType === 'file' && !pendingFile)}
        onSubmit={() => void handleCreateResource()}
      >
        <TextField label="Título" value={title} onChange={(e) => setTitle(e.target.value)} fullWidth required />
        <TextField
          label="Categoria (opcional)"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          fullWidth
          placeholder="ex: atenção, LP, restrições"
        />
        {resourceType === 'link' ? (
          <TextField label="URL" value={url} onChange={(e) => setUrl(e.target.value)} fullWidth required />
        ) : null}
        {resourceType === 'prompt' ? (
          <>
            <FormControl fullWidth>
              <InputLabel>Papel do prompt</InputLabel>
              <Select
                label="Papel do prompt"
                value={promptRole}
                onChange={(e) => setPromptRole(e.target.value)}
              >
                <MenuItem value="knowledge">Base de conhecimento</MenuItem>
                <MenuItem value="instruction">Instrução</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Conteúdo do prompt"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              fullWidth
              multiline
              minRows={6}
            />
          </>
        ) : null}
        {resourceType === 'text' ? (
          <TextField
            label="Conteúdo"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            fullWidth
            multiline
            minRows={4}
          />
        ) : null}
        {resourceType === 'file' ? (
          <>
            <input
              ref={fileInputRef}
              type="file"
              hidden
              accept={ACCEPTED_FILE_TYPES}
              onChange={(e) => setPendingFile(e.target.files?.[0] ?? null)}
            />
            <Button variant="outlined" onClick={() => fileInputRef.current?.click()}>
              {pendingFile ? pendingFile.name : 'Escolher arquivo'}
            </Button>
          </>
        ) : null}
      </ResourceDialog>
    </PageContainer>
  )
}
