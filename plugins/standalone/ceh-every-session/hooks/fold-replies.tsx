import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { SectionId } from '../types'
import { split } from './split-summary'
import { takeDecisions } from './take-decisions'

const open = atom({ plugin: 'ceh-every-session', key: 'open' } as const, [] as SectionId[])
const picked = atom({ plugin: 'ceh-every-session', key: 'picked' } as const, {} as Record<string, number>)
const showAll = atom({ plugin: 'ceh-every-session', key: 'showAll' } as const, false)

// A footer mode label, not $.ui.status: the engine draws a status with a warning mark.
const FOLDED = 'folded replies (mod)'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'details',
      description: 'Fold or unfold the details under summary tables: /details on|off',
    })

    return next(e)
  })

  on('command.run', { command: 'details' }, async ($, e) => {
    const arg = e.args.trim()
    const isAll = arg === 'on' ? true : arg === 'off' ? false : !(await read($, showAll))
    await update($, showAll, () => isAll)

    return { text: isAll ? 'Details shown under summary tables.' : 'Details folded under summary tables.' }
  })

  on('ui.render', { component: 'SessionMode' }, async ($, e, next) =>
    (await read($, showAll)) ? next(e) : next({ ...e, props: { modes: [...e.props.modes, FOLDED] } }),
  )

  on('ui.render', { component: 'AssistantMessage' }, async ($, e, next) => {
    const { rest, decisions } = takeDecisions(e.props.text)
    const parts = (await read($, showAll)) ? null : split(rest)
    if (!parts && decisions.length === 0) return next(e)

    const opened = await read($, open)
    const picks = await read($, picked)
    const { Box, Button, Markdown, Text } = $.ui.resolve(e)
    const decisionId = (index: number) => `${e.requestId}#d${index}`

    // A pick fills the prompt box with every pick of this reply, unsent, so the
    // person can add to it or pick again before pressing Enter.
    const pick = async (index: number, option: number) => {
      const now = { ...picks, [decisionId(index)]: option }
      await update($, picked, all => ({ ...all, [decisionId(index)]: option }))
      const answers = decisions.flatMap((decision, at) => {
        const chosen = decision.options[now[decisionId(at)] ?? -1]
        return chosen ? [`${decision.question} ${chosen.replace(/\s*\(recommended\)\s*$/i, '')}`] : []
      })
      await $.prompt.fill({ text: answers.join('\n') })
    }

    return (
      <Box flexDirection="column">
        {!parts && rest.trim() && <Markdown text={rest.trim()} />}
        {parts?.lead && <Markdown text={parts.lead} />}
        {parts && <Markdown text={parts.table} />}
        {parts?.sections.map((section, index) => {
          const id = `${e.requestId}#${index}`
          const isOpen = opened.includes(id)
          const toggle = () =>
            update($, open, list => (isOpen ? list.filter(one => one !== id) : [...list, id]))

          return (
            <>
              <Box flexDirection="column" borderStyle="round" borderDimColor paddingX={1}>
                <Button key={id} plain onPress={toggle}>
                  <Text dimColor>{isOpen ? '▾' : '▸'}</Text> {section.number && `${section.number} `}
                  <Text bold={isOpen}>{section.topic}</Text>
                </Button>
                {isOpen && <Markdown text={section.body.trim()} />}
              </Box>
              {section.after.trim() && (
                <Box key={`${id}a`} flexDirection="column" borderStyle="round" borderDimColor paddingX={1}>
                  <Markdown text={section.after.trim()} />
                </Box>
              )}
            </>
          )
        })}
        {decisions.map((decision, index) => {
          const chosen = picks[decisionId(index)]

          return (
            <Box flexDirection="column" borderStyle="round" borderDimColor paddingX={1}>
              <Text bold>{decision.question}</Text>
              {decision.options.map((option, at) => (
                <Button key={`${decisionId(index)}o${at}`} plain onPress={() => pick(index, at)}>
                  <Text dimColor={chosen !== at}>{chosen === at ? '●' : '○'}</Text> {at + 1}.{' '}
                  {option.replaceAll('`', '')}
                </Button>
              ))}
            </Box>
          )
        })}
      </Box>
    )
  })
}
