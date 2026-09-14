import { QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

import { AuthPanel } from './features/auth/AuthPanel'
import { httpAuthClient } from './features/auth/authClient'
import { HealthStatus } from './features/health/HealthStatus'
import { httpHealthClient } from './features/health/healthClient'
import { OrganizationPanel } from './features/organizations/OrganizationPanel'
import { httpOrganizationClient } from './features/organizations/organizationClient'
import { queryClient } from './lib/apiClient'

function App() {
  const [authVersion, setAuthVersion] = useState(0)

  return (
    <QueryClientProvider client={queryClient}>
      <main>
        <AuthPanel client={httpAuthClient} onAuthChange={() => setAuthVersion((value) => value + 1)} />
        <OrganizationPanel key={authVersion} client={httpOrganizationClient} />
        <HealthStatus client={httpHealthClient} />
      </main>
    </QueryClientProvider>
  )
}

export default App
