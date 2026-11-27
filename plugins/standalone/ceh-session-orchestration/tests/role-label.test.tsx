import type { On } from 'claude-code'
import { expect, mock, test } from 'claude-code/testing'

const footer = {
  plugin: 'ceh-session-orchestration',
  component: 'SessionMode' as const,
  requestId: 'modes',
  props: { modes: [] as string[] },
}

// Stands for the engine's own drawing of the footer, beneath the plugins.
const engineDraws = (on: On) =>
  on('ui.render', { component: 'SessionMode' }, ($, e) => {
    const { Text } = $.ui.resolve(e)

    return <Text>{e.props.modes.join(' & ')}</Text>
  })

// Stands for load-orchestrator.py, a settings hook beneath the modules: each SessionStart sets
// the lock to what `writes` gives for that event, and the lock folder lists it from then on.
const loader = (on: On, writes: (sessionId: string) => string | undefined, lock: { sessionId?: string } = {}) => {
  on('classic.SessionStart', (_$, e) => {
    lock.sessionId = writes(e.session_id) ?? lock.sessionId
    return {}
  })
  on('fs.list', () => ({
    value: lock.sessionId ? [{ name: 'abc.json', kind: 'file' as const, size: 1, mtimeMs: 0, isLink: false }] : [],
  }))
  on('fs.read', () => ({ value: JSON.stringify({ pid: 1, startedAt: 1, sessionId: lock.sessionId, name: 'x' }) }))
}

const startup = { source: 'startup' as const, session_id: 's1' }

test('the session the loader makes the orchestrator shows the orchestrator label', async ($, on) => {
  mock.env(on, { TEMP: '/tmp' })
  loader(on, id => id)
  engineDraws(on)
  await $.classic.SessionStart(startup)
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('orchestrator')
  await ui.unmount()
})

test('a worker shows the worker label', async ($, on) => {
  mock.env(on, { CEH_ORCHESTRATION_WORKER: 'repo' })
  loader(on, () => undefined)
  engineDraws(on)
  await $.classic.SessionStart(startup)
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('worker')
  await ui.unmount()
})

test('a session the loader refused, as another session orchestrates, shows no label', async ($, on) => {
  mock.env(on, { TEMP: '/tmp' })
  loader(on, () => 'other')
  engineDraws(on)
  await $.classic.SessionStart(startup)
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('')
  await ui.unmount()
})

test('with no lock folder no label shows', async ($, on) => {
  mock.env(on, { TEMP: '/tmp' })
  on('classic.SessionStart', () => ({}))
  engineDraws(on)
  await $.classic.SessionStart(startup)
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('')
  await ui.unmount()
})

test('with load-orchestrator off, an old lock naming the session gives no label', async ($, on) => {
  mock.env(on, { TEMP: '/tmp', CEH_DISABLED_HOOKS: 'usage-limit-watch, load-orchestrator' })
  loader(on, () => undefined, { sessionId: 's1' })
  engineDraws(on)
  await $.classic.SessionStart({ source: 'resume', session_id: 's1' })
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('')
  await ui.unmount()
})

test('after /clear the label follows the lock the loader rewrote for the new session id', async ($, on) => {
  mock.env(on, { TEMP: '/tmp' })
  loader(on, id => id)
  engineDraws(on)
  await $.classic.SessionStart(startup)
  await $.classic.SessionStart({ source: 'clear', session_id: 's2' })
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('orchestrator')
  await ui.unmount()
})

test('after /clear a lock left on the old session id gives no label', async ($, on) => {
  mock.env(on, { TEMP: '/tmp' })
  loader(on, id => (id === 's1' ? id : undefined))
  engineDraws(on)
  await $.classic.SessionStart(startup)
  await $.classic.SessionStart({ source: 'clear', session_id: 's2' })
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  expect((await ui.find({ type: 'Text' }))?.text).toBe('')
  await ui.unmount()
})

test('with ceh-every-session beneath, both labels show in one row', async ($, on) => {
  mock.env(on, { CEH_ORCHESTRATION_WORKER: 'repo' })
  loader(on, () => undefined)
  // Stands for ceh-every-session's footer hook, as fold-replies.tsx appends its label.
  on('ui.render', { component: 'SessionMode' }, ($, e, next) =>
    next({ ...e, props: { modes: [...e.props.modes, 'folded replies (mod)'] } }),
  )
  engineDraws(on)
  await $.classic.SessionStart(startup)
  const ui = await $.ui.mount({ surface: 'terminal', ...footer })
  const text = (await ui.find({ type: 'Text' }))?.text ?? ''
  expect(text).toMatch(/(^| & )worker( & |$)/)
  expect(text).toMatch(/folded replies \(mod\)/)
  await ui.unmount()
})
