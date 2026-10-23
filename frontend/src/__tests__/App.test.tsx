import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'

// Mock the API client with inline factory
vi.mock('../api/client', () => ({
  api: {
    listAudits: vi.fn().mockResolvedValue({ data: [] }),
    createAudit: vi.fn(),
    getAudit: vi.fn(),
    updateAudit: vi.fn(),
    deleteAudit: vi.fn(),
    listFindings: vi.fn(),
    createFinding: vi.fn(),
    updateFinding: vi.fn(),
    getCoverage: vi.fn(),
    getLogs: vi.fn(),
  }
}))

const renderApp = () => render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
)

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders audit list page', async () => {
    renderApp()
    
    await waitFor(() => {
      expect(screen.getByText('Audit Runs')).toBeInTheDocument()
    })
  })

  it('shows empty state when no audits', async () => {
    renderApp()
    
    await waitFor(() => {
      expect(screen.getByText('No audit runs yet')).toBeInTheDocument()
    })
  })

  it('opens create audit modal', async () => {
    renderApp()
    
    await waitFor(() => {
      expect(screen.getByText('New Audit')).toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByText('New Audit'))
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Create Audit Run' })).toBeInTheDocument()
    })
  })
})