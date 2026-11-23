#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname 'docs/spec.md')"
cat >'docs/spec.md' <<'EOF_FIXTURE'
# Spec: password reset

Users who forget their password get a reset link by email. The link works once and expires.
The reset page asks for the new password twice. After a reset, the user is logged in.
Rate limiting: TBD.
EOF_FIXTURE
