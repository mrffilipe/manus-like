import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined'
import {
  Box,
  Button,
  CircularProgress,
  FormControl,
  FormControlLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  Stack,
  Typography,
} from '@mui/material'
import { useEffect, useMemo, useState } from 'react'
import { useOutletContext, useParams } from 'react-router'
import type { AppLayoutOutletContext } from '../components/AppLayout'
import { ChatFooter, ChatThread } from '../components/chat'
import { FeedbackAlerts } from '../components/ui'
import { useChat } from '../hooks/useChat'
import { useExecutionActivity } from '../hooks/useExecutionActivity'
import { exportExecutionPdf, listClients } from '../services'
import type { ClientSummary } from '../types'
import { chat } from '../theme/tokens'
import { floatingSurfaceSx } from '../theme/chatStyles'

export function ChatPage() {
  const { conversationId } = useParams()
  const { refetchConversations } = useOutletContext<AppLayoutOutletContext>()
  const [selectedOption, setSelectedOption] = useState('')
  const [footerHeight, setFooterHeight] = useState(140)
  const [clients, setClients] = useState<ClientSummary[]>([])
  const [selectedClientId, setSelectedClientId] = useState<string>('')

  useEffect(() => {
    void listClients()
      .then((response) => setClients(response.clients))
      .catch(() => setClients([]))
  }, [])

  const isExistingConversation = Boolean(conversationId)
  const activeClientId = isExistingConversation ? null : selectedClientId || null

  const {
    messages,
    conversationClientId,
    loading,
    error,
    activeExecutionId,
    executionStatus,
    isRunning,
    isWaitingHumanInput,
    composerDisabled,
    sendMessage,
    continueWithAnswer,
    setError,
  } = useChat({
    conversationId,
    clientId: activeClientId,
    onConversationCreated: () => {
      void refetchConversations()
    },
    onMessagesUpdated: () => {
      void refetchConversations()
    },
  })

  const lockedClientId = conversationClientId ?? (isExistingConversation ? null : selectedClientId || null)
  const isNewConversation = !isExistingConversation && messages.length === 0
  const needsClientSelection = isNewConversation && clients.length > 0 && !selectedClientId
  const clientName = useMemo(() => {
    if (!lockedClientId) {
      return null
    }
    return clients.find((client) => client.id === lockedClientId)?.name ?? 'Cliente'
  }, [clients, lockedClientId])

  const { activities, loading: activityLoading, connected } = useExecutionActivity(
    activeExecutionId ?? '',
    executionStatus?.status ?? null,
    { enabled: Boolean(activeExecutionId) },
  )

  const showActivityTimeline = Boolean(activeExecutionId) && (isRunning || activities.length > 0)
  const hasMessages = messages.length > 0
  const pendingAssistantMessage =
    executionStatus?.status === 'Completed' &&
    executionStatus.result &&
    executionStatus.execution_id
      ? {
          executionId: executionStatus.execution_id,
          content: executionStatus.result,
        }
      : null

  async function handleExportPdf() {
    if (!executionStatus?.execution_id) {
      return
    }
    try {
      const blob = await exportExecutionPdf(executionStatus.execution_id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `relatorio-${executionStatus.execution_id}.pdf`
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao exportar PDF')
    }
  }

  async function handleContinueWithOption() {
    if (!selectedOption) {
      setError('Selecione uma opção antes de continuar.')
      return
    }

    await continueWithAnswer(selectedOption)
    setSelectedOption('')
  }

  function renderHumanInputOptions() {
    if (!executionStatus?.options?.length) {
      return null
    }

    return (
      <Box sx={{ maxWidth: chat.composerMaxWidth, mx: 'auto', width: '100%', px: { xs: 2, sm: 3 }, pb: 1 }}>
        <Stack spacing={2} sx={[{ px: 2, py: 2 }, floatingSurfaceSx(false)]}>
          <Typography variant="body2" color="text.secondary">
            O agente precisa da sua resposta
          </Typography>
          <RadioGroup
            value={selectedOption}
            onChange={(event) => setSelectedOption(event.target.value)}
          >
            {executionStatus.options.map((option) => (
              <FormControlLabel key={option} value={option} control={<Radio size="small" />} label={option} />
            ))}
          </RadioGroup>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              size="small"
              onClick={() => void handleContinueWithOption()}
              disabled={composerDisabled || !selectedOption}
              sx={{ borderRadius: 5, px: 2.5 }}
            >
              Continuar
            </Button>
          </Box>
        </Stack>
      </Box>
    )
  }

  function renderWelcomeClientSelector() {
    if (!isNewConversation || clients.length === 0) {
      return null
    }

    return (
      <Stack spacing={1.5} sx={{ width: '100%', maxWidth: 480, mt: 1 }}>
        {needsClientSelection ? (
          <Typography variant="body2" color="warning.main" sx={{ fontWeight: 500 }}>
            Selecione um cliente para continuar.
          </Typography>
        ) : null}
        <Stack
          direction="row"
          spacing={1.5}
          sx={[
            { alignItems: 'center', px: 2.5, py: 2, width: '100%', textAlign: 'left' },
            floatingSurfaceSx(false),
          ]}
        >
          <BusinessOutlinedIcon sx={{ fontSize: 20, color: 'text.secondary', flexShrink: 0 }} />
          <FormControl size="small" fullWidth>
            <Select
              value={selectedClientId}
              onChange={(event) => setSelectedClientId(event.target.value)}
              displayEmpty
              renderValue={(value) => {
                if (!value) {
                  return (
                    <Typography component="span" variant="body2" color="text.secondary">
                      Escolha um cliente
                    </Typography>
                  )
                }
                const client = clients.find((item) => item.id === value)
                return client ? `${client.name} — ${client.product}` : value
              }}
            >
              {clients.map((client) => (
                <MenuItem key={client.id} value={client.id}>
                  {client.name} — {client.product}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Stack>
      </Stack>
    )
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: { xs: 'calc(100vh - 52px)', md: '100vh' },
        width: '100%',
        position: 'relative',
      }}
    >
      <FeedbackAlerts error={error} onDismissError={() => setError(null)} />

      {loading ? (
        <Stack sx={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <CircularProgress size={28} />
        </Stack>
      ) : (
        <Box sx={{ position: 'relative', flex: 1, minHeight: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          {hasMessages ? (
            <ChatThread
              messages={messages}
              bottomPadding={footerHeight}
              pendingAssistantMessage={pendingAssistantMessage}
            />
          ) : (
            <Stack
              sx={{
                flex: 1,
                alignItems: 'center',
                justifyContent: 'center',
                px: 3,
                textAlign: 'center',
                maxWidth: chat.composerMaxWidth,
                mx: 'auto',
                width: '100%',
              }}
              spacing={1.5}
            >
              <Typography variant="h4" sx={{ fontWeight: 600, letterSpacing: '-0.02em' }}>
                Como posso ajudar?
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 480, lineHeight: 1.6 }}>
                Selecione um cliente para carregar contexto e materiais. Descreva a tarefa ou anexe
                relatórios e copies para o agente atuar como consultor.
              </Typography>
              {renderWelcomeClientSelector()}
            </Stack>
          )}

          {executionStatus?.status === 'Completed' && executionStatus.result ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', pb: 1 }}>
              <Button size="small" variant="outlined" onClick={() => void handleExportPdf()}>
                Exportar PDF
              </Button>
            </Box>
          ) : null}

          {isWaitingHumanInput && executionStatus?.options?.length ? (
            <Box sx={{ flexShrink: 0, pt: 2 }}>{renderHumanInputOptions()}</Box>
          ) : (
            <ChatFooter
              onSend={isWaitingHumanInput ? (text) => continueWithAnswer(text) : sendMessage}
              composerDisabled={composerDisabled || needsClientSelection}
              composerPlaceholder={
                isWaitingHumanInput
                  ? 'Responda ao agente…'
                  : needsClientSelection
                    ? 'Selecione um cliente acima para enviar mensagens…'
                    : selectedClientId || lockedClientId
                      ? 'Descreva a tarefa ou anexe relatórios…'
                      : undefined
              }
              showActivity={showActivityTimeline && hasMessages}
              activities={activities}
              activityLoading={activityLoading}
              connected={connected}
              isRunning={isRunning}
              overlay={hasMessages}
              onHeightChange={setFooterHeight}
              lockedClientName={!isNewConversation ? clientName : null}
            />
          )}
        </Box>
      )}
    </Box>
  )
}
