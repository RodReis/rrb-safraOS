export type AuthResponse = {
  message: string
  csrfToken?: string
  ok: boolean
}

export type AuthClient = {
  register(email: string, password: string): Promise<AuthResponse>
  login(email: string, password: string): Promise<AuthResponse>
  requestReset(email: string): Promise<AuthResponse>
  confirmEmail(token: string): Promise<AuthResponse>
  resetPassword(token: string, password: string): Promise<AuthResponse>
  logout(csrfToken: string): Promise<AuthResponse>
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5183'

async function post(path: string, body: unknown, csrfToken?: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'content-type': 'application/json',
      ...(csrfToken ? { 'x-csrf-token': csrfToken } : {}),
    },
    body: JSON.stringify(body),
  })
  const payload = (await response.json()) as { message?: string }
  return {
    ok: response.ok,
    message: payload.message ?? 'Operacao indisponivel.',
    csrfToken: response.headers.get('x-csrf-token') ?? undefined,
  }
}

export const httpAuthClient: AuthClient = {
  register: (email, password) => post('/v1/auth/register', { email, password }),
  login: (email, password) => post('/v1/auth/login', { email, password }),
  requestReset: (email) => post('/v1/auth/password-reset/request', { email }),
  confirmEmail: (token) => post('/v1/auth/confirm-email', { token }),
  resetPassword: (token, password) => post('/v1/auth/password-reset/confirm', { token, password }),
  logout: (csrfToken) => post('/v1/auth/logout', {}, csrfToken),
}
