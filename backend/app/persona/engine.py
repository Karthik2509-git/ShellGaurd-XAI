import logging
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger("shellguard.persona")

class OperatorRole(str, Enum):
    BEGINNER = "BEGINNER"
    DEVELOPER = "DEVELOPER"
    SYSADMIN = "SYSADMIN"

class PersonaProfile(BaseModel):
    role: OperatorRole
    confirmation_risk_threshold: int
    explainability_detail_level: str
    auto_apply_safe_alternatives: bool

class PersonaEngine:
    """
    Self-Learning Persona & Skill Level Engine.
    Adjusts risk sensitivity and warning friction dynamically based on operator role.
    """

    PROFILES = {
        OperatorRole.BEGINNER: PersonaProfile(
            role=OperatorRole.BEGINNER,
            confirmation_risk_threshold=40,
            explainability_detail_level="ELI5",
            auto_apply_safe_alternatives=True
        ),
        OperatorRole.DEVELOPER: PersonaProfile(
            role=OperatorRole.DEVELOPER,
            confirmation_risk_threshold=60,
            explainability_detail_level="TECHNICAL",
            auto_apply_safe_alternatives=False
        ),
        OperatorRole.SYSADMIN: PersonaProfile(
            role=OperatorRole.SYSADMIN,
            confirmation_risk_threshold=80,
            explainability_detail_level="TECHNICAL_EXPERT",
            auto_apply_safe_alternatives=False
        )
    }

    def get_profile(self, role: OperatorRole = OperatorRole.DEVELOPER) -> PersonaProfile:
        return self.PROFILES.get(role, self.PROFILES[OperatorRole.DEVELOPER])

persona_engine = PersonaEngine()
