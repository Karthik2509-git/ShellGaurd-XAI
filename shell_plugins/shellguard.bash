#!/usr/bin/env bash
# ShellGuard Runtime — Native Bash Pre-Execution Interceptor Hook
# Intercepts commands live inside gnome-terminal, bash, zsh, kitty before execution.

if [ -z "$SHELLGUARD_HOOK_LOADED" ]; then
    export SHELLGUARD_HOOK_LOADED=1

    _shellguard_preexec() {
        local last_cmd="$BASH_COMMAND"

        # Skip internal/empty/read-only safe queries
        if [[ "$last_cmd" =~ ^(ls|pwd|cd|echo|cat|clear|history|which|whoami) ]]; then
            return 0
        fi

        # Invoke ShellGuard Interceptor CLI in synchronous evaluation mode
        if command -v python >/dev/null 2>&1; then
            python -m app.interceptor.shellguard_cli "$last_cmd"
            local exit_code=$?
            if [ $exit_code -ne 0 ]; then
                echo -e "\033[0;31m[ShellGuard Runtime] Execution cancelled by user safety policy.\033[0m"
                return 1
            fi
        fi
        return 0
    }

    trap '_shellguard_preexec' DEBUG
    echo "[ShellGuard Runtime] Native Bash Interceptor Loaded."
fi
