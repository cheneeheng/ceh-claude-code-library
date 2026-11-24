# ceh-python-library design notes

Maintainer detail moved out of the plugin README on 2026-11-24, when the README was rewritten for
the person installing the plugin. The site does not publish this file.

## Shared standards

`configure-python-library-env` and `write-pytest-library-tests` are duplicated from
`ceh-python-service` (`configure-python-service-env` and `write-pytest-service-tests`) per the repo's
Shared-Standards Duplication Policy. The library copies drop web-service dependencies (`fastapi`,
`uvicorn`, `asyncpg`) and the uvicorn dev-server command. See `docs/CROSS_REFERENCES.md` and edit
both copies in the same session.
