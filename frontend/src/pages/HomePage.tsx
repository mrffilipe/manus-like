import { Button, Stack, TableCell, TableRow, TextField } from '@mui/material'
import { useState } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router'
import { FeedbackAlerts, PageHeader, SectionCard, DataTable, StatusChip } from '../components/ui'
import { runAgent } from '../services'
import type { StoredExecution } from '../types'
import { getApiErrorMessage } from '../utils/apiError'
import { executionStatusLabel, executionStatusVariant } from '../utils/enumLabels'
import { getStoredExecutions, saveStoredExecution } from '../utils/executionStorage'

const columns = [
  { id: 'goal', label: 'Goal', minWidth: 280 },
  { id: 'status', label: 'Status', minWidth: 140 },
  { id: 'created', label: 'Created', minWidth: 180 },
  { id: 'actions', label: '', align: 'right' as const, minWidth: 100 },
]

export function HomePage() {
  const navigate = useNavigate()
  const [goal, setGoal] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [executions, setExecutions] = useState<StoredExecution[]>(() => getStoredExecutions())

  async function handleRunAgent() {
    const trimmed = goal.trim()
    if (!trimmed) {
      setError('Please enter a goal for the agent.')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const response = await runAgent({ goal: trimmed })
      const stored: StoredExecution = {
        execution_id: response.execution_id,
        goal: trimmed,
        status: response.status,
        created_at: new Date().toISOString(),
      }
      saveStoredExecution(stored)
      setExecutions(getStoredExecutions())
      setGoal('')
      setSuccess('Agent execution started.')
      navigate(`/executions/${response.execution_id}`)
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const rows = executions.map((execution) => (
    <TableRow key={execution.execution_id} hover>
      <TableCell>{execution.goal}</TableCell>
      <TableCell>
        <StatusChip
          label={executionStatusLabel(execution.status)}
          variant={executionStatusVariant(execution.status)}
        />
      </TableCell>
      <TableCell>{new Date(execution.created_at).toLocaleString()}</TableCell>
      <TableCell align="right">
        <Button component={RouterLink} to={`/executions/${execution.execution_id}`} size="small">
          View
        </Button>
      </TableCell>
    </TableRow>
  ))

  return (
    <Stack spacing={3}>
      <PageHeader
        title="Dashboard"
        description="Start autonomous agent tasks and monitor recent executions."
      />

      <FeedbackAlerts error={error} success={success} onDismissError={() => setError(null)} onDismissSuccess={() => setSuccess(null)} />

      <SectionCard title="New agent task">
        <Stack spacing={2}>
          <TextField
            label="Goal"
            placeholder="Search for LangGraph documentation and summarize key features"
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
            multiline
            minRows={3}
            fullWidth
          />
          <Stack direction="row" sx={{ justifyContent: 'flex-end' }}>
            <Button variant="contained" onClick={handleRunAgent} disabled={loading}>
              {loading ? 'Starting…' : 'Run Agent'}
            </Button>
          </Stack>
        </Stack>
      </SectionCard>

      <SectionCard title="Recent executions">
        <DataTable
          columns={columns}
          rows={rows}
          emptyTitle="No executions yet"
          emptyDescription="Run your first agent task to see it listed here."
        />
      </SectionCard>
    </Stack>
  )
}
