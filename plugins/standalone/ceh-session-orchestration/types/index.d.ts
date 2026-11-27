/** The session's part in orchestration: empty for a session with neither role. */
export type Role = '' | 'orchestrator' | 'worker'

declare module 'claude-code' {
  interface PluginState {
    'ceh-session-orchestration': {
      role: Role
    }
  }
}
