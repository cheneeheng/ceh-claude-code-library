export type Decision = { question: string; options: string[] }

const QUESTION = /^\*\*Decision:\s*(.+?)\*\*\s*$/
const OPTION = /^\s*\d+[.)]\s+(.+)$/

// The decision blocks that close a reply, and the text before them. A block is
// a `**Decision: <question>**` line and a numbered list of two or more options.
// Only blocks with nothing but other blocks after them count, so a decision line
// in the middle of a reply stays text.
export const takeDecisions = (text: string): { rest: string; decisions: Decision[] } => {
  const lines = text.split('\n')
  for (let start = 0; start < lines.length; start++) {
    if (!QUESTION.test(lines[start] ?? '')) continue
    const decisions = parse(lines.slice(start))
    if (decisions) return { rest: lines.slice(0, start).join('\n'), decisions }
  }

  return { rest: text, decisions: [] }
}

const parse = (lines: string[]): Decision[] | null => {
  const decisions: Decision[] = []
  for (const line of lines) {
    const question = QUESTION.exec(line)?.[1]
    const option = OPTION.exec(line)?.[1]
    const current = decisions.at(-1)
    if (question !== undefined) decisions.push({ question, options: [] })
    else if (option !== undefined && current) current.options.push(option)
    else if (line.trim()) return null
  }

  return decisions.every(decision => decision.options.length >= 2) ? decisions : null
}
