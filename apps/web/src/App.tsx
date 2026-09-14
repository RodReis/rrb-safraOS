import { HealthStatus } from './features/health/HealthStatus'
import { httpHealthClient } from './features/health/healthClient'

function App() {
  return (
    <main>
      <h1>SafraOS</h1>
      <HealthStatus client={httpHealthClient} />
    </main>
  )
}

export default App
