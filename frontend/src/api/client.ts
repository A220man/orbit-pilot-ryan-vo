import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'


class ApiClient {
  private client: AxiosInstance
  private accessToken: string | null = null

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true, // For HttpOnly cookies
    })

    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${this.accessToken}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.accessToken = null
          // Could trigger logout here
        }
        return Promise.reject(error)
      }
    )
  }

  setAccessToken(token: string | null) {
    this.accessToken = token
  }

  // Health
  async health() {
    return this.client.get('/health')
  }

  // Audit Runs
  async listAudits(params?: { status?: string; limit?: number; offset?: number }) {
    return this.client.get('/api/v1/audits', { params })
  }

  async createAudit(data: {
    name: string
    target_path: string
    profile: 'quick' | 'standard' | 'deep'
    config?: Record<string, any>
  }) {
    return this.client.post('/api/v1/audits', data)
  }

  async getAudit(id: number) {
    return this.client.get(`/api/v1/audits/${id}`)
  }

  async updateAudit(id: number, data: {
    name?: string
    status?: string
    config?: Record<string, any>
    error?: string
  }) {
    return this.client.patch(`/api/v1/audits/${id}`, data)
  }

  async deleteAudit(id: number) {
    return this.client.delete(`/api/v1/audits/${id}`)
  }

  // Findings
  async listFindings(auditId: number, params?: {
    status?: string
    attack_class?: string
    severity?: string
    limit?: number
    offset?: number
  }) {
    return this.client.get(`/api/v1/audits/${auditId}/findings`, { params })
  }

  async getFinding(auditId: number, findingId: number) {
    return this.client.get(`/api/v1/audits/${auditId}/findings/${findingId}`)
  }

  async createFinding(auditId: number, data: {
    unit_id: string
    title: string
    description: string
    attack_class: string
    severity?: string
    cwe?: string[]
    cvss_vector?: string
    cvss_version?: string
    references?: Array<{ url: string }>
    evidence?: Record<string, any>
    remediation?: Record<string, any>
    preserved_uses?: Array<{ who: string; path: string; how_it_keeps_working: string }>
    method_backed?: boolean
    source_trace?: Record<string, any>
  }) {
    return this.client.post(`/api/v1/audits/${auditId}/findings`, data)
  }

  async updateFinding(auditId: number, findingId: number, data: {
    title?: string
    description?: string
    attack_class?: string
    status?: string
    severity?: string
    cwe?: string[]
    cvss_vector?: string
    cvss_version?: string
    references?: Array<{ url: string }>
    evidence?: Record<string, any>
    remediation?: Record<string, any>
    preserved_uses?: Array<{ who: string; path: string; how_it_keeps_working: string }>
    method_backed?: boolean
    source_trace?: Record<string, any>
    verifier_notes?: string
  }) {
    return this.client.patch(`/api/v1/audits/${auditId}/findings/${findingId}`, data)
  }

  // Coverage Ledger
  async getCoverage(auditId: number) {
    return this.client.get(`/api/v1/audits/${auditId}/coverage`)
  }

  // Audit Logs
  async getLogs(auditId: number, limit?: number) {
    return this.client.get(`/api/v1/audits/${auditId}/logs`, { params: { limit } })
  }
}

export const api = new ApiClient()