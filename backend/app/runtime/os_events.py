import time
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger("shellguard.runtime.events")

class OSEvent(BaseModel):
    timestamp: str
    event_type: str  # USB_MOUNTED, SUDO_PRIVILEGE_REQUEST, SERVICE_STOPPED, LARGE_FILE_DELETION
    description: str
    severity: str    # SAFE, CAUTION, HIGH, CRITICAL
    source_process: str = "kernel/systemd"

class OSEventMonitor:
    """
    OS System Event Awareness Engine.
    Observes OS-level events (USB mounts, sudo privilege escalations, systemd drops)
    and surfaces them in the CrowdStrike Threat Timeline.
    """

    def __init__(self):
        self.events_log: List[OSEvent] = [
            OSEvent(
                timestamp="11:05:12",
                event_type="SUDO_PRIVILEGE_REQUEST",
                description="Process 'bash' (PID 1420) requested root sudo escalation",
                severity="CAUTION",
                source_process="sudo/pam"
            ),
            OSEvent(
                timestamp="11:02:44",
                event_type="USB_MOUNTED",
                description="External USB block device mounted at /media/user/SANDISK_32G",
                severity="SAFE",
                source_process="udev/udisks2"
            )
        ]

    def get_recent_events(self) -> List[OSEvent]:
        return self.events_log

    def log_event(self, event_type: str, description: str, severity: str = "CAUTION"):
        current_time = time.strftime("%H:%M:%S")
        evt = OSEvent(
            timestamp=current_time,
            event_type=event_type,
            description=description,
            severity=severity
        )
        self.events_log.insert(0, evt)
        if len(self.events_log) > 50:
            self.events_log.pop()
        return evt

os_event_monitor = OSEventMonitor()
