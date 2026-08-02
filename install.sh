#!/usr/bin/env bash
# ShellGuard Runtime v1.0.0-rc2 — Native Linux Installer Script
# Installs Freedesktop Entry, systemd --user service, XDG directories, and shell hooks.

set -e

echo "🛡️ Installing ShellGuard Runtime v1.0.0-rc2..."

# 1. XDG Base Directory Structure
XDG_CONFIG="$HOME/.config/shellguard-runtime"
XDG_STATE="$HOME/.local/state/shellguard-runtime"
XDG_CACHE="$HOME/.cache/shellguard-runtime"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

mkdir -p "$XDG_CONFIG" "$XDG_STATE" "$XDG_CACHE" "$BIN_DIR" "$DESKTOP_DIR" "$AUTOSTART_DIR" "$SYSTEMD_USER_DIR"
echo "✓ Registered XDG directories in $XDG_CONFIG"

# 2. Copy Desktop Entry & Autostart
if [ -f "shell_plugins/shellguard-runtime.desktop" ]; then
    cp "shell_plugins/shellguard-runtime.desktop" "$DESKTOP_DIR/"
    cp "shell_plugins/shellguard-runtime.desktop" "$AUTOSTART_DIR/"
    echo "✓ Installed Freedesktop Entry & Autostart"
fi

# 3. Register Systemd User Service
if [ -f "shell_plugins/shellguard-runtime.service" ]; then
    cp "shell_plugins/shellguard-runtime.service" "$SYSTEMD_USER_DIR/"
    systemctl --user daemon-reload || true
    systemctl --user enable shellguard-runtime.service || true
    echo "✓ Registered systemd user service (shellguard-runtime.service)"
fi

# 4. Register Shell Hooks (Bash, Zsh, Fish)
BASHRC="$HOME/.bashrc"
if [ -f "$BASHRC" ]; then
    if ! grep -q "shellguard.bash" "$BASHRC"; then
        echo "source $PWD/shell_plugins/shellguard.bash" >> "$BASHRC"
        echo "✓ Shell hook added to $BASHRC"
    fi
fi

ZSHRC="$HOME/.zshrc"
if [ -f "$ZSHRC" ]; then
    if ! grep -q "shellguard.zsh" "$ZSHRC"; then
        echo "source $PWD/shell_plugins/shellguard.zsh" >> "$ZSHRC"
        echo "✓ Shell hook added to $ZSHRC"
    fi
fi

echo "✅ ShellGuard Runtime v1.0.0-rc2 Installation Complete!"
echo "Systemd service: systemctl --user start shellguard-runtime"
