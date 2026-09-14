import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, test, vi } from 'vitest'

import { OrganizationPanel } from './OrganizationPanel'
import type { OrganizationClient } from './organizationClient'

function client(overrides: Partial<OrganizationClient> = {}): OrganizationClient {
  return {
    list: vi.fn(async () => ({
      ok: true as const,
      organizations: [{ id: 'org-1', name: 'Fazenda Santa Maria', role: 'owner' as const }],
    })),
    create: vi.fn(async (name: string) => ({
      ok: true as const,
      organization: { id: 'org-2', name, role: 'owner' as const },
    })),
    selectActive: vi.fn(async (organizationId: string) => ({
      ok: true as const,
      organization: { id: organizationId, name: 'Fazenda Santa Maria', role: 'owner' as const },
    })),
    ...overrides,
  }
}

describe('OrganizationPanel (SPEC-003)', () => {
  test('lista organizacoes proprias', async () => {
    render(<OrganizationPanel client={client()} />)

    await waitFor(() => expect(screen.getByText('Fazenda Santa Maria')).toBeInTheDocument())
    expect(screen.getByText('owner')).toBeInTheDocument()
  })

  test('cria organizacao e preserva sessao', async () => {
    const organizationClient = client()
    render(<OrganizationPanel client={organizationClient} />)

    fireEvent.change(screen.getByLabelText(/nome da organizacao/i), {
      target: { value: 'Fazenda Boa Vista' },
    })
    fireEvent.click(screen.getByRole('button', { name: /^Criar$/i }))

    await waitFor(() => expect(screen.getByText('Fazenda Boa Vista')).toBeInTheDocument())
    expect(organizationClient.create).toHaveBeenCalledWith('Fazenda Boa Vista')
  })

  test('seleciona tenant ativo sem nova identidade', async () => {
    const organizationClient = client()
    render(<OrganizationPanel client={organizationClient} />)

    await waitFor(() => expect(screen.getByText('Fazenda Santa Maria')).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /selecionar/i }))

    await waitFor(() => expect(screen.getByText(/tenant ativo/i)).toBeInTheDocument())
    expect(organizationClient.selectActive).toHaveBeenCalledWith('org-1')
  })

  test('mostra sem permissao quando sessao falta', async () => {
    render(
      <OrganizationPanel
        client={client({
          list: vi.fn(async () => ({ ok: false as const, message: 'Sessao ausente ou expirada.' })),
        })}
      />,
    )

    await waitFor(() => expect(screen.getByText(/entre para gerenciar/i)).toBeInTheDocument())
  })
})
