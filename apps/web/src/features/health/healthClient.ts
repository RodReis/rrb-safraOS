/** Contrato tipado de GET /health/ready (SPEC-001). */
export interface HealthChecks {
  database: 'ok' | 'fail'
  redis: 'ok' | 'fail'
}

export interface HealthReadyBody {
  status: 'ready' | 'unhealthy'
  checks: HealthChecks
  correlationId: string
}

export interface HealthReadyResponse {
  ok: boolean
  body: HealthReadyBody
}

export interface HealthClient {
  fetchReadiness: () => Promise<HealthReadyResponse>
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5183'

export const httpHealthClient: HealthClient = {
  async fetchReadiness() {
    const response = await fetch(`${API_BASE_URL}/health/ready`)
    const body = (await response.json()) as HealthReadyBody
    return { ok: response.ok, body }
  },
}
