#!/usr/bin/env zsh
# ShellGuard Runtime — Native Zsh Preexec Interceptor Hook

if [[ -z "$SHELLGUARD_ZSH_HOOK_LOADED" ]]; then
    export SHELLGUARD_ZSH_HOOK_LOADED=1

    shellguard_preexec() {
        local cmd="$1"
        if [[ "$cmd" =~ ^(ls|pwd|cd|echo|cat|clear|history) ]]; then
            return 0
        fi

        if command -v python >/dev/null 2>&1; then
            python -m app.interceptor.shellguard_cli "$cmd"
            if [[ $? -ne 0 ]]; then
                return 1
            fi
        fi
        return 0
    }

    autoload -Uz add-zsh-hook
    add-zsh-hook preexec shellguard_preexec
    echo "[ShellGuard Runtime] Native Zsh Interceptor Loaded."
fi
