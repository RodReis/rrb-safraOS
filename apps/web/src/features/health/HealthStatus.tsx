import { useEffect, useState } from 'react'

import type { HealthChecks, HealthClient } from './healthClient'

type State =
  | { kind: 'loading' }
  | { kind: 'healthy' }
  | { kind: 'unhealthy'; reason: string }

const describeFailure = (checks: HealthChecks): string =>
  Object.entries(checks)
    .filter(([, status]) => status === 'fail')
    .map(([name]) => name)
    .join(', ')

export function HealthStatus({ client }: { client: HealthClient }) {
  const [state, setState] = useState<State>({ kind: 'loading' })

  useEffect(() => {
    let cancelled = false

    client
      .fetchReadiness()
      .then((response) => {
        if (cancelled) return
        setState(
          response.ok
            ? { kind: 'healthy' }
            : { kind: 'unhealthy', reason: describeFailure(response.body.checks) },
        )
      })
      .catch((error: unknown) => {
        if (cancelled) return
        // Nunca esconder o erro: SPEC-001 exige que a web exiba o estado real.
        const message = error instanceof Error ? error.message : String(error)
        setState({ kind: 'unhealthy', reason: message })
      })

    return () => {
      cancelled = true
    }
  }, [client])

  if (state.kind === 'loading') return <p>Verificando status da API…</p>
  if (state.kind === 'healthy') return <p>API saudável</p>
  return (
    <p>
      API indisponível — {state.reason}
    </p>
  )
}
