import { useState, createContext, useContext, ReactNode } from 'react'
import { api } from './api/client'
import type { AuditRun, Finding, CoverageLedger, AuditLogEntry, Profile } from './types'

interface AppContextType {
  audits: AuditRun[]
  currentAudit: AuditRun | null
  findings: Finding[]
  coverage: CoverageLedger | null
  logs: AuditLogEntry[]
  loading: boolean
  error: string | null
  fetchAudits: () => Promise<void>
  fetchAudit: (id: number) => Promise<void>
  fetchFindings: (auditId: number) => Promise<void>
  fetchCoverage: (auditId: number) => Promise<void>
  fetchLogs: (auditId: number) => Promise<void>
  createAudit: (data: { name: string; target_path: string; profile: Profile }) => Promise<AuditRun | null>
  updateAudit: (id: number, data: { name?: string; status?: string; config?: Record<string, any>; error?: string }) => Promise<void>
  deleteAudit: (id: number) => Promise<void>
  createFinding: (auditId: number, data: Partial<Finding>) => Promise<Finding | null>
  updateFinding: (auditId: number, findingId: number, data: Partial<Finding>) => Promise<void>
  setError: (error: string | null) => void
}

const AppContext = createContext<AppContextType | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const [audits, setAudits] = useState<AuditRun[]>([])
  const [currentAudit, setCurrentAudit] = useState<AuditRun | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [coverage, setCoverage] = useState<CoverageLedger | null>(null)
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAudits = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.listAudits({ limit: 50 })
      setAudits(response.data)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to fetch audits')
    } finally {
      setLoading(false)
    }
  }

  const fetchAudit = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.getAudit(id)
      setCurrentAudit(response.data)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to fetch audit')
    } finally {
      setLoading(false)
    }
  }

  const fetchFindings = async (auditId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.listFindings(auditId, { limit: 100 })
      setFindings(response.data)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to fetch findings')
    } finally {
      setLoading(false)
    }
  }

  const fetchCoverage = async (auditId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.getCoverage(auditId)
      setCoverage(response.data)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to fetch coverage')
    } finally {
      setLoading(false)
    }
  }

  const fetchLogs = async (auditId: number) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.getLogs(auditId, 200)
      setLogs(response.data)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to fetch logs')
    } finally {
      setLoading(false)
    }
  }

  const createAudit = async (data: { name: string; target_path: string; profile: Profile }) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.createAudit(data)
      const newAudit = response.data
      setAudits(prev => [newAudit, ...prev])
      return newAudit
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to create audit')
      return null
    } finally {
      setLoading(false)
    }
  }

  const updateAudit = async (id: number, data: { name?: string; status?: string; config?: Record<string, any>; error?: string }) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.updateAudit(id, data)
      const updated = response.data
      setAudits(prev => prev.map(a => a.id === id ? updated : a))
      if (currentAudit?.id === id) setCurrentAudit(updated)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to update audit')
    } finally {
      setLoading(false)
    }
  }

  const deleteAudit = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      await api.deleteAudit(id)
      setAudits(prev => prev.filter(a => a.id !== id))
      if (currentAudit?.id === id) setCurrentAudit(null)
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to delete audit')
    } finally {
      setLoading(false)
    }
  }

  const createFinding = async (auditId: number, data: Partial<Finding>) => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.createFinding(auditId, data as any)
      const newFinding = response.data
      setFindings(prev => [newFinding, ...prev])
      return newFinding
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to create finding')
      return null
    } finally {
      setLoading(false)
    }
  }

  const updateFinding = async (auditId: number, findingId: number, data: Partial<Finding>) => {
    setLoading(true)
    setError(null)
    try {
      await api.updateFinding(auditId, findingId, data as any)
      setFindings(prev => prev.map(f => f.id === findingId ? { ...f, ...data } : f))
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Failed to update finding')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppContext.Provider value={{
      audits, currentAudit, findings, coverage, logs, loading, error,
      fetchAudits, fetchAudit, fetchFindings, fetchCoverage, fetchLogs,
      createAudit, updateAudit, deleteAudit, createFinding, updateFinding, setError
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}