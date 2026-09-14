export type Organization = {
  id: string
  name: string
  role: 'owner'
}

export type OrganizationResult =
  | { ok: true; organization: Organization }
  | { ok: false; message: string }

export type OrganizationListResult =
  | { ok: true; organizations: Organization[] }
  | { ok: false; message: string }

export type OrganizationClient = {
  list(): Promise<OrganizationListResult>
  create(name: string): Promise<OrganizationResult>
  selectActive(organizationId: string): Promise<OrganizationResult>
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5183'

async function parseMessage(response: Response): Promise<string> {
  const payload = (await response.json()) as { message?: string }
  return payload.message ?? 'Operacao indisponivel.'
}

export const httpOrganizationClient: OrganizationClient = {
  async list() {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/organizations`, {
        credentials: 'include',
      })
      if (!response.ok) return { ok: false, message: await parseMessage(response) }
      const payload = (await response.json()) as { organizations: Organization[] }
      return { ok: true, organizations: payload.organizations }
    } catch {
      return { ok: false, message: 'API indisponivel.' }
    }
  },
  async create(name: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/organizations`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      if (!response.ok) return { ok: false, message: await parseMessage(response) }
      return { ok: true, organization: (await response.json()) as Organization }
    } catch {
      return { ok: false, message: 'API indisponivel.' }
    }
  },
  async selectActive(organizationId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/organizations/active`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ organizationId }),
      })
      if (!response.ok) return { ok: false, message: await parseMessage(response) }
      const payload = (await response.json()) as { activeOrganization: Organization }
      return { ok: true, organization: payload.activeOrganization }
    } catch {
      return { ok: false, message: 'API indisponivel.' }
    }
  },
}
