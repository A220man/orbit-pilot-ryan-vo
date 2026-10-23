from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List
from sqlalchemy import (
    String, Text, DateTime, ForeignKey, Enum, Integer, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

from app.core.database import Base


class AuditStatus(str, PyEnum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FindingStatus(str, PyEnum):
    PLANNED = "planned"
    HUNTING = "hunting"
    NEEDS_VALIDATION = "needs_validation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    OUT_OF_SCOPE = "out_of_scope"


class Severity(str, PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    profile: Mapped[str] = mapped_column(String(50), default="standard")  # quick, standard, deep
    status: Mapped[AuditStatus] = mapped_column(Enum(AuditStatus), default=AuditStatus.DRAFT, nullable=False)
    config: Mapped[dict] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    findings: Mapped[List["Finding"]] = relationship(back_populates="audit_run", cascade="all, delete-orphan")
    coverage_ledger: Mapped[Optional["CoverageLedger"]] = relationship(back_populates="audit_run", cascade="all, delete-orphan", uselist=False)

    __table_args__ = (
        Index("ix_audit_runs_status_created", "status", "created_at"),
    )


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_run_id: Mapped[int] = mapped_column(ForeignKey("audit_runs.id", ondelete="CASCADE"), nullable=False)
    unit_id: Mapped[str] = mapped_column(String(128), nullable=False)  # e.g., "auth-bypass-001"
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    attack_class: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[FindingStatus] = mapped_column(Enum(FindingStatus), default=FindingStatus.PLANNED, nullable=False)
    severity: Mapped[Optional[Severity]] = mapped_column(Enum(Severity), nullable=True)
    cwe: Mapped[List[str]] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=list)
    cvss_vector: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    cvss_version: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    references: Mapped[List[dict]] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=list)
    evidence: Mapped[dict] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=dict)
    remediation: Mapped[dict] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=dict)
    preserved_uses: Mapped[List[dict]] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=list)
    method_backed: Mapped[bool] = mapped_column(default=False)
    source_trace: Mapped[dict] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verifier_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    audit_run: Mapped["AuditRun"] = relationship(back_populates="findings")

    __table_args__ = (
        UniqueConstraint("audit_run_id", "unit_id", name="uq_finding_unit_per_run"),
        Index("ix_findings_audit_status", "audit_run_id", "status"),
        Index("ix_findings_class_severity", "attack_class", "severity"),
    )


class CoverageLedger(Base):
    __tablename__ = "coverage_ledger"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_run_id: Mapped[int] = mapped_column(ForeignKey("audit_runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    units: Mapped[List[dict]] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=list)
    attempts: Mapped[List[dict]] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=list)
    promoted_artifacts: Mapped[dict] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_run: Mapped["AuditRun"] = relationship(back_populates="coverage_ledger")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    audit_run_id: Mapped[int] = mapped_column(ForeignKey("audit_runs.id", ondelete="CASCADE"), nullable=False)
    phase: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[dict] = mapped_column(JSON().with_variant(SQLiteJSON, "sqlite"), default=dict)
    actor: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)  # user or agent id
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_logs_run_phase", "audit_run_id", "phase"),
        Index("ix_audit_logs_timestamp", "timestamp"),
    )