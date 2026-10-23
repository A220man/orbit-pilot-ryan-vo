from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class AuditStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FindingStatus(str, Enum):
    PLANNED = "planned"
    HUNTING = "hunting"
    NEEDS_VALIDATION = "needs_validation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    OUT_OF_SCOPE = "out_of_scope"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class AuditRunBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    target_path: str = Field(..., min_length=1, max_length=1024)
    profile: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    config: Dict[str, Any] = Field(default_factory=dict)


class AuditRunCreate(AuditRunBase):
    pass


class AuditRunUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[AuditStatus] = None
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AuditRunResponse(AuditRunBase):
    id: int
    status: AuditStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class FindingBase(BaseModel):
    unit_id: str = Field(..., min_length=1, max_length=128)
    title: str = Field(..., min_length=1, max_length=512)
    description: str
    attack_class: str = Field(..., min_length=1, max_length=128)
    severity: Optional[Severity] = None
    cwe: List[str] = Field(default_factory=list)
    cvss_vector: Optional[str] = None
    cvss_version: Optional[str] = None
    references: List[Dict[str, Any]] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    remediation: Dict[str, Any] = Field(default_factory=dict)
    preserved_uses: List[Dict[str, Any]] = Field(default_factory=list)
    method_backed: bool = False
    source_trace: Dict[str, Any] = Field(default_factory=dict)


class FindingCreate(FindingBase):
    pass


class FindingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=512)
    description: Optional[str] = None
    attack_class: Optional[str] = Field(None, min_length=1, max_length=128)
    status: Optional[FindingStatus] = None
    severity: Optional[Severity] = None
    cwe: Optional[List[str]] = None
    cvss_vector: Optional[str] = None
    cvss_version: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None
    evidence: Optional[Dict[str, Any]] = None
    remediation: Optional[Dict[str, Any]] = None
    preserved_uses: Optional[List[Dict[str, Any]]] = None
    method_backed: Optional[bool] = None
    source_trace: Optional[Dict[str, Any]] = None
    verifier_notes: Optional[str] = None


class FindingResponse(FindingBase):
    id: int
    audit_run_id: int
    status: FindingStatus
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None
    verifier_notes: Optional[str] = None

    class Config:
        from_attributes = True


class CoverageLedgerUnit(BaseModel):
    unit_id: str
    title: str
    attack_class: str
    status: FindingStatus
    files: List[str] = Field(default_factory=list)
    assigned_to: Optional[str] = None


class CoverageLedgerAttempt(BaseModel):
    attempt_id: int
    phase: str
    units_targeted: List[str]
    units_completed: List[str]
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)


class CoverageLedgerBase(BaseModel):
    units: List[CoverageLedgerUnit] = Field(default_factory=list)
    attempts: List[CoverageLedgerAttempt] = Field(default_factory=list)
    promoted_artifacts: Dict[str, Any] = Field(default_factory=dict)


class CoverageLedgerResponse(CoverageLedgerBase):
    audit_run_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditLogEntry(BaseModel):
    id: int
    audit_run_id: int
    phase: str
    action: str
    details: Dict[str, Any]
    actor: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str