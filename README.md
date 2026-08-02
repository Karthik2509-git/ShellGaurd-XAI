# 🛡️ ShellGuard Runtime — OS-Native Linux Safety Layer

> **"Before Linux executes a command, ShellGuard Runtime understands what the user actually means."**  
> *Linux understands commands. ShellGuard Runtime understands intentions.*

---

[![FastAPI](https://img.shields.io/badge/FastAPI-v0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-v14-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-v3.14-3776AB?style=flat-square&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-v5.0-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

---

## 📌 Executive Overview

Linux provides unrestricted, powerful root access via shell commands. However, single accidental or obfuscated operations such as `rm -rf /` or `chmod -R 777 /` can cause irreversible system damage and downtime.

Current security mechanisms rely on user permissions, `sudo` authentication, command history, and static rules—**none of which understand user intent**.

**ShellGuard Runtime** is an intelligent, low-latency OS safety layer that intercepts commands, inspects filesystem telemetry, evaluates security policies, calculates multi-vector safety ratings, and explains consequences *before* execution occurs.

---

## 📜 Five Design Principles (Engineering Philosophy)

1. **Predict before Execute**: Understand intent before execution.
2. **Explain every Decision**: Never block without explanation.
3. **Privacy First**: Everything runs locally whenever possible.
4. **Human Always Decides**: The Runtime recommends. The user remains in control.
5. **Deterministic Before Generative**: Rule Engine first. LLM second.

---

## 🏛️ Master Systems Architecture Pipeline

```
Linux Shell (Bash / Zsh / Fish)
        │
        ▼
ShellGuard Runtime Service
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
Safety Engine (Adaptive Risk Vector Matrix)
        │
        ▼
Explanation Engine (Dual Rationales & Rewrites)
        │
        ▼
IPC Layer (WebSocket & Local Domain Sockets)
        │
        ▼
ShellGuard Runtime UI
 ├── Floating Shield Widget
 ├── Impact Report & Sandbox Preview
 ├── CrowdStrike Threat Timeline
 ├── Safe Command Rewrites
 └── Control Center Dashboard
```

---

## ✨ Key Capabilities & Innovations

- **🔒 Rule Engine Decision Authority**: Deterministic policy rules make the final `PASS`, `WARN`, or `BLOCK` decision. The Explanation Engine generates clear technical and ELI5 rationales.
- **🛡️ Policy Engine**: Operates in 4 dynamic modes (`Learning`, `Normal`, `Strict`, `Enterprise`).
- **📊 Impact Report**: Provides evidence checkmarks, failure likelihood ratings (`Very High`), recovery complexity (`Critical`), and component progress bars.
- **⚡ Sub-Millisecond Processing Telemetry**: Evaluates end-to-end command safety pipeline in **42ms**.
- **🧪 Sandbox Preview**: Runs commands in an isolated virtual clone environment to observe simulated destruction before touching disk.
- **🔐 Trust Mode (`I UNDERSTAND`)**: Production safety override requiring explicit text confirmation (`I UNDERSTAND`) to execute blocked operations.
- **✨ Safe Command Rewrites**: Automatically suggests production-grade alternatives (e.g. converting `chmod -R 777 proj/` into `chmod 755 proj/ && find proj -type f -exec chmod 644 {} +`).
- **📜 Threat Timeline**: CrowdStrike-style security audit log tracking real-time shell executions and system events.

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 1. Start ShellGuard Runtime Service (Backend)

```bash
cd backend
python -m venv venv
# On Linux/macOS: source venv/bin/activate
# On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start ShellGuard Runtime UI (Control Center)

```bash
cd frontend
npm install
npm run dev
```

Open **`http://localhost:3000`** to open the Control Center dashboard.

---

## 🧪 Running Automated Tests

Run the complete 28-test Pytest verification suite:

```bash
python -m pytest backend/tests
```

---

## 🤝 License

Distributed under the MIT License.
