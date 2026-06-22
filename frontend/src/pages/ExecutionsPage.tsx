import { Button, Stack, TableCell, TableRow } from '@mui/material'
import { useMemo } from 'react'
import { Link as RouterLink } from 'react-router'
import { DataTable, PageHeader, SectionCard, StatusChip } from '../components/ui'
import { executionStatusLabel, executionStatusVariant } from '../utils/enumLabels'
import { getStoredExecutions } from '../utils/executionStorage'

const columns = [
  { id: 'goal', label: 'Goal', minWidth: 280 },
  { id: 'status', label: 'Status', minWidth: 140 },
  { id: 'created', label: 'Created', minWidth: 180 },
  { id: 'actions', label: '', align: 'right' as const, minWidth: 100 },
]

export function ExecutionsPage() {
  const executions = useMemo(() => getStoredExecutions(), [])

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
        title="Executions"
        description="Browse agent executions stored in this browser."
        actions={
          <Button component={RouterLink} to="/" variant="contained">
            New task
          </Button>
        }
      />

      <SectionCard title="All executions">
        <DataTable
          columns={columns}
          rows={rows}
          emptyTitle="No executions stored"
          emptyDescription="Start a task from the dashboard to populate this list."
        />
      </SectionCard>
    </Stack>
  )
}
