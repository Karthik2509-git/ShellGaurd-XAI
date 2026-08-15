#!/usr/bin/env zsh
# ShellGuard Runtime — Native Zsh Preexec Interceptor Hook

if [[ -z "$SHELLGUARD_ZSH_HOOK_LOADED" ]]; then
    export SHELLGUARD_ZSH_HOOK_LOADED=1

    shellguard_preexec() {
        # Re-entrancy Guard: Ignore internal ShellGuard processes
        if [[ "${SHELLGUARD_INTERNAL:-0}" -eq 1 ]]; then
            return 0
        fi

        local cmd="$1"

        # Re-entrancy & Internal Command Bypass
        if [[ -z "$cmd" || "$cmd" =~ '_shellguard|shellguard-runtime|app\.interceptor\.shellguard_cli|uvicorn' ]]; then
            return 0
        fi

        # Fast-path bypass for read-only safe queries
        if [[ "$cmd" =~ '^(ls|pwd|cd|echo|cat|clear|history|which|whoami)( |$)' ]]; then
            return 0
        fi

        # Deterministic Python Binary Resolution with Dependency Verification
        local py_bin=""
        local venv_py="$HOME/.local/share/shellguard-runtime/venv/bin/python"
        local venv_py3="$HOME/.local/share/shellguard-runtime/venv/bin/python3"

        if [[ -x "$venv_py" ]] && "$venv_py" -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1; then
            py_bin="$venv_py"
        elif [[ -x "$venv_py3" ]] && "$venv_py3" -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1; then
            py_bin="$venv_py3"
        elif command -v python3 >/dev/null 2>&1 && python3 -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1; then
            py_bin="python3"
        elif command -v python >/dev/null 2>&1 && python -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1; then
            py_bin="python"
        else
            return 0
        fi

        SHELLGUARD_INTERNAL=1 PYTHONPATH="$HOME/.local/share/shellguard-runtime/backend:$PYTHONPATH" "$py_bin" -m app.interceptor.shellguard_cli "$cmd"
        if [[ $? -ne 0 ]]; then
            return 1
        fi
        return 0
    }

    autoload -Uz add-zsh-hook
    add-zsh-hook preexec shellguard_preexec
    echo "[ShellGuard Runtime] Native Zsh Interceptor Loaded."
fi
