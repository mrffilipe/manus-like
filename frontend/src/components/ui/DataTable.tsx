import type { ReactNode } from 'react'
import { Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material'
import { EmptyState } from './EmptyState'

interface DataTableColumn {
  id: string
  label: string
  align?: 'left' | 'right' | 'center'
  minWidth?: number
}

interface DataTableProps {
  columns: DataTableColumn[]
  rows: ReactNode[]
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  skeletonRows?: number
}

export function DataTable({
  columns,
  rows,
  loading = false,
  emptyTitle,
  emptyDescription,
  skeletonRows = 4,
}: DataTableProps) {
  if (loading) {
    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column.id} align={column.align}>
                  {column.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {Array.from({ length: skeletonRows }).map((_, index) => (
              <TableRow key={index}>
                {columns.map((column) => (
                  <TableCell key={column.id}>
                    <Skeleton variant="text" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  if (rows.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />
  }

  return (
    <TableContainer sx={{ overflowX: 'auto' }}>
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            {columns.map((column) => (
              <TableCell key={column.id} align={column.align} sx={{ minWidth: column.minWidth }}>
                {column.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>{rows}</TableBody>
      </Table>
    </TableContainer>
  )
}
