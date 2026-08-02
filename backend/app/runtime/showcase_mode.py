import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger("shellguard.runtime.showcase")

class PresentationScenario(BaseModel):
    id: str
    name: str
    command: str
    description: str
    expected_threat_level: str

class ShowcaseModeEngine:
    """
    🎬 Presentation Mode Engine.
    Preloads 5 offline presentation scenarios ensuring zero presentation failure
    during hackathon judge demonstrations.
    """

    def __init__(self):
        self.scenarios: List[PresentationScenario] = [
            PresentationScenario(
                id="scenario-1",
                name="Scenario 1: Safe Execution",
                command="ls -la /tmp",
                description="Standard read-only directory query",
                expected_threat_level="SAFE"
            ),
            PresentationScenario(
                id="scenario-2",
                name="Scenario 2: Recoverable Cleanup",
                command="rm notes.txt",
                description="Storage cleanup with trash-put alternative",
                expected_threat_level="CAUTION"
            ),
            PresentationScenario(
                id="scenario-3",
                name="Scenario 3: Permission Modification",
                command="chmod -R 777 project/",
                description="Global permissive permission grant",
                expected_threat_level="HIGH"
            ),
            PresentationScenario(
                id="scenario-4",
                name="Scenario 4: Critical OS System Block",
                command="sudo rm -rf /etc",
                description="Root filesystem deletion targeting system configs",
                expected_threat_level="CRITICAL"
            ),
            PresentationScenario(
                id="scenario-5",
                name="Scenario 5: OS Event Awareness",
                command="systemctl stop postgresql",
                description="Background database service termination",
                expected_threat_level="CAUTION"
            ),
        ]

    def get_scenarios(self) -> List[PresentationScenario]:
        return self.scenarios

showcase_engine = ShowcaseModeEngine()
