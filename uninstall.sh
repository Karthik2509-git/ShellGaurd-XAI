#!/usr/bin/env bash
# ShellGuard Runtime — Uninstaller Script

set -e

echo "🛡️ Uninstalling ShellGuard Runtime..."

DESKTOP_FILE="$HOME/.local/share/applications/shellguard-runtime.desktop"
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "✓ Removed Desktop Entry"
fi

echo "✅ ShellGuard Runtime successfully uninstalled."
