import { AuthPanel } from './features/auth/AuthPanel'
import { httpAuthClient } from './features/auth/authClient'
import { HealthStatus } from './features/health/HealthStatus'
import { httpHealthClient } from './features/health/healthClient'

function App() {
  return (
    <main>
      <AuthPanel client={httpAuthClient} />
      <HealthStatus client={httpHealthClient} />
    </main>
  )
}

export default App
