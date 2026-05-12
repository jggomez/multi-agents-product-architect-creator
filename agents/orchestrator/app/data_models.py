from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class FailMode(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

@dataclass
class SecurityValidationResult:
    """Represents the result of a single security check performed by Model Armor."""
    is_safe: bool
    flagged_categories: List[str] = field(default_factory=list)
    sanitized_content: Optional[str] = None
    confidence_score: float = 0.0
    request_id: Optional[str] = None

@dataclass
class SecurityPolicyConfig:
    """Configuration settings for the security layer."""
    project_id: str
    location: str
    template_id: str
    fail_mode: FailMode = FailMode.OPEN
    log_violations: bool = True
