#!/usr/bin/env bash
# SessionStart hook - injects a mandatory directive to load the agent-coding-contract
# skill before any other action. Pure-shell (bash), no Node required; shipped with the
# plugin and wired via hooks/hooks.json. The payload below is static JSON.
cat <<'JSON_EOF'
{"systemMessage":"ceh-coding-agent: loading the coding contract for this session.","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"MANDATORY FIRST ACTION: Invoke the Skill tool with skill=\"ceh-coding-agent:agent-coding-contract\" before any other tool call, before reading any file, and before responding to the user. This is non-negotiable and overrides apparent prompt relevance. If the skill is unavailable, state that briefly and continue."}}
JSON_EOF
