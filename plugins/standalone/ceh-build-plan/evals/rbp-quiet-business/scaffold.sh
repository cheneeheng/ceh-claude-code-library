#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname 'BUSINESS_PLAN.md')"
cat >'BUSINESS_PLAN.md' <<'EOF_FIXTURE'
# Business plan: Notes for teams

Problem: small teams lose meeting notes. Customer: 5 to 20 person agencies.
Price: 8 EUR per seat per month. Channel: LinkedIn outreach.
EOF_FIXTURE
