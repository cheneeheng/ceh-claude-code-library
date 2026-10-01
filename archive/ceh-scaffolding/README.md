# ceh-scaffolding

Per-project-type project setup. Each skill produces the right directory layout, initial config, and
required `.gitignore` entries for one project type — in a single moment-triggered skill. There is no
generic "structure" skill: layout, config, and ignore rules are co-located per type.

## Skills (Auto-Load)

| Skill                     | Triggers When                                                 |
| ------------------------- | ------------------------------------------------------------- |
| `scaffold-python-service` | Starting a FastAPI/Python web service repo                    |
| `scaffold-python-library` | Starting a distributable Python library/package               |
| `scaffold-web-frontend`   | Starting a SvelteKit or React + Vite frontend                 |
| `scaffold-fullstack-web`  | Starting a fullstack web app (service + frontend in one repo) |

The small shared bits duplicated across these skills (e.g. `.gitignore` entries) are governed by the
repo's Shared-Standards Duplication Policy — see `docs/CROSS_REFERENCES.md`.
