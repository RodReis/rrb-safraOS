import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, test, vi } from 'vitest'

import { AuthPanel } from './AuthPanel'
import type { AuthClient } from './authClient'

function client(overrides: Partial<AuthClient> = {}): AuthClient {
  return {
    register: vi.fn(async () => ({ ok: true, message: 'instrucoes enviadas' })),
    login: vi.fn(async () => ({ ok: true, message: 'sessao iniciada', csrfToken: 'csrf' })),
    requestReset: vi.fn(async () => ({ ok: true, message: 'resposta neutra' })),
    confirmEmail: vi.fn(async () => ({ ok: true, message: 'confirmado' })),
    resetPassword: vi.fn(async () => ({ ok: true, message: 'senha redefinida' })),
    logout: vi.fn(async () => ({ ok: true, message: 'sessao encerrada' })),
    ...overrides,
  }
}

describe('AuthPanel (SPEC-002)', () => {
  test('login preserva e-mail e nunca repoe senha em erro recuperavel', async () => {
    const authClient = client({
      login: vi.fn(async () => ({ ok: false, message: 'Credenciais invalidas' })),
    })

    render(<AuthPanel client={authClient} />)
    fireEvent.change(screen.getByLabelText(/e-mail/i), { target: { value: 'dono@example.com' } })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 'senha-longa-segura' } })
    fireEvent.click(screen.getByRole('button', { name: /entrar agora/i }))

    await waitFor(() => expect(screen.getByText(/credenciais invalidas/i)).toBeInTheDocument())
    expect(screen.getByLabelText(/e-mail/i)).toHaveValue('dono@example.com')
    expect(screen.getByLabelText(/senha/i)).toHaveValue('senha-longa-segura')
  })

  test('cadastro limpa senha apos resposta neutra', async () => {
    render(<AuthPanel client={client()} />)
    fireEvent.click(screen.getByRole('button', { name: /^Criar$/i }))
    fireEvent.change(screen.getByLabelText(/e-mail/i), { target: { value: 'dono@example.com' } })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 'senha-longa-segura' } })
    fireEvent.click(screen.getByRole('button', { name: /criar conta agora/i }))

    await waitFor(() => expect(screen.getByText(/instrucoes enviadas/i)).toBeInTheDocument())
    expect(screen.getByLabelText(/senha/i)).toHaveValue('')
  })

  test('login bem sucedido habilita logout com csrf', async () => {
    const authClient = client()

    render(<AuthPanel client={authClient} />)
    fireEvent.change(screen.getByLabelText(/e-mail/i), { target: { value: 'dono@example.com' } })
    fireEvent.change(screen.getByLabelText(/senha/i), { target: { value: 'senha-longa-segura' } })
    fireEvent.click(screen.getByRole('button', { name: /entrar agora/i }))

    await waitFor(() => expect(screen.getByRole('button', { name: /^Sair$/i })).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: /^Sair$/i }))

    await waitFor(() => expect(authClient.logout).toHaveBeenCalledWith('csrf'))
  })
})
