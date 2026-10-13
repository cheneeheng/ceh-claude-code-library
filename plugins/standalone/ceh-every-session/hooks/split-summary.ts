export type Section = { number?: string; topic: string; body: string; after: string }

const isTableRow = (line: string) => line.trimStart().startsWith('|')
const isSeparator = (line: string) => /^\s*\|[\s:|-]+\|\s*$/.test(line)

// A reply that opens with a summary table, split into the table and one
// section per bold Topic line below it. One paragraph before the table, which
// the style forbids but the model sometimes writes, is kept as `lead`. Null
// when the reply opens with no table or has nothing below it, so the caller
// draws the reply whole.
export const split = (text: string): { lead: string; table: string; sections: Section[] } | null => {
  const all = text.trimStart().split('\n')
  const start = all.findIndex((line, at) => isTableRow(line) && isSeparator(all[at + 1] ?? ''))
  if (start === -1) return null
  const lead = all.slice(0, start).join('\n').trim()
  if (/\n\s*\n/.test(lead)) return null

  const lines = all.slice(start)
  const end = lines.findIndex(line => !isTableRow(line))
  if (end === -1) return null

  // Topic cell -> "#" cell, so a section's button shows its row number.
  const rowNumber = new Map<string, string>()
  for (const row of lines.slice(2, end)) {
    const cells = row.split('|').map(cell => cell.trim())
    if (cells[1] && cells[2]) rowNumber.set(cells[2], cells[1])
  }

  // A section's body is everything from its Topic to the next Topic, tables and
  // code blocks included. A `---` line, the style's marker for closing text,
  // ends the body: what follows it up to the next Topic is `after`, drawn as is
  // outside the fold. Text before the first Topic folds under "Details".
  const sections: Section[] = []
  let current: Section | undefined
  let isClosed = false
  let inFence = false
  for (const line of lines.slice(end)) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    const topic = inFence ? undefined : /^\*\*(.+)\*\*\s*$/.exec(line)?.[1]
    if (topic !== undefined) {
      current = { number: rowNumber.get(topic), topic, body: '', after: '' }
      sections.push(current)
      isClosed = false
      continue
    }
    if (!inFence && /^\s*---+\s*$/.test(line)) {
      isClosed = true
      continue
    }
    if (!current) {
      if (!line.trim()) continue
      current = { topic: 'Details', body: '', after: '' }
      sections.push(current)
    }

    if (isClosed) current.after += `${line}\n`
    else current.body += `${line}\n`
  }
  if (sections.length === 0) return null

  return { lead, table: lines.slice(0, end).join('\n'), sections }
}
