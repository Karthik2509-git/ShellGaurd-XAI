# ShellGuard Runtime — Native Fish Shell Preexec Interceptor Hook
# Intercepts commands live inside Fish shell before execution.

function __shellguard_preexec --on-event fish_preexec
    set -l cmd $argv[1]

    # Skip read-only queries
    if string match -r '^(ls|pwd|cd|echo|cat|clear|history)' -- $cmd
        return 0
    end

    if command -v python3 >/dev/null 2>&1
        env PYTHONPATH="$HOME/.local/share/shellguard-runtime/backend:$PYTHONPATH" python3 -m app.interceptor.shellguard_cli "$cmd"
        if test $status -ne 0
            echo -e "\033[0;31m[ShellGuard Runtime] Execution blocked by safety policy.\033[0m"
            return 1
        end
    end
    return 0
end

echo "[ShellGuard Runtime] Native Fish Interceptor Loaded."
