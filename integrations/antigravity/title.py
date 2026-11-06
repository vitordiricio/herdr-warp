#!/usr/bin/env python3
"""Publish only the active Antigravity conversation name as the terminal title."""

import json
import sys

try:
    state = json.load(sys.stdin)
except (ValueError, OSError):
    state = {}

value = state.get("conversation_title") if isinstance(state, dict) else None
if isinstance(value, str):
    title = " ".join("".join(char if char.isprintable() else " " for char in value).split())
else:
    title = ""

print(title or "Antigravity")
