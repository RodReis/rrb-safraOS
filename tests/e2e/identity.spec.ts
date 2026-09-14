import { expect, request, test } from '@playwright/test';

const API_PORT = Number(process.env.SAFRAOS_API_PORT ?? 5183);
const MAILPIT_PORT = Number(process.env.SAFRAOS_MAILPIT_UI_PORT ?? 8126);
const API_BASE = `http://localhost:${API_PORT}`;
const MAILPIT_BASE = `http://localhost:${MAILPIT_PORT}`;

type MailpitMessage = {
  ID: string;
  To: Array<{ Address: string }>;
  Subject: string;
};

async function findMessageId(email: string, subject: RegExp): Promise<string> {
  const mailpit = await request.newContext({ baseURL: MAILPIT_BASE });
  await expect
    .poll(
      async () => {
        const response = await mailpit.get('/api/v1/messages');
        const payload = (await response.json()) as { messages: MailpitMessage[] };
        const message = payload.messages.find(
          (item) =>
            item.To.some((to) => to.Address === email) && subject.test(item.Subject),
        );
        return message?.ID ?? '';
      },
      { timeout: 15_000 },
    )
    .not.toBe('');
  const response = await mailpit.get('/api/v1/messages');
  const payload = (await response.json()) as { messages: MailpitMessage[] };
  const message = payload.messages.find(
    (item) => item.To.some((to) => to.Address === email) && subject.test(item.Subject),
  );
  await mailpit.dispose();
  if (!message) throw new Error(`Mensagem nao encontrada para ${email}`);
  return message.ID;
}

async function readMessage(id: string): Promise<string> {
  const mailpit = await request.newContext({ baseURL: MAILPIT_BASE });
  const response = await mailpit.get(`/api/v1/message/${id}`);
  const payload = (await response.json()) as { Text?: string; HTML?: string };
  await mailpit.dispose();
  return `${payload.Text ?? ''}\n${payload.HTML ?? ''}`;
}

function extractToken(body: string, path: string): string {
  const escapedPath = path.replaceAll('/', '\\/');
  const match = body.match(new RegExp(`${escapedPath}\\?token=([A-Za-z0-9_-]+)`));
  if (!match?.[1]) throw new Error(`Token nao encontrado em ${path}`);
  return match[1];
}

test('cadastro, confirmacao, login, logout e reset via Mailpit', async () => {
  const api = await request.newContext({ baseURL: API_BASE });
  const email = `dono-${Date.now()}@example.com`;
  const firstPassword = 'senha-longa-segura';
  const secondPassword = 'senha-longa-nova';

  const register = await api.post('/v1/auth/register', {
    data: { email, password: firstPassword },
  });
  expect(register.status()).toBe(202);

  const denied = await api.post('/v1/auth/login', {
    data: { email, password: firstPassword },
  });
  expect(denied.status()).toBe(401);

  const verifyMessageId = await findMessageId(email, /Confirme seu e-mail/i);
  const verifyToken = extractToken(await readMessage(verifyMessageId), '/confirmar-email');
  const confirm = await api.post('/v1/auth/confirm-email', { data: { token: verifyToken } });
  expect(confirm.ok()).toBeTruthy();

  const login = await api.post('/v1/auth/login', {
    data: { email, password: firstPassword },
  });
  expect(login.ok()).toBeTruthy();
  const csrf = login.headers()['x-csrf-token'];
  expect(csrf).toBeTruthy();

  const blockedLogout = await api.post('/v1/auth/logout');
  expect(blockedLogout.status()).toBe(403);

  const resetRequest = await api.post('/v1/auth/password-reset/request', {
    data: { email },
  });
  expect(resetRequest.status()).toBe(202);

  const resetMessageId = await findMessageId(email, /Redefina sua senha/i);
  const resetToken = extractToken(await readMessage(resetMessageId), '/redefinir-senha');
  const reset = await api.post('/v1/auth/password-reset/confirm', {
    data: { token: resetToken, password: secondPassword },
  });
  expect(reset.ok()).toBeTruthy();

  const oldPassword = await api.post('/v1/auth/login', {
    data: { email, password: firstPassword },
  });
  expect(oldPassword.status()).toBe(401);

  const newPassword = await api.post('/v1/auth/login', {
    data: { email, password: secondPassword },
  });
  expect(newPassword.ok()).toBeTruthy();
  await api.dispose();
});
