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
