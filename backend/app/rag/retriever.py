import logging
from typing import List, Dict, Any

logger = logging.getLogger("shellguard.rag")

class LinuxRAGRetriever:
    """
    RAG Retriever for Linux Security Benchmarks, Man Pages, and GNU Docs.
    """

    LINUX_SECURITY_KNOWLEDGE_BASE = {
        "rm": {
            "source": "GNU Coreutils Man Page (rm)",
            "guideline": "By default, rm does not remove directories. Use trash-cli or --interactive to prevent unrecoverable data loss. Never pass -rf to root / or critical paths.",
            "cis_benchmark": "CIS Linux 1.8: Enforce strict file deletion auditing & restrict unlinking system binary directories."
        },
        "chmod": {
            "source": "Arch Linux Security & CIS Benchmark 2.1",
            "guideline": "Never set 777 (read-write-execute) permissions on system or web directories. Use principle of least privilege: 755 for directories, 644 for files.",
            "cis_benchmark": "CIS Linux 2.1.4: Restrict world-writable files and directories."
        },
        "killall": {
            "source": "Linux System Administration Manual",
            "guideline": "killall sends SIGTERM or SIGKILL to all processes matching name. Use systemctl stop/reload or pkill -f for targeted process lifecycle control.",
            "cis_benchmark": "CIS Linux 3.2: Service Availability Guard"
        }
    }

    def retrieve_guidelines(self, base_command: str) -> List[Dict[str, str]]:
        """
        Retrieves authoritative Linux security guidelines and CIS benchmark entries.
        """
        base = base_command.lower()
        if base in self.LINUX_SECURITY_KNOWLEDGE_BASE:
            item = self.LINUX_SECURITY_KNOWLEDGE_BASE[base]
            return [item]
        
        return [{
            "source": "Linux Security Guide",
            "guideline": f"Verify privileges and target paths before executing '{base_command}'.",
            "cis_benchmark": "CIS Linux 1.1: General System Hardening"
        }]

rag_retriever = LinuxRAGRetriever()
