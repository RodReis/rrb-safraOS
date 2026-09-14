import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, test } from 'vitest'

import { HealthStatus } from './HealthStatus'
import type { HealthClient } from './healthClient'

describe('HealthStatus (SPEC-001)', () => {
  test('mostra estado de carregamento antes da resposta', () => {
    const client: HealthClient = { fetchReadiness: () => new Promise(() => {}) }

    render(<HealthStatus client={client} />)

    expect(screen.getByText(/verificando/i)).toBeInTheDocument()
  })

  test('mostra saudável quando a API responde ready', async () => {
    const client: HealthClient = {
      fetchReadiness: async () => ({
        ok: true,
        body: { status: 'ready', checks: { database: 'ok', redis: 'ok' }, correlationId: 'abc' },
      }),
    }

    render(<HealthStatus client={client} />)

    await waitFor(() => expect(screen.getByText(/saudável/i)).toBeInTheDocument())
  })

  test('mostra indisponível sem esconder o erro quando a API falha', async () => {
    const client: HealthClient = {
      fetchReadiness: async () => ({
        ok: false,
        body: { status: 'unhealthy', checks: { database: 'fail', redis: 'ok' }, correlationId: 'abc' },
      }),
    }

    render(<HealthStatus client={client} />)

    await waitFor(() => expect(screen.getByText(/indisponível/i)).toBeInTheDocument())
    // Contrato explícito da SPEC-001: "sem esconder erro" — o motivo aparece na tela.
    expect(screen.getByText(/database/i)).toBeInTheDocument()
  })

  test('mostra indisponível quando a requisição falha por rede', async () => {
    const client: HealthClient = {
      fetchReadiness: () => Promise.reject(new Error('network down')),
    }

    render(<HealthStatus client={client} />)

    await waitFor(() => expect(screen.getByText(/indisponível/i)).toBeInTheDocument())
    expect(screen.getByText(/network down/i)).toBeInTheDocument()
  })
})
