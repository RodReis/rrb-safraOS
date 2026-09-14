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

test('usuario cadastra e arquiva fazenda por teclado; tenant alheio nao acessa', async ({
  page,
}) => {
  const suffix = Date.now();
  const password = 'senha-longa-segura';
  const ownerA = `farm-owner-a-${suffix}@example.com`;
  const ownerB = `farm-owner-b-${suffix}@example.com`;

  const apiA = await createActiveUser(ownerA, password);
  const apiB = await createActiveUser(ownerB, password);

  // Login e criacao/selecao de organizacao pela UI (o cookie de sessao/tenant do
  // usuario A precisa viver no mesmo browser context usado para acessar /fazendas).
  await page.goto('/');
  await page.getByLabel(/e-mail/i).fill(ownerA);
  await page.getByLabel(/senha/i).fill(password);
  await page.getByRole('button', { name: /entrar agora/i }).click();
  await expect(page.getByText(/sessao iniciada/i)).toBeVisible();

  const organizationRegion = page.getByRole('region', {
    name: 'Organizacoes e tenant ativo',
  });
  await page.getByLabel(/nome da organizacao/i).fill('Fazenda Owner A');
  await organizationRegion.getByRole('button', { name: /^Criar$/i }).click();
  await expect(page.getByText('Fazenda Owner A')).toBeVisible();
  await organizationRegion.getByRole('button', { name: /selecionar/i }).click();
  await expect(page.getByText(/Tenant ativo: Fazenda Owner A/i)).toBeVisible();

  // Usuario B tambem precisa de organizacao ativa propria, criada via API direta
  // (nao participa da UI neste teste — usado so na verificacao de isolamento).
  const loginB = await apiB.post('/v1/auth/login', { data: { email: ownerB, password } });
  expect(loginB.ok()).toBeTruthy();
  const orgB = await apiB.post('/v1/organizations', { data: { name: 'Fazenda Owner B' } });
  expect(orgB.status()).toBe(201);
  const orgBId = ((await orgB.json()) as { id: string }).id;
  const activateB = await apiB.post('/v1/organizations/active', {
    data: { organizationId: orgBId },
  });
  expect(activateB.ok()).toBeTruthy();

  await page.goto('/fazendas');
  await expect(page.getByRole('heading', { name: 'Fazendas' })).toBeVisible();

  // Abre o formulario e navega por teclado: Tab entre campos, preenche, Enter submete.
  await page.getByRole('button', { name: 'Nova fazenda' }).click();

  const nameInput = page.locator('#farm-name');
  await nameInput.click();
  await nameInput.pressSequentially('Fazenda Santa Luzia');
  await page.keyboard.press('Tab');

  const ufInput = page.locator('#farm-uf');
  await expect(ufInput).toBeFocused();
  await page.keyboard.type('GO');
  await page.keyboard.press('Tab');

  const municipioSelect = page.locator('#farm-municipio');
  await expect(municipioSelect).toBeFocused();
  await municipioSelect.selectOption({ label: 'Goiania (GO)' });
  await page.keyboard.press('Tab');

  const submitButton = page.getByRole('button', { name: 'Salvar' });
  await expect(submitButton).toBeFocused();
  await page.keyboard.press('Enter');

  await expect(page.getByText(/fazenda criada com sucesso/i)).toBeVisible();
  const row = page.getByRole('row', { name: /Fazenda Santa Luzia/i });
  await expect(row).toBeVisible();

  // Descobre o id da fazenda criada via page.request, que compartilha os cookies de
  // sessao/tenant do proprio browser context (apiA nunca fez login pela UI).
  const listResponse = await page.request.get(`${API_BASE}/v1/farms`);
  expect(listResponse.ok()).toBeTruthy();
  const farms = ((await listResponse.json()) as {
    items: Array<{ id: string; name: string }>;
  }).items;
  const createdFarm = farms.find((farm) => farm.name === 'Fazenda Santa Luzia');
  if (!createdFarm) throw new Error('Fazenda criada nao encontrada via API');

  // Arquiva via AlertDialog navegando por teclado ate o botao "Arquivar" da linha e confirmando.
  const archiveButton = row.getByRole('button', { name: 'Arquivar' });
  await archiveButton.focus();
  await page.keyboard.press('Enter');

  const alertDialog = page.getByRole('alertdialog');
  await expect(alertDialog).toBeVisible();
  await expect(alertDialog.getByText('Arquivar fazenda?')).toBeVisible();
  const confirmButton = alertDialog.getByRole('button', { name: 'Confirmar arquivamento' });
  await confirmButton.focus();
  await page.keyboard.press('Enter');

  await expect(page.getByText(/fazenda arquivada/i)).toBeVisible();
  await expect(page.getByRole('row', { name: /Fazenda Santa Luzia/i })).toHaveCount(0);

  // Tenant alheio (usuario B, organizacao propria ativa) nao acessa a fazenda do usuario A:
  // tentativa de atualizar e de arquivar pelo id devem retornar 404 problem+json.
  const crossTenantUpdate = await apiB.put(`/v1/farms/${createdFarm.id}`, {
    data: { name: 'Tentativa invasao', uf: 'GO', municipioIbgeCode: '5208707' },
  });
  expect(crossTenantUpdate.status()).toBe(404);
  const updateProblem = (await crossTenantUpdate.json()) as { type?: string; code?: string };
  expect(updateProblem.code).toBe('farms.not_found');

  const crossTenantArchive = await apiB.post(`/v1/farms/${createdFarm.id}/archive`, {});
  expect(crossTenantArchive.status()).toBe(404);
  const archiveProblem = (await crossTenantArchive.json()) as { type?: string; code?: string };
  expect(archiveProblem.code).toBe('farms.not_found');

  await page.screenshot({ path: 'tests/e2e/screenshots/farms-list.png', fullPage: true });

  await apiA.dispose();
  await apiB.dispose();
});
