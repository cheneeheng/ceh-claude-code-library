import type { On } from 'claude-code'
import { expect, test } from 'claude-code/testing'

const REPLY = [
  '| #   | Topic  | Outcome    | Status |',
  '| --- | ------ | ---------- | ------ |',
  '| 1   | Alpha  | Did alpha. | done   |',
  '| 2   | Beta   | Did beta.  | done   |',
  '',
  '**Alpha**',
  '',
  '- alpha detail',
  '',
  '**Beta**',
  '',
  '- beta detail',
].join('\n')

const DECISIONS = [
  '**Decision: Which store?**',
  '',
  '1. Postgres (recommended)',
  '2. SQLite',
  '',
  '**Decision: Which port?**',
  '',
  '1. 8080',
  '2. 3000',
].join('\n')

const message = (text: string) => ({
  plugin: 'ceh-every-session',
  component: 'AssistantMessage' as const,
  requestId: 'reply-1',
  props: { text, isFirstOfReply: true },
})

const details = (args: string) => ({
  command: 'details',
  args,
  origin: { kind: 'composer' as const },
  presentation: { isFullscreen: false, columns: 120 },
})

// Stands for the engine's own drawing of a reply, beneath the plugin.
const engineDraws = (on: On) =>
  on('ui.render', { component: 'AssistantMessage' }, ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>{e.props.text}</Text>
  })

test('a reply with a summary table folds each topic behind its own button', async $ => {
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ surface, ...message(REPLY) })
    expect(await ui.find({ type: 'Markdown', text: /\| 1 +\| Alpha/ })).toBeDefined()
    expect(await ui.find({ text: /alpha detail/ })).toBeUndefined()
    expect((await ui.find({ key: 'reply-1#0' }))?.text).toMatch(/▸ 1 Alpha/)

    await ui.press({ key: 'reply-1#0' })
    expect(await ui.find({ text: /alpha detail/ })).toBeDefined()
    expect(await ui.find({ text: /beta detail/ })).toBeUndefined()

    await ui.press({ key: 'reply-1#0' })
    expect(await ui.find({ text: /alpha detail/ })).toBeUndefined()
    await ui.unmount()
  }
})

test('a lead-in line before the summary table shows as is, and the topics still fold', async $ => {
  const ui = await $.ui.mount({ surface: 'terminal', ...message(`I agree, with one caveat.\n\n${REPLY}`) })
  expect(await ui.find({ type: 'Markdown', text: /^I agree, with one caveat\.$/ })).toBeDefined()
  expect(await ui.find({ type: 'Markdown', text: /\| 1 +\| Alpha/ })).toBeDefined()
  expect(await ui.find({ text: /alpha detail/ })).toBeUndefined()
  expect((await ui.find({ key: 'reply-1#0' }))?.text).toMatch(/▸ 1 Alpha/)
  await ui.unmount()
})

test('a reply with two paragraphs before its first table is drawn whole by the engine', async ($, on) => {
  engineDraws(on)
  const ui = await $.ui.mount({ surface: 'terminal', ...message(`First point.\n\nSecond point.\n\n${REPLY}`) })
  expect(await ui.find({ type: 'Button' })).toBeUndefined()
  await ui.unmount()
})

test('closing text below a --- line shows open in its own Notes box, outside its fold', async $ => {
  const reply = `${REPLY}\n\nA beta note.\n  continued beta line\n\n---\n\nDo you want me to go on?\n\nTests: 3 of 3 pass.`
  const ui = await $.ui.mount({ surface: 'terminal', ...message(reply) })
  expect((await ui.find({ key: 'reply-1#1a' }))?.text).toMatch(/^Notes\s*Do you want me to go on\?\s+Tests: 3 of 3 pass\./)
  expect(await ui.find({ text: /continued beta line/ })).toBeUndefined()

  await ui.press({ key: 'reply-1#1' })
  const beta = await ui.find({ type: 'Markdown', text: /beta detail/ })
  expect(beta?.text).toMatch(/continued beta line/)
  expect(beta?.text).not.toMatch(/Do you want/)
  await ui.unmount()
})

test('a code block and the bullets after it stay inside their fold', async $ => {
  const reply = REPLY.replace('- alpha detail', '```\ntree/\n  **leaf**\n```\n\n- alpha detail')
  const ui = await $.ui.mount({ surface: 'terminal', ...message(reply) })
  expect(await ui.find({ text: /alpha detail/ })).toBeUndefined()
  expect(await ui.find({ text: /tree\// })).toBeUndefined()

  await ui.press({ key: 'reply-1#0' })
  const alpha = await ui.find({ type: 'Markdown', text: /tree\// })
  expect(alpha?.text).toMatch(/\*\*leaf\*\*[\s\S]*alpha detail/)
  expect(await ui.find({ key: 'reply-1#1' })).toBeDefined()
  await ui.unmount()
})

test('paragraphs, tables, and bullets after them all stay inside their fold', async $ => {
  const body = 'Where they differ:\n\n| Run | Found |\n| --- | ----- |\n| a   | 6/6   |\n\n- after the table\n\nA last note.'
  const reply = REPLY.replace('- alpha detail', `- alpha detail\n\n${body}`)
  const ui = await $.ui.mount({ surface: 'terminal', ...message(reply) })
  expect(await ui.find({ text: /Where they differ|after the table|A last note/ })).toBeUndefined()

  await ui.press({ key: 'reply-1#0' })
  const alpha = await ui.find({ type: 'Markdown', text: /alpha detail/ })
  expect(alpha?.text).toMatch(/Where they differ[\s\S]*\| a +\| 6\/6[\s\S]*after the table[\s\S]*A last note/)
  await ui.unmount()
})

test('decision blocks become options, and a pick fills the prompt box with every pick', async ($, on) => {
  const filled: string[] = []
  on('prompt.fill', (_$, e) => {
    filled.push(e.text)
    return { isFilled: true }
  })
  const ui = await $.ui.mount({ surface: 'terminal', ...message(`${REPLY}\n\n${DECISIONS}`) })
  expect(await ui.find({ type: 'Text', text: 'Which store?' })).toBeDefined()
  expect(await ui.find({ key: 'reply-1#1' })).toBeDefined()

  await ui.press({ key: 'reply-1#d0o0' })
  expect(filled.at(-1)).toBe('Which store? Postgres')
  expect((await ui.find({ key: 'reply-1#d0o0' }))?.text).toMatch(/● 1\. Postgres/)

  await ui.press({ key: 'reply-1#d1o1' })
  expect(filled.at(-1)).toBe('Which store? Postgres\nWhich port? 3000')
  await ui.unmount()
})

test('a decision line in the middle of a reply stays text', async ($, on) => {
  engineDraws(on)
  const ui = await $.ui.mount({ surface: 'terminal', ...message(`Intro.\n\n${DECISIONS}\n\nMore text.`) })
  expect(await ui.find({ type: 'Button' })).toBeUndefined()
  await ui.unmount()
})

test('a reply with no summary table is drawn whole by the engine', async ($, on) => {
  engineDraws(on)
  const ui = await $.ui.mount({ surface: 'terminal', ...message('Just a short answer.') })
  expect(await ui.find({ type: 'Text', text: /Just a short answer/ })).toBeDefined()
  expect(await ui.find({ type: 'Button' })).toBeUndefined()
  await ui.unmount()
})

test('/details on shows every reply whole, /details off folds again', async ($, on) => {
  engineDraws(on)
  await $.command.run(details('on'))
  const shown = await $.ui.mount({ surface: 'terminal', ...message(REPLY) })
  expect(await shown.find({ type: 'Text', text: /beta detail/ })).toBeDefined()
  expect(await shown.find({ type: 'Button' })).toBeUndefined()
  await shown.unmount()

  await $.command.run(details('off'))
  const folded = await $.ui.mount({ surface: 'terminal', ...message(REPLY) })
  expect(await folded.find({ key: 'reply-1#1' })).toBeDefined()
  await folded.unmount()
})

test('the footer shows a folded replies mode while folding is on', async ($, on) => {
  on('ui.render', { component: 'SessionMode' }, ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>{e.props.modes.join(' & ')}</Text>
  })
  const footer = {
    plugin: 'ceh-every-session',
    component: 'SessionMode' as const,
    requestId: 'modes',
    props: { modes: ['focus'] },
  }

  const folded = await $.ui.mount({ surface: 'terminal', ...footer })
  expect(await folded.find({ type: 'Text', text: 'focus & folded replies (mod)' })).toBeDefined()
  await folded.unmount()

  await $.command.run(details('on'))
  const shown = await $.ui.mount({ surface: 'terminal', ...footer })
  expect(await shown.find({ type: 'Text', text: 'focus' })).toBeDefined()
  await shown.unmount()
})
