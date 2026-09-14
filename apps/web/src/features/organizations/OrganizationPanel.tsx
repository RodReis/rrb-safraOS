import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import type { Organization, OrganizationClient } from './organizationClient'

type Props = {
  client: OrganizationClient
}

type LoadState = 'loading' | 'success' | 'empty' | 'error' | 'unauthorized'

export function OrganizationPanel({ client }: Props) {
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [activeId, setActiveId] = useState('')
  const [name, setName] = useState('')
  const [message, setMessage] = useState('')
  const [state, setState] = useState<LoadState>('loading')
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    const result = await client.list()
    if (!result.ok) {
      setMessage(result.message)
      setState(result.message.includes('Sessao') ? 'unauthorized' : 'error')
      return
    }
    setOrganizations(result.organizations)
    setState(result.organizations.length > 0 ? 'success' : 'empty')
    setMessage('')
  }, [client])

  useEffect(() => {
    // oxlint-disable-next-line react/set-state-in-effect -- carga inicial sincroniza UI com API.
    void load()
  }, [load])

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    const result = await client.create(name)
    if (!result.ok) {
      setMessage(result.message)
      setBusy(false)
      return
    }
    setName('')
    setOrganizations((current) => [...current, result.organization])
    setState('success')
    setMessage('Organizacao criada.')
    setBusy(false)
  }

  async function select(organizationId: string) {
    setBusy(true)
    const result = await client.selectActive(organizationId)
    if (!result.ok) {
      setMessage(result.message)
      setBusy(false)
      return
    }
    setActiveId(result.organization.id)
    setMessage(`Tenant ativo: ${result.organization.name}`)
    setBusy(false)
  }

  return (
    <section className="tenant-shell" aria-labelledby="tenant-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">SPEC-003 / F3</p>
          <h2 id="tenant-title">Organizacoes e tenant ativo</h2>
        </div>
        <span className="status-badge">Owner MVP0</span>
      </div>

      <form className="tenant-form" onSubmit={create}>
        <label htmlFor="organization-name">Nome da organizacao</label>
        <div className="inline-action">
          <input
            id="organization-name"
            minLength={2}
            onChange={(event) => setName(event.target.value)}
            placeholder="Fazenda Santa Maria"
            required
            value={name}
          />
          <button disabled={busy} type="submit">
            Criar
          </button>
        </div>
      </form>

      {state === 'loading' ? <div className="skeleton" aria-label="Carregando organizacoes" /> : null}
      {state === 'unauthorized' ? (
        <p className="notice" role="status">
          Entre para gerenciar organizacoes.
        </p>
      ) : null}
      {state === 'error' ? (
        <div className="notice" role="alert">
          <p>{message}</p>
          <button
            type="button"
            onClick={() => {
              setState('loading')
              void load()
            }}
          >
            Tentar novamente
          </button>
        </div>
      ) : null}
      {state === 'empty' ? (
        <p className="notice" role="status">
          Nenhuma organizacao criada. Crie a primeira para abrir o tenant.
        </p>
      ) : null}
      {state === 'success' ? (
        <ul className="tenant-list" aria-label="Organizacoes">
          {organizations.map((organization) => (
            <li key={organization.id} data-active={activeId === organization.id}>
              <div>
                <strong>{organization.name}</strong>
                <span>{organization.role}</span>
              </div>
              <button disabled={busy} type="button" onClick={() => select(organization.id)}>
                {activeId === organization.id ? 'Ativo' : 'Selecionar'}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {message ? <p role="status">{message}</p> : null}
    </section>
  )
}
