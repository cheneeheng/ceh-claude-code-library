export type Section = { number?: string; topic: string; body: string; after: string }

// A summary item: `1. **Topic** · *status*`, its outcome on indented lines below.
const ITEM = /^(\d+)\.\s+\*\*(.+?)\*\*\s+·/
const isRule = (line: string) => /^\s*---+\s*$/.test(line)

// A reply that opens with a summary list, split into the list and one section
// per bold Topic line below it. One paragraph before the list, which the style
// forbids but the model sometimes writes, is kept as `lead`. Null when the
// reply opens with no summary list or has nothing below it, so the caller
// draws the reply whole.
export const split = (text: string): { lead: string; summary: string; sections: Section[] } | null => {
  const all = text.trimStart().split('\n')
  const start = all.findIndex(line => ITEM.test(line))
  if (start === -1) return null
  const lead = all.slice(0, start).join('\n').trim()
  if (/\n\s*\n/.test(lead)) return null

  // The list runs over items, their indented outcome lines, and blank lines.
  const lines = all.slice(start)
  const end = lines.findIndex(line => line.trim() !== '' && !ITEM.test(line) && !/^\s/.test(line))
  if (end === -1) return null

  // Topic -> item number, so a section's button shows its number.
  const rowNumber = new Map<string, string>()
  for (const line of lines.slice(0, end)) {
    const [, number, topic] = ITEM.exec(line) ?? []
    if (number && topic) rowNumber.set(topic, number)
  }
  // The `---` right after the list separates it from the details, so it does
  // not start closing text the way a later `---` does.
  const below = isRule(lines[end] ?? '') ? end + 1 : end

  // A section's body is everything from its Topic to the next Topic, tables and
  // code blocks included. A `---` line, the style's marker for closing text,
  // ends the body: what follows it up to the next Topic is `after`, drawn as is
  // outside the fold. Text before the first Topic folds under "Details".
  const sections: Section[] = []
  let current: Section | undefined
  let isClosed = false
  let inFence = false
  for (const line of lines.slice(below)) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence
    const topic = inFence ? undefined : /^\*\*(.+)\*\*\s*$/.exec(line)?.[1]
    if (topic !== undefined) {
      current = { number: rowNumber.get(topic), topic, body: '', after: '' }
      sections.push(current)
      isClosed = false
      continue
    }
    if (!inFence && isRule(line)) {
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

  return { lead, summary: lines.slice(0, end).join('\n').trim(), sections }
}
