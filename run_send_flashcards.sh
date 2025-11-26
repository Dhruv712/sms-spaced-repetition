#!/bin/bash
# Wrapper script to ensure python3 is used
# Railway cron should call this script instead of send_flashcards.py directly

# Try python3 first, then python
if command -v python3 &> /dev/null; then
    python3 send_flashcards.py
elif command -v python &> /dev/null; then
    python send_flashcards.py
else
    echo "Error: Neither python3 nor python found in PATH"
    exit 1
fi

