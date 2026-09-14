import { useState } from 'react'

import { AuthPanel } from './features/auth/AuthPanel'
import { httpAuthClient } from './features/auth/authClient'
import { HealthStatus } from './features/health/HealthStatus'
import { httpHealthClient } from './features/health/healthClient'
import { OrganizationPanel } from './features/organizations/OrganizationPanel'
import { httpOrganizationClient } from './features/organizations/organizationClient'

function App() {
  const [authVersion, setAuthVersion] = useState(0)

  return (
    <main>
      <AuthPanel client={httpAuthClient} onAuthChange={() => setAuthVersion((value) => value + 1)} />
      <OrganizationPanel key={authVersion} client={httpOrganizationClient} />
      <HealthStatus client={httpHealthClient} />
    </main>
  )
}

export default App
