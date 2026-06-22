import { Button, CircularProgress, FormControlLabel, Radio, RadioGroup, Stack, TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { Link as RouterLink, useParams } from 'react-router'
import { ActivityPreviewPanel } from '../components/activity'
import {
  ConfirmDialog,
  FeedbackAlerts,
  FormActions,
  MarkdownContent,
  PageHeader,
  SectionCard,
  StaticField,
  StatusChip,
} from '../components/ui'
import { useExecutionActivity } from '../hooks/useExecutionActivity'
import { continueExecution, getExecutionStatus, resumeExecution } from '../services'
import type { AgentStatusResponse } from '../types'
import { getApiErrorMessage } from '../utils/apiError'
import { executionStatusLabel, executionStatusVariant, executionStepLabel } from '../utils/enumLabels'
import { getStoredExecution, saveStoredExecution, updateStoredExecutionStatus } from '../utils/executionStorage'

const TERMINAL_STATUSES = new Set(['Completed', 'Failed'])

export function ExecutionPage() {
  const { executionId = '' } = useParams()
  const [status, setStatus] = useState<AgentStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [answer, setAnswer] = useState('')
  const [selectedOption, setSelectedOption] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [resumeOpen, setResumeOpen] = useState(false)

  useEffect(() => {
    if (!executionId) {
      return
    }

    let cancelled = false
    let intervalId: number | undefined

    async function fetchStatus() {
      try {
        const response = await getExecutionStatus(executionId)
        if (cancelled) {
          return
        }
        setStatus(response)
        updateStoredExecutionStatus(executionId, response.status)
        setError(null)

        if (TERMINAL_STATUSES.has(response.status) && intervalId !== undefined) {
          window.clearInterval(intervalId)
        }
      } catch (err) {
        if (!cancelled) {
          setError(getApiErrorMessage(err))
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void fetchStatus()
    intervalId = window.setInterval(() => {
      void fetchStatus()
    }, 2000)

    return () => {
      cancelled = true
      if (intervalId !== undefined) {
        window.clearInterval(intervalId)
      }
    }
  }, [executionId])

  async function handleContinue() {
    const finalAnswer = status?.options?.length ? selectedOption : answer.trim()
    if (!finalAnswer) {
      setError('Please provide an answer before continuing.')
      return
    }

    setSubmitting(true)
    setError(null)
    setSuccess(null)

    try {
      await continueExecution(executionId, finalAnswer)
      setAnswer('')
      setSelectedOption('')
      setSuccess('Answer submitted. The agent will resume shortly.')
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleResume() {
    setSubmitting(true)
    setError(null)
    setSuccess(null)

    try {
      await resumeExecution(executionId)
      setSuccess('Execution resume requested.')
      setResumeOpen(false)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  useEffect(() => {
    if (status && !getStoredExecution(executionId)) {
      saveStoredExecution({
        execution_id: status.execution_id,
        goal: status.goal,
        status: status.status,
        created_at: new Date().toISOString(),
      })
    }
  }, [executionId, status])

  const { activities, loading: activityLoading, connected } = useExecutionActivity(
    executionId,
    status?.status ?? null,
  )

  const showActivityPanel = status?.status === 'Running' || activities.length > 0

  return (
    <Stack spacing={3}>
      <Button component={RouterLink} to="/executions" variant="text" color="inherit" sx={{ alignSelf: 'flex-start', color: 'text.secondary' }}>
        Back to executions
      </Button>

      <PageHeader
        title="Execution details"
        description="Monitor agent progress, provide human input, or resume after interruptions."
        actions={
          <Button variant="outlined" onClick={() => setResumeOpen(true)} disabled={submitting}>
            Resume
          </Button>
        }
      />

      <FeedbackAlerts
        error={error}
        success={success}
        onDismissError={() => setError(null)}
        onDismissSuccess={() => setSuccess(null)}
      />

      <SectionCard title="Status">
        {loading && !status ? (
          <Stack sx={{ alignItems: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Stack>
        ) : null}
        {status ? (
          <Stack spacing={2}>
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
              <StatusChip
                label={executionStatusLabel(status.status)}
                variant={executionStatusVariant(status.status)}
              />
              <Typography variant="body2" color="text.secondary">
                {status.execution_id}
              </Typography>
            </Stack>
            <StaticField label="Goal" value={status.goal} />
            <StaticField label="Current step" value={executionStepLabel(status.current_step)} />
            {status.error_message ? (
              <StaticField label="Error" value={status.error_message} />
            ) : null}
          </Stack>
        ) : null}
      </SectionCard>

      <ActivityPreviewPanel
        activities={activities}
        loading={activityLoading}
        connected={connected}
        show={showActivityPanel}
      />

      {status?.result ? (
        <SectionCard title="Result">
          <MarkdownContent content={status.result} />
        </SectionCard>
      ) : null}

      {status?.status === 'WaitingHumanInput' ? (
        <SectionCard title="Human input required">
          <Stack spacing={2}>
            <Typography variant="body1">{status.question}</Typography>
            {status.options?.length ? (
              <RadioGroup value={selectedOption} onChange={(event) => setSelectedOption(event.target.value)}>
                {status.options.map((option) => (
                  <FormControlLabel key={option} value={option} control={<Radio />} label={option} />
                ))}
              </RadioGroup>
            ) : (
              <TextField
                label="Your answer"
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                multiline
                minRows={2}
                fullWidth
              />
            )}
            <FormActions>
              <Button variant="contained" onClick={handleContinue} disabled={submitting}>
                {submitting ? 'Submitting…' : 'Continue execution'}
              </Button>
            </FormActions>
          </Stack>
        </SectionCard>
      ) : null}

      <ConfirmDialog
        open={resumeOpen}
        title="Resume execution"
        message="This will re-enqueue the execution. Use it after a worker restart or interruption."
        confirmLabel="Resume"
        onConfirm={handleResume}
        onClose={() => setResumeOpen(false)}
        loading={submitting}
      />
    </Stack>
  )
}
