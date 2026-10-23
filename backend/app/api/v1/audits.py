from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import AuditRun, Finding, CoverageLedger, AuditLog, AuditStatus, FindingStatus
from app.schemas import (
    AuditRunCreate, AuditRunUpdate, AuditRunResponse,
    FindingCreate, FindingUpdate, FindingResponse,
    CoverageLedgerResponse, AuditLogEntry, HealthResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    from app.core.config import settings
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.APP_ENV,
    )


# Audit Runs
@router.post("/audits", response_model=AuditRunResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_run(payload: AuditRunCreate, db: AsyncSession = Depends(get_db)):
    audit = AuditRun(
        name=payload.name,
        target_path=payload.target_path,
        profile=payload.profile,
        config=payload.config,
        status=AuditStatus.DRAFT,
    )
    db.add(audit)
    await db.flush()
    
    # Create empty coverage ledger
    ledger = CoverageLedger(audit_run_id=audit.id)
    db.add(ledger)
    
    # Log creation
    log = AuditLog(audit_run_id=audit.id, phase="init", action="created", details={"profile": payload.profile})
    db.add(log)
    
    await db.commit()
    await db.refresh(audit)
    return audit


@router.get("/audits", response_model=List[AuditRunResponse])
async def list_audit_runs(
    status: Optional[AuditStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditRun).order_by(AuditRun.created_at.desc()).limit(limit).offset(offset)
    if status:
        query = query.where(AuditRun.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/audits/{audit_id}", response_model=AuditRunResponse)
async def get_audit_run(audit_id: int, db: AsyncSession = Depends(get_db)):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    return audit


@router.patch("/audits/{audit_id}", response_model=AuditRunResponse)
async def update_audit_run(audit_id: int, payload: AuditRunUpdate, db: AsyncSession = Depends(get_db)):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(audit, field, value)
    
    if payload.status == AuditStatus.RUNNING and not audit.started_at:
        audit.started_at = datetime.utcnow()
    if payload.status in (AuditStatus.COMPLETED, AuditStatus.FAILED, AuditStatus.CANCELLED) and not audit.completed_at:
        audit.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(audit)
    return audit


@router.delete("/audits/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_run(audit_id: int, db: AsyncSession = Depends(get_db)):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    await db.delete(audit)
    await db.commit()


# Findings
@router.get("/audits/{audit_id}/findings", response_model=List[FindingResponse])
async def list_findings(
    audit_id: int,
    status: Optional[FindingStatus] = None,
    attack_class: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    query = select(Finding).where(Finding.audit_run_id == audit_id).order_by(Finding.created_at.desc()).limit(limit).offset(offset)
    if status:
        query = query.where(Finding.status == status)
    if attack_class:
        query = query.where(Finding.attack_class == attack_class)
    if severity:
        query = query.where(Finding.severity == severity)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/audits/{audit_id}/findings/{finding_id}", response_model=FindingResponse)
async def get_finding(audit_id: int, finding_id: int, db: AsyncSession = Depends(get_db)):
    finding = await db.get(Finding, finding_id)
    if not finding or finding.audit_run_id != audit_id:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.post("/audits/{audit_id}/findings", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(audit_id: int, payload: FindingCreate, db: AsyncSession = Depends(get_db)):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    # Check unit_id uniqueness within audit run
    existing = await db.execute(
        select(Finding).where(Finding.audit_run_id == audit_id, Finding.unit_id == payload.unit_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Finding with unit_id '{payload.unit_id}' already exists")
    
    finding = Finding(audit_run_id=audit_id, **payload.model_dump())
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.patch("/audits/{audit_id}/findings/{finding_id}", response_model=FindingResponse)
async def update_finding(audit_id: int, finding_id: int, payload: FindingUpdate, db: AsyncSession = Depends(get_db)):
    finding = await db.get(Finding, finding_id)
    if not finding or finding.audit_run_id != audit_id:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(finding, field, value)
    
    if payload.status == FindingStatus.CONFIRMED and not finding.verified_at:
        finding.verified_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(finding)
    return finding


# Coverage Ledger
@router.get("/audits/{audit_id}/coverage", response_model=CoverageLedgerResponse)
async def get_coverage_ledger(audit_id: int, db: AsyncSession = Depends(get_db)):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    ledger = await db.execute(
        select(CoverageLedger).where(CoverageLedger.audit_run_id == audit_id)
    )
    ledger = ledger.scalar_one_or_none()
    if not ledger:
        # Create empty ledger
        ledger = CoverageLedger(audit_run_id=audit_id)
        db.add(ledger)
        await db.commit()
        await db.refresh(ledger)
    
    return ledger


# Audit Logs
@router.get("/audits/{audit_id}/logs", response_model=List[AuditLogEntry])
async def get_audit_logs(audit_id: int, limit: int = 200, db: AsyncSession = Depends(get_db)):
    audit = await db.get(AuditRun, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    query = select(AuditLog).where(AuditLog.audit_run_id == audit_id).order_by(AuditLog.timestamp.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()