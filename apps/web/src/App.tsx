import { QueryClientProvider } from '@tanstack/react-query'
import { lazy, Suspense, useState } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'

import { AuthPanel } from './features/auth/AuthPanel'
import { httpAuthClient } from './features/auth/authClient'
import { HealthStatus } from './features/health/HealthStatus'
import { httpHealthClient } from './features/health/healthClient'
import { OrganizationPanel } from './features/organizations/OrganizationPanel'
import { httpOrganizationClient } from './features/organizations/organizationClient'
import { queryClient } from './lib/apiClient'

const FarmsPage = lazy(() =>
  import('./features/farms/routes/FarmsPage').then((module) => ({ default: module.FarmsPage })),
)

const TalhoesPage = lazy(() =>
  import('./features/talhoes/routes/TalhoesPage').then((module) => ({ default: module.TalhoesPage })),
)

function HomePage() {
  const [authVersion, setAuthVersion] = useState(0)

  return (
    <main>
      <AuthPanel client={httpAuthClient} onAuthChange={() => setAuthVersion((value) => value + 1)} />
      <OrganizationPanel key={authVersion} client={httpOrganizationClient} />
      <HealthStatus client={httpHealthClient} />
    </main>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route
            path="/fazendas"
            element={
              <Suspense fallback={<main><p role="status">Carregando...</p></main>}>
                <FarmsPage />
              </Suspense>
            }
          />
          <Route
            path="/fazendas/:farmId/talhoes"
            element={
              <Suspense fallback={<main><p role="status">Carregando...</p></main>}>
                <TalhoesPage />
              </Suspense>
            }
          />
        </Routes>
      </BrowserRouter>
      <Toaster richColors closeButton />
    </QueryClientProvider>
  )
}

export default App
