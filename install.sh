#!/usr/bin/env bash
# ShellGuard Runtime v1.0.0-rc3 — Native Linux Installer Script
# Installs Freedesktop Entry, systemd --user service, XDG directories, and shell hooks.

set -e

echo "🛡️ Installing ShellGuard Runtime v1.0.0-rc3..."

# 1. XDG Base Directory Structure
XDG_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/shellguard-runtime"
XDG_STATE="${XDG_STATE_HOME:-$HOME/.local/state}/shellguard-runtime"
XDG_CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/shellguard-runtime"
BIN_DIR="$HOME/.local/bin"
SHARE_DIR="$HOME/.local/share/shellguard-runtime"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
AUTOSTART_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
SYSTEMD_USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

mkdir -p "$XDG_CONFIG" "$XDG_STATE" "$XDG_CACHE" "$BIN_DIR" "$SHARE_DIR" "$DESKTOP_DIR" "$AUTOSTART_DIR" "$SYSTEMD_USER_DIR"
echo "✓ Registered XDG directories ($XDG_CONFIG)"

# 2. Deploy Application Payload
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$SHARE_DIR/backend" "$SHARE_DIR/shell_plugins"
cp -r "$SCRIPT_DIR/backend/"* "$SHARE_DIR/backend/"
cp -r "$SCRIPT_DIR/shell_plugins/"* "$SHARE_DIR/shell_plugins/"

# Setup Python Virtual Environment & Install Bundled Dependencies
if command -v python3 >/dev/null 2>&1; then
    echo "ℹ️  Configuring Python virtual environment in $SHARE_DIR/venv..."
    if [ -d "$SHARE_DIR/venv" ] && [ ! -f "$SHARE_DIR/venv/bin/pip" ]; then
        rm -rf "$SHARE_DIR/venv"
    fi
    if [ ! -d "$SHARE_DIR/venv" ]; then
        python3 -m venv "$SHARE_DIR/venv" 2>/dev/null || true
    fi

    if [ -f "$SHARE_DIR/venv/bin/pip" ]; then
        echo "ℹ️  Installing bundled Python dependencies..."
        "$SHARE_DIR/venv/bin/pip" install --quiet -r "$SHARE_DIR/backend/requirements.txt" || echo "⚠️  Warning: Virtual environment pip install returned non-zero exit code."
    else
        echo "⚠️  Warning: Could not create Python virtualenv ($SHARE_DIR/venv/bin/pip missing)."
        echo "   Please install python3-venv / python3-pip on Ubuntu/Debian via:"
        echo "   sudo apt install -y python3-venv python3-pip"
    fi
fi

# Create Daemon Binary Wrapper Executable
cat << 'EOF' > "$BIN_DIR/shellguard-runtime-daemon"
#!/usr/bin/env bash
# ShellGuard Runtime Daemon Executable Wrapper
export PYTHONUNBUFFERED=1
SHARE_DIR="$HOME/.local/share/shellguard-runtime"
export PYTHONPATH="$SHARE_DIR/backend:$PYTHONPATH"

if [ -f "$SHARE_DIR/venv/bin/python" ]; then
    exec "$SHARE_DIR/venv/bin/python" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 "$@"
else
    exec python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 "$@"
fi
EOF
chmod +x "$BIN_DIR/shellguard-runtime-daemon"
echo "✓ Created binary wrapper ($BIN_DIR/shellguard-runtime-daemon)"

# 3. Copy Desktop Entry & Autostart
if [ -f "$SHARE_DIR/shell_plugins/shellguard-runtime.desktop" ]; then
    cp "$SHARE_DIR/shell_plugins/shellguard-runtime.desktop" "$DESKTOP_DIR/"
    cp "$SHARE_DIR/shell_plugins/shellguard-runtime.desktop" "$AUTOSTART_DIR/"
    echo "✓ Installed Freedesktop Entry & Autostart"
fi

# 4. Register Systemd User Service
if [ -f "$SHARE_DIR/shell_plugins/shellguard-runtime.service" ]; then
    cp "$SHARE_DIR/shell_plugins/shellguard-runtime.service" "$SYSTEMD_USER_DIR/"
    if command -v systemctl >/dev/null 2>&1; then
        systemctl --user daemon-reload || true
        systemctl --user enable shellguard-runtime.service || true
        echo "✓ Registered systemd user service (shellguard-runtime.service)"
    fi
fi

# 5. Register Shell Hooks (Bash, Zsh, Fish)
HOOK_CMD="source \"$SHARE_DIR/shell_plugins/shellguard.bash\""
BASHRC="$HOME/.bashrc"
if [ -f "$BASHRC" ]; then
    if ! grep -q "shellguard.bash" "$BASHRC"; then
        echo "$HOOK_CMD" >> "$BASHRC"
        echo "✓ Shell hook added to $BASHRC"
    fi
fi

ZSH_HOOK_CMD="source \"$SHARE_DIR/shell_plugins/shellguard.zsh\""
ZSHRC="$HOME/.zshrc"
if [ -f "$ZSHRC" ]; then
    if ! grep -q "shellguard.zsh" "$ZSHRC"; then
        echo "$ZSH_HOOK_CMD" >> "$ZSHRC"
        echo "✓ Shell hook added to $ZSHRC"
    fi
fi

FISH_HOOK_CMD="source \"$SHARE_DIR/shell_plugins/shellguard.fish\""
FISHCONFIG="$HOME/.config/fish/config.fish"
if [ -f "$FISHCONFIG" ]; then
    if ! grep -q "shellguard.fish" "$FISHCONFIG"; then
        echo "$FISH_HOOK_CMD" >> "$FISHCONFIG"
        echo "✓ Shell hook added to $FISHCONFIG"
    fi
fi

echo "✅ ShellGuard Runtime v1.0.0-rc3 Installation Complete!"
echo "To start runtime service: systemctl --user start shellguard-runtime"
