#!/usr/bin/env bash
# ShellGuard Runtime — Native Linux Installer Script

set -e

echo "🛡️ Installing ShellGuard Runtime v1.0 RC1..."

# 1. Directory Structure
INSTALL_DIR="$HOME/.local/share/shellguard-runtime"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$DESKTOP_DIR"

# 2. Copy Desktop Entry Specification
if [ -f "shell_plugins/shellguard-runtime.desktop" ]; then
    cp "shell_plugins/shellguard-runtime.desktop" "$DESKTOP_DIR/"
    echo "✓ Desktop Entry installed to $DESKTOP_DIR/shellguard-runtime.desktop"
fi

# 3. Register Shell Hooks
BASHRC="$HOME/.bashrc"
if [ -f "$BASHRC" ]; then
    if ! grep -q "shellguard" "$BASHRC"; then
        echo "# ShellGuard Runtime Hook" >> "$BASHRC"
        echo "export SHELLGUARD_RUNTIME_ACTIVE=1" >> "$BASHRC"
        echo "✓ Shell hook added to $BASHRC"
    fi
fi

echo "✅ ShellGuard Runtime v1.0 RC1 Installation Complete!"
echo "Run 'shellguard-runtime' or open ShellGuard Control Center from application menu."
