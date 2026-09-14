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

async function createActiveUser(email: string, password: string) {
  const api = await request.newContext({ baseURL: API_BASE });
  await api.post('/v1/auth/register', { data: { email, password } });
  const mailpit = await request.newContext({ baseURL: MAILPIT_BASE });
  await expect
    .poll(async () => {
      const response = await mailpit.get('/api/v1/messages');
      const payload = (await response.json()) as { messages: MailpitMessage[] };
      return (
        payload.messages.find((item) =>
          item.To.some((to) => to.Address === email) && /Confirme seu e-mail/i.test(item.Subject),
        )?.ID ?? ''
      );
    })
    .not.toBe('');
  const messages = (await (await mailpit.get('/api/v1/messages')).json()) as {
    messages: MailpitMessage[];
  };
  const messageId = messages.messages.find((item) =>
    item.To.some((to) => to.Address === email) && /Confirme seu e-mail/i.test(item.Subject),
  )?.ID;
  if (!messageId) throw new Error('Mensagem de confirmacao nao encontrada');
  const message = (await (await mailpit.get(`/api/v1/message/${messageId}`)).json()) as {
    Text?: string;
    HTML?: string;
  };
  const token = `${message.Text ?? ''}\n${message.HTML ?? ''}`.match(
    /\/confirmar-email\?token=([A-Za-z0-9_-]+)/,
  )?.[1];
  if (!token) throw new Error('Token de confirmacao nao encontrado');
  await api.post('/v1/auth/confirm-email', { data: { token } });
  await mailpit.dispose();
  return api;
}

test('usuario cria organizacao, seleciona tenant e nao seleciona tenant alheio', async ({
  page,
}) => {
  const suffix = Date.now();
  const password = 'senha-longa-segura';
  const ownerA = `owner-a-${suffix}@example.com`;
  const ownerB = `owner-b-${suffix}@example.com`;
  const apiA = await createActiveUser(ownerA, password);
  const apiB = await createActiveUser(ownerB, password);

  const loginB = await apiB.post('/v1/auth/login', { data: { email: ownerB, password } });
  expect(loginB.ok()).toBeTruthy();
  const orgB = await apiB.post('/v1/organizations', { data: { name: 'Organizacao Alheia' } });
  expect(orgB.status()).toBe(201);
  const orgBId = ((await orgB.json()) as { id: string }).id;

  await page.goto('/');
  await page.getByLabel(/e-mail/i).fill(ownerA);
  await page.getByLabel(/senha/i).fill(password);
  await page.getByRole('button', { name: /entrar agora/i }).click();
  await expect(page.getByText(/sessao iniciada/i)).toBeVisible();
  const organizationRegion = page.getByRole('region', {
    name: 'Organizacoes e tenant ativo',
  });
  await page.getByLabel(/nome da organizacao/i).fill('Fazenda Santa Maria');
  await organizationRegion.getByRole('button', { name: /^Criar$/i }).click();
  await expect(page.getByText('Fazenda Santa Maria')).toBeVisible();
  await organizationRegion.getByRole('button', { name: /selecionar/i }).click();
  await expect(page.getByText(/Tenant ativo: Fazenda Santa Maria/i)).toBeVisible();

  const loginA = await apiA.post('/v1/auth/login', { data: { email: ownerA, password } });
  expect(loginA.ok()).toBeTruthy();
  const blocked = await apiA.post('/v1/organizations/active', {
    data: { organizationId: orgBId },
  });
  expect(blocked.status()).toBe(404);
  await apiA.dispose();
  await apiB.dispose();
});
