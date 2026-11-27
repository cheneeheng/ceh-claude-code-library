import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Role } from '../types'

const role = atom({ plugin: 'ceh-session-orchestration', key: 'role' } as const, '' as Role)

// The session's role as load-orchestrator.py left it: a worker by its variable, the
// orchestrator when a lock the loader wrote names this session. The loader's lock is
// <temp>/ceh-session-orchestration/<hash of the repo root>.json (docs/CROSS_REFERENCES.md); this
// reads every lock there and matches its sessionId, so it needs no copy of the hash.
// less-code: a lock of this session under another repository root also matches; hash the root as
// the loader does if a session is ever seen to start under a second root.
async function findRole($: EngineInterface, sessionId: string): Promise<Role> {
  try {
    if (await $.env.get('CEH_ORCHESTRATION_WORKER')) return 'worker'
    // The loader off: it never deletes a lock, so a resumed session would still match its old one.
    const disabled = ((await $.env.get('CEH_DISABLED_HOOKS')) ?? '').replace(/ /g, '').split(',')
    if (disabled.includes('load-orchestrator')) return ''
    // Python's tempfile.gettempdir() order, which the loader uses. Checked on Windows only.
    const temp =
      (await $.env.get('TMPDIR')) || (await $.env.get('TEMP')) || (await $.env.get('TMP')) || '/tmp'
    const dir = `${temp}/ceh-session-orchestration`
    for (const entry of await $.fs.list(dir)) {
      const held = await $.fs.read(`${dir}/${entry.name}`).then(JSON.parse, () => undefined)
      if (held?.sessionId === sessionId) return 'orchestrator'
    }
  } catch {
    // A missing folder or a failed call: no label.
  }
  return ''
}

export const register: Register = on => {
  // After next(e), which runs the settings and plugin hooks beneath the modules, the loader among
  // them, so its lock is written. Nothing after next(e) throws, so the loader never runs twice.
  on('classic.SessionStart', async ($, e, next) => {
    const result = await next(e)
    try {
      const found = await findRole($, e.session_id)
      await update($, role, () => found)
    } catch {
      // The label stays as it was.
    }
    return result
  })

  // A footer mode label, not $.ui.status, as fold-replies.tsx in ceh-every-session does.
  on('ui.render', { component: 'SessionMode' }, async ($, e, next) => {
    const now = await read($, role)
    return now ? next({ ...e, props: { modes: [...e.props.modes, now] } }) : next(e)
  })
}
