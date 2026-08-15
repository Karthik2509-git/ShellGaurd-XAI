#!/usr/bin/env bash
# ShellGuard Runtime — Native Linux Uninstaller Script

set -e

echo "🛡️ Uninstalling ShellGuard Runtime..."

# 1. Stop & Disable Systemd User Service
if command -v systemctl >/dev/null 2>&1; then
    systemctl --user stop shellguard-runtime.service || true
    systemctl --user disable shellguard-runtime.service || true
    echo "✓ Stopped and disabled systemd user service"
fi

SYSTEMD_UNIT="$HOME/.config/systemd/user/shellguard-runtime.service"
if [ -f "$SYSTEMD_UNIT" ]; then
    rm "$SYSTEMD_UNIT"
    if command -v systemctl >/dev/null 2>&1; then
        systemctl --user daemon-reload || true
    fi
fi

# 2. Remove Desktop Entry & Autostart
DESKTOP_FILE="$HOME/.local/share/applications/shellguard-runtime.desktop"
AUTOSTART_FILE="$HOME/.config/autostart/shellguard-runtime.desktop"
[ -f "$DESKTOP_FILE" ] && rm "$DESKTOP_FILE"
[ -f "$AUTOSTART_FILE" ] && rm "$AUTOSTART_FILE"
echo "✓ Removed Desktop Entry & Autostart"

# 3. Remove Binary Executable Wrapper
BIN_WRAPPER="$HOME/.local/bin/shellguard-runtime-daemon"
[ -f "$BIN_WRAPPER" ] && rm "$BIN_WRAPPER"
echo "✓ Removed binary executable wrapper"

# 4. Remove Shell Hooks from Shell Configs
if [ -f "$HOME/.bashrc" ]; then
    sed -i '/shellguard.bash/d' "$HOME/.bashrc"
    echo "✓ Cleaned shell hook from ~/.bashrc"
fi

if [ -f "$HOME/.zshrc" ]; then
    sed -i '/shellguard.zsh/d' "$HOME/.zshrc"
    echo "✓ Cleaned shell hook from ~/.zshrc"
fi

if [ -f "$HOME/.config/fish/config.fish" ]; then
    sed -i '/shellguard.fish/d' "$HOME/.config/fish/config.fish"
    echo "✓ Cleaned shell hook from ~/.config/fish/config.fish"
fi

# 5. Remove Application Payload (Preserving User Config & Logs)
[ -d "$HOME/.local/share/shellguard-runtime" ] && rm -rf "$HOME/.local/share/shellguard-runtime"

echo "✅ ShellGuard Runtime successfully uninstalled (User settings preserved in ~/.config/shellguard-runtime)."
