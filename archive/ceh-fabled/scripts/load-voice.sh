#!/usr/bin/env bash
# SessionStart hook - injects a directive to load the fabled-voice skill so every
# session delivers in fable's response style without the user asking. Pure-shell
# (bash), no Node required; shipped with the plugin and wired via hooks/hooks.json.
# The payload below is static JSON. Ordered after the coding contract: the contract
# governs behaviour, this skill governs form only.
cat <<'JSON_EOF'
{"systemMessage":"ceh-fabled: loading fabled-voice response style for this session.","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"REQUIRED SETUP ACTION: Invoke the Skill tool with skill=\"ceh-fabled:fabled-voice\" before responding to the user. If the ceh-coding-agent:agent-coding-contract skill is also pending, load that one first. This governs the form of your responses for the whole session, not the work you do. If the skill is unavailable, state that briefly and continue."}}
JSON_EOF
