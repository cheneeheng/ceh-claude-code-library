# ceh-ops

Operations standards for running a deployed service: deploy pipeline, incident response, and
rollback — plus CI/CD pipeline automation via GitHub Actions and GitLab CI agents.

Security, observability, and database-migration standards now live in `ceh-python-service`; semantic
versioning and git tagging live in `ceh-git-workflow:release`.

## Skills (Auto-Load)

| Skill       | Triggers When                                                                                              |
| ----------- | ---------------------------------------------------------------------------------------------------------- |
| `deploy`    | Building/tagging images, promoting staging→prod, post-deploy health/metric checks, classifying a change    |
| `incidents` | Responding to a production incident, classifying P1/P2/P3, writing a post-mortem, creating a hotfix branch |
| `rollback`  | Deployment fails health check, error rates spike post-deploy, data integrity issue detected                |

## Agents

| Agent            | When to Use                                                                         |
| ---------------- | ----------------------------------------------------------------------------------- |
| `github-actions` | Create, review, debug, or optimize GitHub Actions workflows in `.github/workflows/` |
| `gitlab-ci`      | Create, review, debug, or optimize GitLab CI pipelines in `.gitlab-ci.yml`          |

## Scripts

All scripts live in `scripts/`. Used by the CI agents — also callable directly.

| Script                            | Usage                                                                  |
| --------------------------------- | ---------------------------------------------------------------------- |
| `gh-detect-stack.sh`              | Identify project stack and existing GitHub workflows                   |
| `gh-scaffold.sh <stack>`          | Emit a starter workflow for node, python-uv, python, go, rust, generic |
| `gh-validate.sh <file>`           | YAML lint + actionlint (if installed)                                  |
| `gh-analyze-failure.sh <logfile>` | Extract the first failure signal from a GitHub Actions log             |
| `gl-detect-stack.sh`              | Identify project stack and existing GitLab CI config                   |
| `gl-scaffold.sh <stack>`          | Emit a starter `.gitlab-ci.yml` for common stacks                      |
| `gl-validate.sh <file>`           | YAML lint + glab ci lint (if installed)                                |
| `gl-analyze-failure.sh <logfile>` | Extract the first failure signal from a GitLab job log                 |
