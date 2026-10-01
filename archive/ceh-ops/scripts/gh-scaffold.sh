#!/usr/bin/env bash
# gh-scaffold.sh
# Emits a starter GitHub Actions workflow for a given stack to stdout.
# The agent reads and customizes the output before writing it to disk.
# Usage: bash gh-scaffold.sh <node|python|go|rust|java-maven|docker|generic>

set -euo pipefail
STACK="${1:-generic}"

case "$STACK" in

node)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    name: Test (Node ${{ matrix.node }})
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        node: [20, 22]
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020  # v4.4.0
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test
YAML
  ;;

python-uv)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5.6.0
        with:
          python-version-file: pyproject.toml
      - run: pip install uv
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run mypy --strict src/
      - run: uv run pytest -q --tb=short
YAML
  ;;

python)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    name: Test (Python ${{ matrix.python }})
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        python: ['3.11', '3.12']
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065  # v5.6.0
        with:
          python-version: ${{ matrix.python }}
          cache: pip
      - run: pip install -r requirements.txt
      - run: python -m pytest -q --tb=short
YAML
  ;;

go)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/setup-go@d35c59abb061a4a6fb18e82ac0862c26744d6ab5  # v5.5.0
        with:
          go-version-file: go.mod
          cache: true
      - run: go vet ./...
      - run: go test -race -count=1 ./...
YAML
  ;;

rust)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

env:
  CARGO_TERM_COLOR: always

jobs:
  test:
    name: Test
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@98c8021b550208e191a6a3145459bfc9fb29c4c0  # v2.8.1
      - run: cargo fmt --check
      - run: cargo clippy -- -D warnings
      - run: cargo test --all-features
YAML
  ;;

java-maven)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    name: Test (Java ${{ matrix.java }})
    runs-on: ubuntu-latest
    timeout-minutes: 20
    strategy:
      fail-fast: false
      matrix:
        java: [17, 21]
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: actions/setup-java@c5195efecf7bdfc987ee8bae7a71cb8b11521c00  # v4.7.1
        with:
          java-version: ${{ matrix.java }}
          distribution: temurin
          cache: maven
      - run: mvn -B verify --no-transfer-progress
YAML
  ;;

docker)
  cat <<'YAML'
name: Docker Build
on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:

permissions:
  contents: read
  packages: write  # for GHCR push

jobs:
  build:
    name: Build & Push
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - uses: docker/setup-buildx-action@b5730b3e9e62e939ef4e1f35e8e8af9ccc1a0ac0  # v3.10.0
      - uses: docker/login-action@74a5d142397b4f367a81961eba4e8cd7edddf772  # v3.4.0
        if: github.event_name != 'pull_request'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@14487ce63c7a62a4a324b0bfb37086795e31c6c1  # v6.16.0
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
YAML
  ;;

*)
  cat <<'YAML'
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  build:
    name: Build & Test
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      - name: Build
        run: echo "Replace with your build command"
      - name: Test
        run: echo "Replace with your test command"
YAML
  ;;

esac
