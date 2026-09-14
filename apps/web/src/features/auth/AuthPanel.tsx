import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'

import type { AuthClient } from './authClient'

type Mode = 'login' | 'register' | 'reset'

type Props = {
  client: AuthClient
}

export function AuthPanel({ client }: Props) {
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [csrfToken, setCsrfToken] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)

  const title = useMemo(() => {
    if (mode === 'register') return 'Criar conta'
    if (mode === 'reset') return 'Recuperar senha'
    return 'Entrar'
  }, [mode])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setMessage('')
    try {
      const response =
        mode === 'register'
          ? await client.register(email, password)
          : mode === 'reset'
            ? await client.requestReset(email)
            : await client.login(email, password)
      if (response.csrfToken) setCsrfToken(response.csrfToken)
      setMessage(response.message)
      if (mode !== 'login') setPassword('')
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Servico indisponivel.')
    } finally {
      setBusy(false)
    }
  }

  async function logout() {
    setBusy(true)
    const response = await client.logout(csrfToken)
    setMessage(response.message)
    setCsrfToken('')
    setBusy(false)
  }

  return (
    <section className="auth-shell" aria-labelledby="auth-title">
      <div className="auth-brand">
        <p>SafraOS</p>
        <h1 id="auth-title">{title}</h1>
      </div>

      <div className="auth-tabs" role="tablist" aria-label="Autenticacao">
        <button type="button" aria-selected={mode === 'login'} onClick={() => setMode('login')}>
          Entrar
        </button>
        <button type="button" aria-selected={mode === 'register'} onClick={() => setMode('register')}>
          Criar
        </button>
        <button type="button" aria-selected={mode === 'reset'} onClick={() => setMode('reset')}>
          Recuperar
        </button>
      </div>

      <form className="auth-form" onSubmit={submit}>
        <label>
          E-mail
          <input
            autoComplete="email"
            inputMode="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>
        {mode !== 'reset' ? (
          <label>
            Senha
            <input
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={12}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
        ) : null}
        <button aria-label={`${title} agora`} disabled={busy} type="submit">
          {busy ? 'Aguarde' : title}
        </button>
      </form>

      {csrfToken ? (
        <button className="secondary-action" disabled={busy} onClick={logout} type="button">
          Sair
        </button>
      ) : null}

      {message ? <p role="status">{message}</p> : null}
    </section>
  )
}
