import { useState } from 'react'
import { useApp } from '../AppContext'
import { useNavigate } from 'react-router-dom'
import type { Profile } from '../types'

export function AuditList() {
  const { audits, loading, error, deleteAudit, createAudit } = useApp()
  const navigate = useNavigate()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newAudit, setNewAudit] = useState({ name: '', target_path: '', profile: 'standard' as Profile })

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    const audit = await createAudit(newAudit)
    if (audit) {
      setShowCreateModal(false)
      setNewAudit({ name: '', target_path: '', profile: 'standard' })
      navigate(`/audits/${audit.id}`)
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this audit run?')) return
    await deleteAudit(id)
  }

  return (
    <div className="container" style={{ paddingTop: '24px', paddingBottom: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '600' }}>Audit Runs</h1>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          New Audit
        </button>
      </div>

      {error && (
        <div className="toast toast-error" style={{ marginBottom: '16px' }}>
          {error}
        </div>
      )}

      {loading && audits.length === 0 ? (
        <div className="card" style={{ display: 'flex', justifyContent: 'center', padding: '48px' }}>
          <div className="loading-spinner" />
        </div>
      ) : audits.length === 0 ? (
        <div className="card empty-state">
          <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          <p className="empty-state-title">No audit runs yet</p>
          <p>Create your first security audit run to get started.</p>
          <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => setShowCreateModal(true)}>
            Create Audit Run
          </button>
        </div>
      ) : (
        <div className="card">
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Target</th>
                  <th>Profile</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th style={{ width: '100px' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {audits.map((audit) => (
                  <tr key={audit.id}>
                    <td style={{ fontWeight: '500' }}>{audit.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {audit.target_path}
                    </td>
                    <td><span className="badge">{audit.profile}</span></td>
                    <td><span className={`badge badge-${audit.status}`}>{audit.status}</span></td>
                    <td>{new Date(audit.created_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button 
                          className="btn btn-outline btn-sm" 
                          onClick={() => navigate(`/audits/${audit.id}`)}
                        >
                          View
                        </button>
                        <button 
                          className="btn btn-outline btn-sm btn-danger" 
                          onClick={() => handleDelete(audit.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '100%', maxWidth: '480px', margin: '16px' }}>
            <div className="card-header">
              <h2 style={{ fontSize: '18px', fontWeight: '600' }}>Create Audit Run</h2>
            </div>
            <form onSubmit={handleCreate}>
              <div className="card-body">
                <div className="form-group">
                  <label className="form-label">Name</label>
                  <input 
                    className="form-input" 
                    placeholder="e.g., Q4 Security Audit" 
                    value={newAudit.name} 
                    onChange={e => setNewAudit({...newAudit, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Target Path</label>
                  <input 
                    className="form-input" 
                    placeholder="/path/to/target/repository" 
                    value={newAudit.target_path} 
                    onChange={e => setNewAudit({...newAudit, target_path: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Profile</label>
                  <select 
                    className="form-select" 
                    value={newAudit.profile} 
                    onChange={e => setNewAudit({...newAudit, profile: e.target.value as Profile})}
                  >
                    <option value="quick">Quick - Single hunter wave</option>
                    <option value="standard">Standard - Multiple waves + validation</option>
                    <option value="deep">Deep - Extended hunting + carried records</option>
                  </select>
                </div>
              </div>
              <div className="card-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={loading || !newAudit.name || !newAudit.target_path}>
                  {loading ? 'Creating...' : 'Create Audit'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}