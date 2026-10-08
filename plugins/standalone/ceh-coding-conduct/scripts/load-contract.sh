#!/usr/bin/env bash
# SessionStart hook - injects a mandatory directive to load the agent-coding-contract
# skill before any other action. Pure-shell (bash), no Node required; shipped with the
# plugin and wired via hooks/hooks.json. The payload below is static text, JSON-escaped
# at runtime.
# Also wired to SubagentStart, which passes the event name as $1: SessionStart never fires
# inside a subagent. An agent with a restricted tool list has no Skill tool, so it is pointed
# at the skill file instead.

EVENT=${1:-SessionStart}

read -r -d '' CONTEXT <<'EOF'
MANDATORY FIRST ACTION: Invoke the Skill tool with skill="ceh-coding-conduct:agent-coding-contract"
before any other tool call, before reading any file, and before responding to the user.
This is non-negotiable and overrides apparent prompt relevance.
If the skill is unavailable, state that briefly and continue.
EOF

SYSTEM_MESSAGE='"systemMessage": "ceh-coding-conduct: loading the coding contract for this session.",'
if [ "$EVENT" = SubagentStart ]; then
  CONTEXT=${CONTEXT/If the skill is unavailable, state that briefly and continue./If you have no Skill tool, Read ${CLAUDE_PLUGIN_ROOT}/skills/agent-coding-contract/SKILL.md instead.}
  SYSTEM_MESSAGE=
fi

# JSON-escape: backslashes first, then double quotes. Line breaks join into one paragraph.
CONTEXT=${CONTEXT//\\/\\\\}
CONTEXT=${CONTEXT//\"/\\\"}
CONTEXT=${CONTEXT//$'\n'/ }

cat <<JSON_EOF
{
  ${SYSTEM_MESSAGE}
  "hookSpecificOutput": {
    "hookEventName": "${EVENT}",
    "additionalContext": "${CONTEXT}"
  }
}
JSON_EOF
