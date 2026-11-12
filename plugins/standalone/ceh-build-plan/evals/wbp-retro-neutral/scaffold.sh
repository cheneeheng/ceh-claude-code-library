#!/usr/bin/env bash
set -euo pipefail
mkdir -p "$(dirname 'app.py')"
cat >'app.py' <<'EOF_FIXTURE'
from flask import Flask, jsonify, request

app = Flask(__name__)
NOTES = []


@app.post("/notes")
def create():
    NOTES.append({"id": len(NOTES) + 1, "body": request.json["body"]})
    return jsonify(NOTES[-1]), 201


@app.get("/notes")
def list_notes():
    return jsonify(NOTES)


@app.delete("/notes/<int:note_id>")
def delete(note_id):
    NOTES.pop(note_id)
    return "", 204
EOF_FIXTURE
mkdir -p "$(dirname 'README.md')"
cat >'README.md' <<'EOF_FIXTURE'
# notes

A tiny notes API. Run `flask --app app run` and you will recieve a JSON API.
EOF_FIXTURE
mkdir -p "$(dirname 'retros/2026-10-20.md')"
cat >'retros/2026-10-20.md' <<'EOF_FIXTURE'
# Retro 2026-10-20

What went wrong this week and the fixes we agreed on:

1. `DELETE /notes/<id>` pops by list index, not by note id, so it deletes the wrong note. Fix in `app.py`.
2. No tests exist. Add `tests/test_app.py` covering create, list, and delete.
3. The README does not say how to install Flask. Add an install section.
EOF_FIXTURE
