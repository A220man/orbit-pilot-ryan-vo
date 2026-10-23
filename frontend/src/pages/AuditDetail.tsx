import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useApp } from '../AppContext'
import type { Finding, FindingStatus, Severity } from '../types'

const STATUS_OPTIONS: FindingStatus[] = ['planned', 'hunting', 'needs_validation', 'confirmed', 'rejected', 'deferred', 'out_of_scope']
const SEVERITY_OPTIONS: Severity[] = ['critical', 'high', 'medium', 'low', 'informational']

export function AuditDetail() {
  const { auditId } = useParams<{ auditId: string }>()
  const { 
    currentAudit, findings, coverage, logs, loading, error,
    fetchAudit, fetchFindings, fetchCoverage, fetchLogs,
    updateAudit, createFinding, updateFinding,
  } = useApp()
  const navigate = useNavigate()
  const id = parseInt(auditId || '0', 10)

  const [showCreateFinding, setShowCreateFinding] = useState(false)
  const [newFinding, setNewFinding] = useState({
    unit_id: '',
    title: '',
    description: '',
    attack_class: '',
    severity: 'medium' as Severity,
  })
  const [activeTab, setActiveTab] = useState<'findings' | 'coverage' | 'logs'>('findings')

  useEffect(() => {
    if (id) {
      fetchAudit(id)
      fetchFindings(id)
      fetchCoverage(id)
      fetchLogs(id)
    }
  }, [id])

  const handleCreateFinding = async (e: React.FormEvent) => {
    e.preventDefault()
    await createFinding(id, newFinding)
    setShowCreateFinding(false)
    setNewFinding({ unit_id: '', title: '', description: '', attack_class: '', severity: 'medium' })
  }

  const handleUpdateFinding = async (finding: Finding, updates: Partial<Finding>) => {
    await updateFinding(id, finding.id, updates)
  }

  const handleStatusChange = (finding: Finding, status: FindingStatus) => {
    handleUpdateFinding(finding, { status })
  }

  const handleSeverityChange = (finding: Finding, severity: Severity) => {
    handleUpdateFinding(finding, { severity })
  }

  const handleRunAudit = async () => {
    if (!currentAudit) return
    await updateAudit(id, { status: 'running' })
  }

  const handleCompleteAudit = async () => {
    if (!currentAudit) return
    await updateAudit(id, { status: 'completed' })
  }

  if (loading && !currentAudit) {
    return (
      <div className="container" style={{ paddingTop: '24px', display: 'flex', justifyContent: 'center', paddingBottom: '48px' }}>
        <div className="loading-spinner" />
      </div>
    )
  }

  if (!currentAudit) {
    return (
      <div className="container empty-state" style={{ paddingTop: '48px' }}>
        <p className="empty-state-title">Audit not found</p>
      </div>
    )
  }

  const confirmedFindings = findings.filter(f => f.status === 'confirmed').length
  const needsValidationFindings = findings.filter(f => f.status === 'needs_validation').length
  const huntingFindings = findings.filter(f => f.status === 'hunting').length

  return (
    <div className="container" style={{ paddingTop: '24px', paddingBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '600' }}>{currentAudit.name}</h1>
          <p style={{ color: 'var(--color-text-muted)', marginTop: '4px' }}>
            {currentAudit.target_path} • Profile: {currentAudit.profile}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          {currentAudit.status === 'draft' && (
            <button className="btn btn-primary" onClick={handleRunAudit}>Start Audit</button>
          )}
          {currentAudit.status === 'running' && (
            <button className="btn btn-success" onClick={handleCompleteAudit}>Mark Complete</button>
          )}
          <button className="btn btn-outline" onClick={() => navigate('/')}>Back</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div className="card">
          <div className="card-body" style={{ padding: '16px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--color-success)' }}>{confirmedFindings}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Confirmed</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body" style={{ padding: '16px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--color-warning)' }}>{needsValidationFindings}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Needs Validation</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body" style={{ padding: '16px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--color-primary)' }}>{huntingFindings}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Hunting</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body" style={{ padding: '16px' }}>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>{findings.length}</div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>Total Findings</div>
          </div>
        </div>
      </div>

      {error && (
        <div className="toast toast-error" style={{ marginBottom: '16px' }}>
          {error}
        </div>
      )}

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'findings' ? 'active' : ''}`} 
          onClick={() => setActiveTab('findings')}
        >
          Findings ({findings.length})
        </button>
        <button 
          className={`tab ${activeTab === 'coverage' ? 'active' : ''}`} 
          onClick={() => setActiveTab('coverage')}
        >
          Coverage Ledger
        </button>
        <button 
          className={`tab ${activeTab === 'logs' ? 'active' : ''}`} 
          onClick={() => setActiveTab('logs')}
        >
          Audit Logs ({logs.length})
        </button>
      </div>

      {activeTab === 'findings' && (
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: '16px', fontWeight: '600' }}>Findings</h2>
            <button className="btn btn-primary btn-sm" onClick={() => setShowCreateFinding(true)}>
              Add Finding
            </button>
          </div>
          {findings.length === 0 ? (
            <div className="empty-state" style={{ padding: '48px' }}>
              <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="empty-state-title">No findings yet</p>
              <p>Add your first finding to start tracking security issues.</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th style={{ width: '120px' }}>Unit ID</th>
                    <th>Title</th>
                    <th style={{ width: '140px' }}>Class</th>
                    <th style={{ width: '140px' }}>Status</th>
                    <th style={{ width: '120px' }}>Severity</th>
                    <th style={{ width: '80px' }}>Method</th>
                    <th style={{ width: '100px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map(finding => (
                    <tr key={finding.id}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{finding.unit_id}</td>
                      <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{finding.title}</td>
                      <td><span className="badge">{finding.attack_class}</span></td>
                      <td>
                        <select
                          className="form-select"
                          value={finding.status}
                          onChange={e => handleStatusChange(finding, e.target.value as FindingStatus)}
                          style={{ width: 'auto', padding: '4px 8px', fontSize: '12px' }}
                        >
                          {STATUS_OPTIONS.map(s => (
                            <option key={s} value={s}>{s.replace('_', ' ')}</option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <select
                          className="form-select"
                          value={finding.severity || ''}
                          onChange={e => handleSeverityChange(finding, e.target.value as Severity || null)}
                          style={{ width: 'auto', padding: '4px 8px', fontSize: '12px' }}
                        >
                          <option value="">—</option>
                          {SEVERITY_OPTIONS.map(s => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <span className={`badge ${finding.method_backed ? 'badge-confirmed' : 'badge-planned'}`}>
                          {finding.method_backed ? 'Method-backed' : 'Reading'}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="btn btn-outline btn-sm"
                          onClick={() => navigate(`/audits/${id}/findings/${finding.id}`)}
                        >
                          Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'coverage' && (
        <div className="card">
          <div className="card-header">
            <h2 style={{ fontSize: '16px', fontWeight: '600' }}>Coverage Ledger</h2>
          </div>
          <div className="card-body">
            {coverage && coverage.units.length === 0 && (
              <div className="empty-state" style={{ padding: '48px' }}>
                <p className="empty-state-title">No coverage units tracked</p>
                <p>Units will appear as the audit progresses through phases.</p>
              </div>
            )}
            {coverage && coverage.units.length > 0 && (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Unit ID</th>
                      <th>Title</th>
                      <th>Attack Class</th>
                      <th>Status</th>
                      <th>Files</th>
                      <th>Assigned To</th>
                    </tr>
                  </thead>
                  <tbody>
                    {coverage.units.map((unit, idx) => (
                      <tr key={idx}>
                        <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{unit.unit_id}</td>
                        <td>{unit.title}</td>
                        <td><span className="badge">{unit.attack_class}</span></td>
                        <td><span className={`badge badge-${unit.status}`}>{unit.status.replace('_', ' ')}</span></td>
                        <td style={{ fontSize: '12px', fontFamily: 'var(--font-mono)' }}>
                          {unit.files.length > 0 ? unit.files.join(', ') : '—'}
                        </td>
                        <td>{unit.assigned_to || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {coverage && coverage.attempts.length > 0 && (
              <div style={{ marginTop: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>Attempts</h3>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Attempt</th>
                        <th>Phase</th>
                        <th>Units Targeted</th>
                        <th>Units Completed</th>
                        <th>Artifacts</th>
                      </tr>
                    </thead>
                    <tbody>
                      {coverage.attempts.map(attempt => (
                        <tr key={attempt.attempt_id}>
                          <td>#{attempt.attempt_id}</td>
                          <td>{attempt.phase}</td>
                          <td>{attempt.units_targeted.join(', ') || '—'}</td>
                          <td>{attempt.units_completed.join(', ') || '—'}</td>
                          <td>{attempt.artifacts.length}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="card">
          <div className="card-header">
            <h2 style={{ fontSize: '16px', fontWeight: '600' }}>Audit Logs</h2>
          </div>
          <div className="card-body">
            {logs.length === 0 ? (
              <div className="empty-state" style={{ padding: '48px' }}>
                <p className="empty-state-title">No logs yet</p>
              </div>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Phase</th>
                      <th>Action</th>
                      <th>Actor</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map(log => (
                      <tr key={log.id}>
                        <td style={{ fontSize: '12px', whiteSpace: 'nowrap' }}>
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td><span className="badge">{log.phase}</span></td>
                        <td>{log.action}</td>
                        <td>{log.actor || 'system'}</td>
                        <td style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', maxWidth: '300px' }}>
                          {JSON.stringify(log.details)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {showCreateFinding && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '100%', maxWidth: '560px', margin: '16px', maxHeight: '90vh', overflow: 'auto' }}>
            <div className="card-header">
              <h2 style={{ fontSize: '18px', fontWeight: '600' }}>Add Finding</h2>
            </div>
            <form onSubmit={handleCreateFinding}>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">Unit ID</label>
                  <input 
                    className="form-input" 
                    placeholder="e.g., auth-bypass-001" 
                    value={newFinding.unit_id} 
                    onChange={e => setNewFinding({...newFinding, unit_id: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Title</label>
                  <input 
                    className="form-input" 
                    placeholder="Brief title of the finding" 
                    value={newFinding.title} 
                    onChange={e => setNewFinding({...newFinding, title: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea 
                    className="form-input form-textarea" 
                    placeholder="Detailed description of the finding" 
                    value={newFinding.description} 
                    onChange={e => setNewFinding({...newFinding, description: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Attack Class</label>
                  <input 
                    className="form-input" 
                    placeholder="e.g., authentication, injection, authorization" 
                    value={newFinding.attack_class} 
                    onChange={e => setNewFinding({...newFinding, attack_class: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Severity</label>
                  <select 
                    className="form-select" 
                    value={newFinding.severity} 
                    onChange={e => setNewFinding({...newFinding, severity: e.target.value as Severity})}
                  >
                    {SEVERITY_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
              <div className="card-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowCreateFinding(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading || !newFinding.unit_id || !newFinding.title}>
                  {loading ? 'Creating...' : 'Add Finding'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}