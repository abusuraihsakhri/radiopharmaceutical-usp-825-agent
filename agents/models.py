"""
Pydantic v2 schemas and data definitions for Radiopharmaceutical Usp 825 Agent.
Domain: Nuclear Pharmacy (demonstration)
Standard: Generic demonstration thresholds; not USP <825> criteria
"""
import datetime
import re
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class UrgencyLevel(str, Enum):
    ROUTINE = "ROUTINE"
    ELEVATED = "ELEVATED_RISK"
    CRITICAL_STAT = "CRITICAL_STAT_PANIC"


class SystemIntegrityStatus(str, Enum):
    VALIDATED = "VALIDATED_OPTIMAL"
    DISCORDANT = "DISCORDANT_ANOMALY"
    RECALIBRATION_REQUIRED = "RECALIBRATION_REQUIRED"


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9._\-]{1,128}$")
_METRIC_MAX = 1_000_000.0


class SystemTaskPayload(BaseModel):
    task_id: str = Field(..., description="Unique task / case identifier")
    target_identifier: str = Field(..., description="Synthetic sample identifier; do not enter PHI")
    primary_metric: float = Field(..., description="Primary domain measurement or score")
    secondary_metric: float = Field(default=0.0, description="Secondary kinetic or confidence score")
    status_descriptor: str = Field(default="NOMINAL", description="Status code or phenotype descriptor")
    is_critical_flag: bool = Field(default=False, description="Emergency escalation or high priority trigger")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    @field_validator("task_id", "target_identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not _IDENTIFIER_PATTERN.match(v):
            raise ValueError(
                f"Identifier must match pattern {_IDENTIFIER_PATTERN.pattern} (alphanumeric, dash, dot, underscore; max 128 chars)"
            )
        return v

    @field_validator("primary_metric", "secondary_metric")
    @classmethod
    def validate_metric(cls, v: float) -> float:
        if not (-_METRIC_MAX <= v <= _METRIC_MAX):
            raise ValueError(f"Metric value must be between -{_METRIC_MAX} and {_METRIC_MAX}")
        return v


class AgentAlert(BaseModel):
    alert_id: str
    origin_worker: str
    urgency: UrgencyLevel
    summary: str
    technical_details: str
    actionable_remediation: str
    standard_reference: str = "Generic demonstration thresholds; not USP <825> criteria"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class ConsensusDossier(BaseModel):
    dossier_id: str
    system_slug: str = "radiopharmaceutical-usp-825-agent"
    domain: str = "Nuclear Pharmacy (demonstration)"
    task_id: str
    target_identifier: str
    overall_urgency: UrgencyLevel
    integrity_status: SystemIntegrityStatus
    total_alerts: int
    critical_alerts_count: int
    alerts: List[AgentAlert]
    standard_reference: str = "Generic demonstration thresholds; not USP <825> criteria"
    consensus_summary: str
    audit_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
