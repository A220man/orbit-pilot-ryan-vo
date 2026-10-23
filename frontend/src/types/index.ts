export type AuditStatus = 'draft' | 'running' | 'completed' | 'failed' | 'cancelled'

export type FindingStatus = 
  | 'planned' 
  | 'hunting' 
  | 'needs_validation' 
  | 'confirmed' 
  | 'rejected' 
  | 'deferred' 
  | 'out_of_scope'

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'informational'

export type Profile = 'quick' | 'standard' | 'deep'

export interface AuditRun {
  id: number
  name: string
  target_path: string
  profile: Profile
  status: AuditStatus
  config: Record<string, any>
  created_at: string
  started_at: string | null
  completed_at: string | null
  error: string | null
}

export interface Finding {
  id: number
  audit_run_id: number
  unit_id: string
  title: string
  description: string
  attack_class: string
  status: FindingStatus
  severity: Severity | null
  cwe: string[]
  cvss_vector: string | null
  cvss_version: string | null
  references: Array<{ url: string }>
  evidence: Record<string, any>
  remediation: Record<string, any>
  preserved_uses: Array<{ who: string; path: string; how_it_keeps_working: string }>
  method_backed: boolean
  source_trace: Record<string, any>
  created_at: string
  updated_at: string
  verified_at: string | null
  verifier_notes: string | null
}

export interface CoverageLedgerUnit {
  unit_id: string
  title: string
  attack_class: string
  status: FindingStatus
  files: string[]
  assigned_to: string | null
}

export interface CoverageLedgerAttempt {
  attempt_id: number
  phase: string
  units_targeted: string[]
  units_completed: string[]
  artifacts: Array<Record<string, any>>
}

export interface CoverageLedger {
  audit_run_id: number
  units: CoverageLedgerUnit[]
  attempts: CoverageLedgerAttempt[]
  promoted_artifacts: Record<string, any>
  created_at: string
  updated_at: string
}

export interface AuditLogEntry {
  id: number
  audit_run_id: number
  phase: string
  action: string
  details: Record<string, any>
  actor: string | null
  timestamp: string
}

export interface HealthResponse {
  status: string
  version: string
  environment: string
}