#!/usr/bin/env bash
# gl-scaffold.sh
# Emits a starter .gitlab-ci.yml for a given stack to stdout.
# The agent reads and customizes the output before writing it to disk.
# Usage: bash gl-scaffold.sh <node|python|go|rust|java-maven|docker|generic>

set -euo pipefail
STACK="${1:-generic}"

case "$STACK" in

node)
  cat <<'YAML'
# .gitlab-ci.yml — Node.js
default:
  image: node:22-alpine
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - .npm/
      - node_modules/

stages: [lint, test, build]

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

.node-base:
  before_script:
    - npm ci --prefer-offline

lint:
  stage: lint
  extends: .node-base
  script:
    - npm run lint --if-present
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  extends: .node-base
  script:
    - npm test
  artifacts:
    when: always
    reports:
      junit: junit.xml       # adjust to your reporter output
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

build:
  stage: build
  extends: .node-base
  script:
    - npm run build --if-present
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

python-uv)
  cat <<'YAML'
# .gitlab-ci.yml — Python (uv)
default:
  image: python:3.12-slim
  cache:
    key:
      files:
        - uv.lock
    paths:
      - .uv-cache/

stages: [lint, test]

variables:
  UV_CACHE_DIR: "$CI_PROJECT_DIR/.uv-cache"

.python-base:
  before_script:
    - pip install --quiet uv
    - uv sync --frozen

lint:
  stage: lint
  extends: .python-base
  script:
    - uv run ruff check .
    - uv run mypy --strict src/
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  extends: .python-base
  script:
    - uv run pytest --junitxml=report.xml --cov --cov-report=xml -q
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    when: always
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

python)
  cat <<'YAML'
# .gitlab-ci.yml — Python
default:
  image: python:3.12-slim
  cache:
    key:
      files:
        - requirements.txt
    paths:
      - .cache/pip/
      - .venv/

stages: [lint, test]

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

.python-base:
  before_script:
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install --quiet -r requirements.txt

lint:
  stage: lint
  extends: .python-base
  script:
    - pip install --quiet ruff
    - ruff check .
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  extends: .python-base
  script:
    - pip install --quiet pytest pytest-cov
    - pytest --junitxml=report.xml --cov --cov-report=xml -q
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    when: always
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

go)
  cat <<'YAML'
# .gitlab-ci.yml — Go
default:
  image: golang:1.23-alpine
  cache:
    key:
      files:
        - go.sum
    paths:
      - .go-cache/
      - .go-mod/

stages: [lint, test]

variables:
  GOCACHE: "$CI_PROJECT_DIR/.go-cache"
  GOMODCACHE: "$CI_PROJECT_DIR/.go-mod"
  CGO_ENABLED: "0"

lint:
  stage: lint
  script:
    - go vet ./...
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  script:
    - go test -race ./... -count=1
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

rust)
  cat <<'YAML'
# .gitlab-ci.yml — Rust
default:
  image: rust:1-slim
  cache:
    key:
      files:
        - Cargo.lock
    paths:
      - .cargo/registry/
      - target/

stages: [lint, test]

variables:
  CARGO_HOME: "$CI_PROJECT_DIR/.cargo"
  CARGO_TERM_COLOR: always

lint:
  stage: lint
  script:
    - rustup component add clippy rustfmt
    - cargo fmt --check
    - cargo clippy -- -D warnings
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  script:
    - cargo test --all-features
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

java-maven)
  cat <<'YAML'
# .gitlab-ci.yml — Java (Maven)
default:
  image: eclipse-temurin:21-jdk
  cache:
    key:
      files:
        - pom.xml
    paths:
      - .m2/repository/

stages: [build, test]

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"

build:
  stage: build
  script:
    - mvn -B package -DskipTests --no-transfer-progress
  artifacts:
    paths:
      - target/*.jar
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

test:
  stage: test
  script:
    - mvn -B verify --no-transfer-progress
  artifacts:
    when: always
    reports:
      junit:
        - target/surefire-reports/TEST-*.xml
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

docker)
  cat <<'YAML'
# .gitlab-ci.yml — Docker build + push to GitLab Container Registry
default:
  image: docker:26
  services:
    - docker:26-dind

stages: [build, push]

variables:
  DOCKER_TLS_CERTDIR: "/certs"
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

before_script:
  - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"

build:
  stage: build
  script:
    - docker build --pull -t "$IMAGE_TAG" .
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

push:
  stage: push
  needs: [build]
  script:
    - docker push "$IMAGE_TAG"
    - docker tag "$IMAGE_TAG" "$CI_REGISTRY_IMAGE:latest"
    - docker push "$CI_REGISTRY_IMAGE:latest"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

*)
  cat <<'YAML'
# .gitlab-ci.yml — generic starter
stages: [build, test]

build:
  stage: build
  script:
    - echo "Replace with your build command"

test:
  stage: test
  needs: [build]
  script:
    - echo "Replace with your test command"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
YAML
  ;;

esac
