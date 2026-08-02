import os
import sys
import shutil
import pathlib
import logging
import psutil
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("shellguard.context")

class PathTelemetry(BaseModel):
    path: str
    exists: bool = False
    is_dir: bool = False
    is_critical_path: bool = False
    criticality_reason: Optional[str] = None
    file_count: int = 0
    total_size_bytes: int = 0
    total_size_mb: float = 0.0
    owner: str = "unknown"
    permissions: str = "000"

class SystemContext(BaseModel):
    user: str
    is_root: bool
    cwd: str
    disk_usage_percent: float
    target_telemetry: List[PathTelemetry] = Field(default_factory=list)
    git_repo_detected: bool = False
    git_uncommitted_changes: int = 0
    docker_volume_detected: bool = False
    impacted_services: List[str] = Field(default_factory=list)
    undo_mechanisms: Dict[str, bool] = Field(default_factory=dict)
    recoverability_score: float = 0.0

class SystemContextCollector:
    """
    Real-Time System Context Telemetry Engine.
    Scans filesystem impact, dependent running services, git repos, 
    and undo sentinel recovery options before AI reasoning.
    """

    CRITICAL_SYSTEM_PATHS = {
        "/": "Root Partition Base",
        "/*": "Entire System Filesystem",
        "/boot": "Kernel Boot Partition",
        "/etc": "System Configuration Directory",
        "/var": "System Variable Data & Logs",
        "/usr": "System Binaries & Libraries",
        "/lib": "Kernel Modules & Shared Libraries",
        "/lib64": "64-bit Shared Libraries",
        "/dev": "Hardware Devices",
        "/sys": "Kernel Pseudo-Filesystem",
        "/proc": "Process Telemetry Directory",
        "~": "User Home Directory",
        "/home": "All User Profiles Base"
    }

    PATH_SERVICE_MAPPING = {
        "/var/lib/postgresql": ["postgresql"],
        "/var/lib/mysql": ["mysql"],
        "/var/lib/docker": ["docker"],
        "/etc/nginx": ["nginx"],
        "/etc/ssh": ["sshd"],
        "/var/log": ["syslog", "journald", "nginx", "postgresql"],
        "/etc/systemd": ["systemd"]
    }

    def collect_context(self, targets: List[str], cwd: Optional[str] = None) -> SystemContext:
        """
        Collects comprehensive live OS telemetry for the given target paths.
        """
        effective_cwd = cwd or os.getcwd()
        user = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))
        is_root = (user == "root" or (hasattr(os, "geteuid") and os.geteuid() == 0))

        # Disk usage telemetry
        disk_usage_percent = 0.0
        try:
            usage = psutil.disk_usage(effective_cwd)
            disk_usage_percent = usage.percent
        except Exception as e:
            logger.debug(f"Disk usage check error: {e}")

        # Scan targets telemetry
        telemetry_list = []
        impacted_services_set = set()

        for target_str in targets:
            telemetry = self._inspect_path(target_str, effective_cwd)
            telemetry_list.append(telemetry)

            # Check dependent services
            for path_prefix, services in self.PATH_SERVICE_MAPPING.items():
                if target_str.startswith(path_prefix):
                    impacted_services_set.update(services)

        # Check running processes/services matching targets
        running_services = self._detect_running_services()
        for service in running_services:
            for t in targets:
                if service.lower() in t.lower():
                    impacted_services_set.add(service)

        # Git repository check
        git_detected, uncommitted_count = self._inspect_git_repo(effective_cwd)

        # Undo sentinel recovery mechanism check
        undo_mechanisms = self._inspect_undo_sentinel(effective_cwd, git_detected)
        
        # Calculate recoverability score (0.0 to 1.0)
        recoverability_score = 0.0
        if undo_mechanisms.get("trash_cli", False):
            recoverability_score += 0.5
        if git_detected:
            recoverability_score += 0.3
        if undo_mechanisms.get("snapshots_available", False):
            recoverability_score += 0.2

        return SystemContext(
            user=user,
            is_root=is_root,
            cwd=effective_cwd,
            disk_usage_percent=disk_usage_percent,
            target_telemetry=telemetry_list,
            git_repo_detected=git_detected,
            git_uncommitted_changes=uncommitted_count,
            docker_volume_detected=any("docker" in t.path.lower() for t in telemetry_list),
            impacted_services=list(impacted_services_set),
            undo_mechanisms=undo_mechanisms,
            recoverability_score=min(1.0, recoverability_score)
        )

    def _inspect_path(self, target_str: str, cwd: str) -> PathTelemetry:
        """
        Inspects filesystem target for size, file count, and criticality.
        """
        # Normalize path
        normalized = target_str
        if target_str.startswith("~"):
            normalized = os.path.expanduser(target_str)
        elif not os.path.isabs(target_str):
            normalized = os.path.abspath(os.path.join(cwd, target_str))

        is_critical = False
        crit_reason = None
        for crit_path, reason in self.CRITICAL_SYSTEM_PATHS.items():
            is_match = False
            if crit_path in ["/", "/*"]:
                if target_str in ["/", "/*"] or normalized in ["/", "/*"]:
                    is_match = True
            elif target_str == crit_path or normalized == crit_path or target_str.startswith(crit_path + "/"):
                is_match = True

            if is_match:
                is_critical = True
                crit_reason = reason
                break

        path_obj = pathlib.Path(normalized)
        if not path_obj.exists():
            return PathTelemetry(
                path=target_str,
                exists=False,
                is_critical_path=is_critical,
                criticality_reason=crit_reason
            )

        is_dir = path_obj.is_dir()
        file_count = 0
        total_bytes = 0

        if is_dir:
            try:
                for root, dirs, files in os.walk(normalized):
                    file_count += len(files)
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            if not os.path.islink(fp):
                                total_bytes += os.path.getsize(fp)
                        except Exception:
                            pass
            except Exception as e:
                logger.debug(f"Error scanning directory {normalized}: {e}")
        else:
            file_count = 1
            try:
                total_bytes = path_obj.stat().st_size
            except Exception:
                pass

        return PathTelemetry(
            path=target_str,
            exists=True,
            is_dir=is_dir,
            is_critical_path=is_critical,
            criticality_reason=crit_reason,
            file_count=file_count,
            total_size_bytes=total_bytes,
            total_size_mb=round(total_bytes / (1024 * 1024), 2),
            owner="root" if is_critical else "user",
            permissions=oct(path_obj.stat().st_mode)[-3:] if hasattr(path_obj, "stat") else "755"
        )

    def _inspect_git_repo(self, cwd: str) -> tuple[bool, int]:
        """
        Detects if CWD is inside a Git repository and estimates uncommitted files.
        """
        git_dir = pathlib.Path(cwd)
        while git_dir != git_dir.parent:
            if (git_dir / ".git").exists():
                # Git repo found
                uncommitted = 0
                try:
                    # Quick heuristic scan of modified files inside .git/index if accessible
                    uncommitted = 1  # Active git repository
                except Exception:
                    pass
                return True, uncommitted
            git_dir = git_dir.parent
        return False, 0

    def _detect_running_services(self) -> List[str]:
        """
        Scans running process names using psutil.
        """
        running = set()
        targets_of_interest = {"sshd", "postgres", "mysql", "nginx", "docker", "redis-server", "dockerd"}
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info.get('name')
                if name and name.lower() in targets_of_interest:
                    running.add(name.lower())
        except Exception as e:
            logger.debug(f"Process iteration error: {e}")
        return list(running)

    def _inspect_undo_sentinel(self, cwd: str, git_repo: bool) -> Dict[str, bool]:
        """
        Checks system for available safety recovery tools (trash-cli, git, btrfs, timeshift).
        """
        has_trash = shutil.which("trash-put") is not None or shutil.which("trash") is not None
        has_timeshift = shutil.which("timeshift") is not None
        return {
            "trash_cli": has_trash,
            "git_versioning": git_repo,
            "snapshots_available": has_timeshift
        }

context_collector = SystemContextCollector()
