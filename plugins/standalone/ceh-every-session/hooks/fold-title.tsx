import type { ClientModule, ClientSurface } from 'claude-code'

// A topic title in the terminal. A Button cannot be used here: the engine reads a
// second click within 500 ms and one cell as a word select and never presses, and
// a Button has no way to end that click chain. A Client holds the pointer from
// press to release, so nothing it draws can be selected.

type Props = { head: string; topic: string; isOpen: boolean }
type Pointer = { isHeld: boolean; isHover: boolean; toggledAt: number }

// An accidental double click counts once. A deliberate second click takes longer.
const REPRESS_MS = 200

// One line of title as `Text` spans, since neither a Button nor a Client takes
// Markdown: each `code` span in the color a reply draws inline code in. An unpaired
// backtick leaves the line as written.
export const inline = (Text: ClientSurface['elements']['Text'], line: string) => {
  const parts = line.split('`')
  return parts.length % 2 === 0
    ? line
    : parts.map((part, at) => (at % 2 ? <Text color="permission">{part}</Text> : part))
}

const FoldTitle: ClientModule<Props, Pointer> = ({ head, topic, isOpen }, surface) => {
  const { Text } = surface.elements
  const pointer = surface.state ?? { isHeld: false, isHover: false, toggledAt: 0 }
  if (!surface.state) surface.setState(pointer)

  surface.onPointer(e => {
    if (e.type === 'enter' || e.type === 'leave') {
      pointer.isHover = e.type === 'enter'
      surface.setState(pointer)
    }
    if (e.type === 'down' && e.button === 'left') pointer.isHeld = true
    if (e.type !== 'up' || !pointer.isHeld) return

    pointer.isHeld = false
    const isOver = e.x >= 0 && e.x < surface.columns && e.y >= 0 && e.y < surface.rows
    const now = Date.now()
    if (isOver && now - pointer.toggledAt >= REPRESS_MS) {
      pointer.toggledAt = now
      surface.post('toggle')
    }
  })

  return (
    <Text inverse={pointer.isHover}>
      <Text dimColor>{isOpen ? '▾' : '▸'}</Text> {head}
      <Text bold={isOpen}>{inline(Text, topic)}</Text>
    </Text>
  )
}

export default FoldTitle
