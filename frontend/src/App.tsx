import { Routes, Route } from 'react-router-dom'
import { AppProvider } from './AppContext'
import { AuditList } from './pages/AuditList'
import { AuditDetail } from './pages/AuditDetail'

function App() {
  return (
    <AppProvider>
      <Routes>
        <Route path="/" element={<AuditList />} />
        <Route path="/audits/:auditId" element={<AuditDetail />} />
      </Routes>
    </AppProvider>
  )
}

export default App