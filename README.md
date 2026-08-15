# 🛡️ ShellGuard Runtime `v1.0.0-rc3`

> **"Before Linux executes a command, ShellGuard Runtime understands what the user actually means."**  
> *Linux understands commands. ShellGuard Runtime understands intentions.*

ShellGuard Runtime is an **AI-powered Operating System Safety Layer** built natively for Linux. It runs continuously as a background daemon, monitors terminal execution telemetry before commands hit the kernel, evaluates intent and blast radius using deterministic rule engines, explains risks clearly, and recommends safer alternatives.

---

## 🏛️ Systems Architecture & Pipeline

```
Linux Shell (Bash / Zsh / Fish)
        │
        ▼
ShellGuard Runtime Service (systemd --user daemon)
        │
 ┌──────┼────────┐
 │      │        │
 ▼      ▼        ▼
Evidence Context OS Events
        │
        ▼
Policy Engine (Learning, Normal, Strict, Enterprise)
        │
        ▼
Rule Engine (Deterministic Policy Verification)
        │
        ▼
Safety Engine (Adaptive Risk Vector Matrix & System Trust)
        │
        ▼
Explanation Engine (Dual Rationales & Rewrites)
        │
        ▼
IPC Layer (WebSocket & Local Domain Sockets)
        │
        ▼
ShellGuard Runtime UI & Tray Applet
 ├── Desktop System Tray Status Bar (Green / Yellow / Orange / Red)
 ├── Floating Shield Widget
 ├── Impact Report & Sandbox Preview
 ├── CrowdStrike Threat Timeline
 ├── Safe Command Rewrites
 └── Control Center Dashboard
```

---

## 📊 Shell & Terminal Emulator Compatibility Matrix

| Terminal / Shell | Support Level | Interception Latency | Hook mechanism |
| :--- | :--- | :--- | :--- |
| **Bash 4.4+** | `Supported` | `< 12ms` | `trap DEBUG` preexec hook |
| **Zsh 5.8+** | `Supported` | `< 10ms` | `add-zsh-hook preexec` |
| **Fish 3.0+** | `Supported` | `< 14ms` | `fish_preexec` event handler |
| **GNOME Terminal** | `Supported` | Native | Supported via XDG Desktop Entry |
| **Kitty Terminal** | `Supported` | Native | Supported via GPU-accelerated ANSI |
| **Konsole (KDE)** | `Supported` | Native | Supported via KDE tray applet |
| **tmux / screen** | `Supported` | Sub-session | Preserves multi-pane environment variables |

---

## 📁 XDG Base Directory Compliance

ShellGuard Runtime strictly adheres to the **Freedesktop XDG Base Directory Specification**:

- **Configuration**: `~/.config/shellguard-runtime/`
- **State & Logs**: `~/.local/state/shellguard-runtime/`
- **Cache**: `~/.cache/shellguard-runtime/`

---

## ⚙️ Systemd User Service Management

```bash
# Start background daemon
systemctl --user start shellguard-runtime.service

# Check service status
systemctl --user status shellguard-runtime.service

# Enable automatic startup on login
systemctl --user enable shellguard-runtime.service

# Stop background daemon
systemctl --user stop shellguard-runtime.service
```

---

## 🚀 Quickstart & Native Installation

```bash
# 1. Run Native Linux Installer Script
chmod +x install.sh
./install.sh

# 2. Run Test Suite
python -m pytest backend/tests
```

---

## 📜 Release Information

- **Semantic Version**: `v1.0.0-rc3`
- **Build Number**: `20260803.2`
- **Commit Hash**: `dd9f988`
- **License**: MIT
