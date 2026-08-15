# ShellGuard Runtime — Native Fish Shell Preexec Interceptor Hook
# Intercepts commands live inside Fish shell before execution.

function __shellguard_preexec --on-event fish_preexec
    # Re-entrancy Guard: Ignore internal ShellGuard processes
    if test "$SHELLGUARD_INTERNAL" = "1"
        return 0
    end

    set -l cmd $argv[1]

    # Re-entrancy & Internal Command Bypass
    if test -z "$cmd"; or string match -q -r '_shellguard|shellguard-runtime|app\.interceptor\.shellguard_cli|uvicorn' -- $cmd
        return 0
    end

    # Skip read-only queries
    if string match -q -r '^(ls|pwd|cd|echo|cat|clear|history|which|whoami)(\s|$)' -- $cmd
        return 0
    end

    # Deterministic Python Binary Resolution with Dependency Verification
    set -l py_bin ""
    set -l venv_py "$HOME/.local/share/shellguard-runtime/venv/bin/python"
    set -l venv_py3 "$HOME/.local/share/shellguard-runtime/venv/bin/python3"

    if test -x "$venv_py"; and "$venv_py" -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1
        set py_bin "$venv_py"
    else if test -x "$venv_py3"; and "$venv_py3" -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1
        set py_bin "$venv_py3"
    else if command -v python3 >/dev/null 2>&1; and python3 -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1
        set py_bin "python3"
    else if command -v python >/dev/null 2>&1; and python -c "import httpx, fastapi, pydantic, bashlex" >/dev/null 2>&1
        set py_bin "python"
    else
        return 0
    end

    env SHELLGUARD_INTERNAL=1 PYTHONPATH="$HOME/.local/share/shellguard-runtime/backend:$PYTHONPATH" $py_bin -m app.interceptor.shellguard_cli "$cmd"
    if test $status -ne 0
        echo -e "\033[0;31m[ShellGuard Runtime] Execution blocked by safety policy.\033[0m"
        return 1
    end
    return 0
end

echo "[ShellGuard Runtime] Native Fish Interceptor Loaded."
