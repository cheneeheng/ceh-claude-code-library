# ceh-workflow-builder: Architecture

How the plugin turns a repetitive task into a workflow that runs through Claude Code, interactively
or headless (`claude -p`), and where Claude Code's dynamic workflows fit in.

The `flow.yaml` format is specified in
[`references/flow-config-schema.md`](../references/flow-config-schema.md) and the runner in
[`skills/run-agentic-workflow/SKILL.md`](../skills/run-agentic-workflow/SKILL.md). This page shows how
they fit together; those two files are the authority on keys and statuses.

Evidence for every runtime claim marked `Fn` is in [TEST_RESULTS.md](TEST_RESULTS.md).

## Two phases, two lifetimes

| Phase     | Who drives                                          | Mode                    | Produces                                                             |
| --------- | --------------------------------------------------- | ----------------------- | -------------------------------------------------------------------- |
| **Build** | `interview-workflow-task`, `build-agentic-workflow` | Interactive only        | Files committed to the target repo                                   |
| **Run**   | `run-agentic-workflow`, following `flow.yaml`       | Interactive or headless | Run artifacts and `run-state.md` under the git-ignored run directory |

Building is interactive by construction: the interview asks the user, the intake gate refuses to
infer missing answers, and nothing is written until the user agrees to the file list. Running is the
part that must work unattended.

## Components

```mermaid
flowchart LR
    subgraph plugin["ceh-workflow-builder plugin"]
        interview["interview-workflow-task<br/>(skill)"]
        builder["build-agentic-workflow<br/>(skill)"]
        runner["run-agentic-workflow<br/>(skill)"]
        schema[("references/<br/>flow-config-schema.md")]
    end

    subgraph target["Target repo"]
        spec[("&lt;build-dir&gt;/&lt;name&gt;-workflow-spec.md")]
        subgraph emitted[".claude/ (committed)"]
            trigger["skills/&lt;name&gt;-flow/SKILL.md<br/>thin trigger"]
            config[("skills/&lt;name&gt;-flow/flow.yaml")]
            guide["skills/&lt;name&gt;-flow/README.md<br/>invocation guide"]
            stepskills["skills/&lt;name&gt;-&lt;step&gt;/<br/>step skills"]
            scripts["skills/&lt;name&gt;-flow/scripts/"]
            schemas[("skills/&lt;name&gt;-flow/references/<br/>handoff schemas")]
            wf["workflows/&lt;name&gt;-&lt;step&gt;.js<br/>optional dynamic workflow"]
        end
        rundir[("&lt;run-dir&gt;/&lt;name&gt;/&lt;run-id&gt;/<br/>run-state.md + artifacts<br/>(git-ignored)")]
    end

    interview -->|writes| spec
    builder -->|reads| spec
    builder -.->|calls when a row is open| interview
    builder -->|emits| emitted
    builder -.->|validates against| schema
    trigger -->|invokes with config=| runner
    runner -->|reads| config
    runner -.->|validates against| schema
    runner -->|dispatches stages| stepskills
    runner -->|dispatches stages| scripts
    runner -->|dispatches stages| wf
    runner -->|writes| rundir
```

| Component                 | Role                                                                                                                                                                                                        |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interview-workflow-task` | Asks the nine questions and writes the spec. Never answers for the user.                                                                                                                                    |
| `build-agentic-workflow`  | Gates on the spec, decides one skill vs workflow, picks a backend per step, emits leaf-first.                                                                                                               |
| `flow-config-schema.md`   | The `flow.yaml` contract. One copy, shared by builder (writer) and runner (reader) via `${CLAUDE_PLUGIN_ROOT}`.                                                                                             |
| `run-agentic-workflow`    | Generic runner: loads `flow.yaml`, preflights, walks stages, enforces gates and approvals, keeps run state.                                                                                                 |
| `<name>-flow/SKILL.md`    | Thin trigger in the target repo. Carries the moment in its `description` and `/<name>-flow`; its body only calls the runner with `config=${CLAUDE_SKILL_DIR}/flow.yaml` followed by `$ARGUMENTS` unchanged. |
| `flow.yaml`               | Stages, gates, approvals, fan-out and retry bounds for one workflow. Replaces the pipeline tables the flow skill used to carry.                                                                             |
| `<name>-flow/README.md`   | Invocation guide: the interactive and headless commands, with `--allowedTools` collected from each stage's `tools`. A skill directory's README is never loaded as context.                                  |
| `.claude/workflows/*.js`  | Optional: a stage that runs as a saved Claude Code dynamic workflow.                                                                                                                                        |

The single-skill path is unchanged: when the builder's workflow gate does not hold, it emits one
`SKILL.md` and none of the above beyond it.

## Stage backends

The runner owns ordering, gates, approvals and state. Each stage's work goes to one backend:

| `kind`     | Runs via               | Own context    | Can ask the user  | Use for                                                                                                 |
| ---------- | ---------------------- | -------------- | ----------------- | ------------------------------------------------------------------------------------------------------- |
| `inline`   | the runner itself      | no             | yes (interactive) | small steps that fit in the run's context                                                               |
| `skill`    | `Skill` tool           | no             | yes (interactive) | a step owned by an existing or generated skill                                                          |
| `script`   | `Bash`                 | n/a            | no                | mechanical, deterministic steps                                                                         |
| `agent`    | `Agent` tool           | yes            | no                | a large step, or a fan-out bounded by `max_parallel` (1-16) and `max_items`, one output file per worker |
| `workflow` | Workflow tool, by name | yes, per agent | no                | many items, cross-checking, loop-until-pass: dozens to hundreds of agents                               |

`workflow` is never assumed. The runner checks at preflight that the Workflow tool is present, and a
`skill` stage naming a plugin skill that the plugin is installed. When the capability is **absent**,
the stage runs its `fallback`: `fail` (the default), `agent` or `inline`. Without the tool, Claude
has been observed to imitate a workflow by hand and report success (F6), so imitation is forbidden.
A call that is attempted and **denied or errors** is a failed stage (`workflow-denied`), never a
fallback, because a fallback there would hide a missing permission.

Human input happens **only between stages, in the runner**. `AskUserQuestion` is stripped from
subagents, and a dynamic workflow takes no input mid-run, so an approval can never live inside an
`agent` or `workflow` stage.

## How a run proceeds

```mermaid
flowchart TD
    start(["/&lt;name&gt;-flow args<br/>mode=interactive|headless"]) --> load["Load flow.yaml, check against<br/>schema, inputs, .js line endings"]
    load -->|invalid| prefail(["FLOW STATUS:<br/>failed - &lt;reason&gt;"])
    load --> pre["Preflight: Workflow tool and<br/>plugin skills present?"]
    pre -->|absent, fallback=fail| prefail
    pre --> state["Create or resume run dir<br/>and run-state.md"]
    state --> next{"Next pending stage?"}
    next -->|none| done(["FLOW STATUS: done"])
    next --> appr{"Stage has approval?"}
    appr -->|no| world
    appr -->|yes, interactive| ask["AskUserQuestion,<br/>showing the whole batch"]
    ask -->|approved| world
    ask -->|declined| failed
    appr -->|yes, headless| hl{"approval.headless"}
    hl -->|preapproved-only and<br/>approve=&lt;stage&gt; passed| world
    hl -->|stop, or preapproved-only<br/>without approve=| waiting(["Write approval-&lt;stage&gt;.md<br/>FLOW STATUS:<br/>awaiting-approval &lt;stage&gt;"])
    hl -->|fail| failed
    world{"unsafe_to_rerun?<br/>world_check true?"} -->|"no check, or true"| run["Dispatch: inline / skill /<br/>script / agent / workflow"]
    world -->|false: effect may exist| failed
    run --> gate{"Gate passes?"}
    gate -->|yes| mark["Mark stage done<br/>in run-state.md"] --> next
    gate -->|no, retries left| run
    gate -->|no, bound spent| failed(["FLOW STATUS:<br/>failed &lt;stage&gt; &lt;reason&gt;"])
```

The final `FLOW STATUS:` line is written to `run-state.md` too, so a headless caller can branch on
either the reply or the file. Failures before any stage runs use `-` as the stage id. A declined
approval ends as `failed <stage> declined` with the stage left `pending`, so a resumed run asks again.
`on_fail: retry` is not allowed on a stage with an `approval` or a `fan_out`, so a retry can never
fire an irreversible step or a whole fan-out twice.

## Interactive vs headless

The mode is an explicit launch argument, default `interactive`. A skill cannot reliably detect it
is headless, and guessing wrong either hangs on a question nobody can answer or skips a
confirmation.

| Concern                           | Interactive                            | Headless (`claude -p`)                                                                              |
| --------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Start                             | the moment, or `/<name>-flow`          | `claude -p '/<name>-flow mode=headless ...'` — skill slash commands work (F11)                      |
| Approval before a stage           | `AskUserQuestion`                      | `headless: stop` writes `approval-<stage>.md` and ends at `awaiting-approval`; resumed later        |
| Resume a stopped run              | asks: resume or new                    | `resume=latest` or `new` (default `new`)                                                            |
| Workflow tool                     | Pro: `/config` → Dynamic workflows     | `--settings '{"enableWorkflows": true, "disableWorkflows": false}'` (F5, F8)                        |
| Launching a saved workflow        | runner calls the Workflow tool by name | same; `/<workflow-name>` does **not** work in `-p` (F9)                                             |
| Workflow launch permission        | approval dialog                        | `--allowedTools 'Workflow(<name>)'` (F12)                                                           |
| Tool permissions for agents       | prompted mid-run                       | nobody to prompt: each stage lists its `tools`, and the builder collects them into `--allowedTools` |
| Usage limit hit inside a workflow | run waits for the reset                | agents fail; stage stays `pending`, resume later                                                    |
| Watching or stopping a run        | `/workflows`                           | none; bounded by `max_parallel`, `max_items` and retry bounds in `flow.yaml`                        |
| Output for a caller               | reply text                             | `--output-format json`: `result` ends with the `FLOW STATUS:` line, plus `session_id`               |

### Headless approval loop

A headless run cannot ask, so an approval ends the session and a later invocation carries the
answer. Both continuation routes were tested (F11):

```mermaid
sequenceDiagram
    participant C as Caller (shell, CI, scheduler)
    participant S1 as claude -p session
    participant R as run-state.md
    participant H as Human

    C->>S1: /name-flow mode=headless ...
    S1->>R: stages 1..k done, stage k+1 awaiting-approval, approval-publish.md
    S1-->>C: JSON: session_id, approval content, "FLOW STATUS: awaiting-approval publish"
    C->>H: notify with approval-publish.md (out of band)
    H-->>C: approve
    alt session still available
        C->>S1: claude -p --resume session_id 'APPROVED publish'
        Note over S1: same session_id (F14), keeps context
    else session gone
        C->>S1: claude -p '/name-flow mode=headless resume=latest approve=publish'
        Note over S1: fresh session, state from run-state.md only
    end
    S1->>R: record approval (stage, time, source), run stage k+1 ...
    S1-->>C: "FLOW STATUS: done" or the next awaiting-approval
```

`run-state.md` is the record; `--resume` is a convenience that keeps the conversation context.
Every approval is written to the state file with its source, so a resumed run never relies on prompt
text alone. `approval-<stage>.md` holds exactly what the approval's `show` names, so the person
approving headless sees what an interactive user would have been shown. On resume the inputs come
from `run-state.md`; re-passing a different value fails the run (`inputs changed on resume`).

Example headless invocation (pwsh; Bash is the same apart from line continuation):

```powershell
claude -p '/prepublish-flow mode=headless repo=.' `
  --settings '{"enableWorkflows": true, "disableWorkflows": false}' `
  --allowedTools 'Workflow(prepublish-audit)' 'Read' 'Edit' 'Write' 'Bash(uv run pytest:*)' `
  --output-format json
```

The builder writes this command into the flow's `README.md`, with `--allowedTools` collected from
each stage's `tools`, and includes `--settings` only when a `workflow` stage exists. A flow with a
`workflow` stage requires Claude Code v2.1.269 or later. That floor comes from the documented
feature versions. The tests ran on v2.1.288, so the undocumented `enableWorkflows` behaviour (F8) is
verified only there.

## Design decisions

| Decision                                                                           | Why                                                                                                                                                      |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A generic runner skill reads `flow.yaml`, instead of compiling it to per-step code | One config drives both modes with no regeneration. A dynamic workflow cannot be the interpreter: it cannot read files or ask the user.                   |
| Dynamic workflows are a stage backend, not the orchestrator                        | They take no mid-run input, so approvals must sit between stages. One workflow per stage matches the docs' advice for sign-off between stages.           |
| Mode is an explicit argument                                                       | A skill cannot detect headless reliably.                                                                                                                 |
| No "proceed anyway" headless approval                                              | `headless:` is `stop`, `preapproved-only` or `fail`. Pre-approval is an explicit `approve=` argument, recorded in run state.                             |
| Missing Workflow tool fails or falls back, never imitates                          | Observed imitation looked like success on disk (F6).                                                                                                     |
| A denied workflow call fails the stage instead of falling back                     | A fallback would hide a missing permission behind a run that looks healthy.                                                                              |
| Fan-out declares `max_items` as well as `max_parallel`                             | Headless runs have no `/workflows` view to stop them, so the config bounds the cost.                                                                     |
| No `on_fail: retry` on a stage with an approval or a fan-out                       | A retry must never fire an irreversible step or a whole fan-out a second time.                                                                           |
| Explicit `--settings` and `--allowedTools` on every headless run                   | `enableWorkflows` is undocumented (F8), and a launch allowed without a rule was likely machine-specific (F12). Explicit flags make the run reproducible. |
| The runner lives in the plugin, not vendored into each target repo                 | One copy, updated with the plugin. Generated flows declare the plugin in `compatibility`.                                                                |
| Workflow `.js` is written with LF and pinned by `.gitattributes`                   | CRLF makes the launch fail (F2).                                                                                                                         |
| Building stays interactive-only                                                    | The intake must not infer answers, and emission needs the user's agreement to the file list.                                                             |
