/** A section unfolded by hand, as `<requestId>#<index>`. */
export type SectionId = string

declare module 'claude-code' {
  interface PluginState {
    'ceh-every-session': {
      open: SectionId[]
      /** The option index picked per decision, keyed `<requestId>#d<index>`. */
      picked: Record<string, number>
      /** True when /details on shows every reply whole. */
      showAll: boolean
    }
  }
}
