export const ACCEPTED_FILE_EXTENSIONS = [
  '.txt',
  '.md',
  '.csv',
  '.tsv',
  '.pdf',
  '.xlsx',
  '.xls',
  '.json',
  '.xml',
  '.html',
  '.htm',
  '.yaml',
  '.yml',
  '.log',
  '.js',
  '.ts',
  '.jsx',
  '.tsx',
  '.py',
  '.css',
  '.docx',
] as const

export const ACCEPTED_FILE_TYPES = ACCEPTED_FILE_EXTENSIONS.join(',')

export function getFileExtension(filename: string): string {
  const dot = filename.lastIndexOf('.')
  if (dot === -1) {
    return ''
  }
  return filename.slice(dot).toLowerCase()
}
