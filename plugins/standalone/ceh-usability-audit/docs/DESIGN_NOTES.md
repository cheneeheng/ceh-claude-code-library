# ceh-usability-audit design notes

## Hand-offs are not dependencies

`ceh-web-frontend:make-ui-accessible` owns the mechanical floor — keyboard reachability, contrast,
ARIA, focus. This plugin owns the comprehension layer and delegates the floor rather than
re-deriving it. `ceh-ui-design:design-ui` owns build-time visual decisions. Both hand-offs are
conditional, so neither `ceh-web-frontend` nor `ceh-ui-design` is a dependency.

## Report render and generated Markdown guard

| Hook                     | Event                                        | Script                    | Default |
| ------------------------ | -------------------------------------------- | ------------------------- | ------- |
| Report render            | `PostToolUse` (`Edit`, `Write`, `MultiEdit`) | `artifact-render-hook.py` | on      |
| Generated Markdown guard | `PreToolUse` (`Edit`, `Write`, `MultiEdit`)  | `generated-md-guard.py`   | on      |

`simulate-newcomer-first-run` and `audit-interface` save `UX_AUDIT.yaml` (`first-run-audit/v2` and
`interface-audit/v2`), and `audit-error-messages` saves `ERROR_MESSAGES.yaml`
(`error-messages-audit/v2`). After every write to one, the render hook picks the model by the
file's `schema:` key, checks the YAML through `uv` and renders the Markdown beside it, or reports
each error back to the agent and leaves the Markdown as it was. The guard denies a direct edit to a
generated Markdown file and names its YAML. Both need `uv`: without it the agent is told once per
session that the file went unchecked. `CEH_ARTIFACT_CHECK=off`, or `CEH_DISABLED_HOOKS` with
`artifact-render-hook` or `generated-md-guard`, switches them off, and these are the only
environment variables the plugin reads.
