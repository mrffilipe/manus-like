import {
  Box,
  Button,
  CircularProgress,
  FormControlLabel,
  Radio,
  RadioGroup,
  Stack,
  Typography,
} from '@mui/material'
import { useState } from 'react'
import { useOutletContext, useParams } from 'react-router'
import type { AppLayoutOutletContext } from '../components/AppLayout'
import { ChatFooter, ChatThread } from '../components/chat'
import { FeedbackAlerts } from '../components/ui'
import { useChat } from '../hooks/useChat'
import { useExecutionActivity } from '../hooks/useExecutionActivity'
import { chat } from '../theme/tokens'
import { floatingSurfaceSx } from '../theme/chatStyles'

export function ChatPage() {
  const { conversationId } = useParams()
  const { refetchConversations } = useOutletContext<AppLayoutOutletContext>()
  const [selectedOption, setSelectedOption] = useState('')
  const [footerHeight, setFooterHeight] = useState(140)

  const {
    messages,
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
    onConversationCreated: () => {
      void refetchConversations()
    },
    onMessagesUpdated: () => {
      void refetchConversations()
    },
  })

  const { activities, loading: activityLoading, connected } = useExecutionActivity(
    activeExecutionId ?? '',
    executionStatus?.status ?? null,
    { enabled: Boolean(activeExecutionId) },
  )

  const showActivityTimeline = Boolean(activeExecutionId) && (isRunning || activities.length > 0)
  const hasMessages = messages.length > 0

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
            <ChatThread messages={messages} bottomPadding={footerHeight} />
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
              }}
              spacing={1.5}
            >
              <Typography variant="h4" sx={{ fontWeight: 600, letterSpacing: '-0.02em' }}>
                Como posso ajudar?
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 420, lineHeight: 1.6 }}>
                Descreva uma tarefa e o agente executará pesquisa, navegação e análise para você.
              </Typography>
            </Stack>
          )}

          {isWaitingHumanInput && executionStatus?.options?.length ? (
            <Box sx={{ flexShrink: 0, pt: 2 }}>{renderHumanInputOptions()}</Box>
          ) : (
            <ChatFooter
              onSend={isWaitingHumanInput ? continueWithAnswer : sendMessage}
              composerDisabled={composerDisabled}
              composerPlaceholder={isWaitingHumanInput ? 'Responda ao agente…' : undefined}
              showActivity={showActivityTimeline && hasMessages}
              activities={activities}
              activityLoading={activityLoading}
              connected={connected}
              isRunning={isRunning}
              overlay={hasMessages}
              onHeightChange={setFooterHeight}
            />
          )}
        </Box>
      )}
    </Box>
  )
}
