import { expect, request, test } from '@playwright/test';

const API_PORT = Number(process.env.SAFRAOS_API_PORT ?? 5183);
const MAILPIT_PORT = Number(process.env.SAFRAOS_MAILPIT_UI_PORT ?? 8126);
const API_BASE = `http://localhost:${API_PORT}`;
const MAILPIT_BASE = `http://localhost:${MAILPIT_PORT}`;

const MUNICIPIO_IBGE_CODE = '5208707'; // Goiania (GO) — seedado

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

function polygonNear(lngOffset: number, latOffset: number) {
  const baseLng = -49.0 + lngOffset;
  const baseLat = -16.0 + latOffset;
  return {
    type: 'Polygon',
    coordinates: [
      [
        [baseLng, baseLat],
        [baseLng, baseLat - 0.005],
        [baseLng + 0.005, baseLat - 0.005],
        [baseLng + 0.005, baseLat],
        [baseLng, baseLat],
      ],
    ],
  };
}

test.describe('Talhões', () => {
  test('import de GeoJSON cria talhão e mostra área calculada pelo backend', async ({ page }) => {
    const suffix = Date.now();
    const password = 'senha-longa-segura';
    const owner = `talhao-owner-${suffix}@example.com`;

    await createActiveUser(owner, password);

    await page.goto('/');
    await page.getByLabel(/e-mail/i).fill(owner);
    await page.getByLabel(/senha/i).fill(password);
    await page.getByRole('button', { name: /entrar agora/i }).click();
    await expect(page.getByText(/sessao iniciada/i)).toBeVisible();

    const organizationRegion = page.getByRole('region', {
      name: 'Organizacoes e tenant ativo',
    });
    await page.getByLabel(/nome da organizacao/i).fill('Fazenda Talhao E2E');
    await organizationRegion.getByRole('button', { name: /^Criar$/i }).click();
    await expect(page.getByText('Fazenda Talhao E2E')).toBeVisible();
    await organizationRegion.getByRole('button', { name: /selecionar/i }).click();
    await expect(page.getByText(/Tenant ativo: Fazenda Talhao E2E/i)).toBeVisible();

    const farmResponse = await page.request.post(`${API_BASE}/v1/farms`, {
      data: { name: 'Fazenda Seed E2E', uf: 'GO', municipioIbgeCode: MUNICIPIO_IBGE_CODE },
    });
    expect(farmResponse.status(), await farmResponse.text()).toBe(201);
    const farm = (await farmResponse.json()) as { id: string };

    await page.goto(`/fazendas/${farm.id}/talhoes`);
    await expect(page.getByRole('heading', { name: 'Talhões' })).toBeVisible();

    await page.getByRole('button', { name: 'Novo talhão' }).click();
    await page.getByLabel(/nome do talhão/i).fill('Talhao E2E');

    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.getByLabel(/importar arquivo geojson/i).click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
      name: 'talhao.geojson',
      mimeType: 'application/geo+json',
      buffer: Buffer.from(JSON.stringify(polygonNear(0, 0))),
    });

    const createResponsePromise = page.waitForResponse(
      (response) =>
        response.url().includes('/v1/talhoes') && response.request().method() === 'POST',
    );
    await page.getByRole('button', { name: /salvar talhão/i }).click();
    const createResponse = await createResponsePromise;
    const createdTalhao = (await createResponse.json()) as { areaHa: string };

    const talhaoRow = page.getByRole('row', { name: /Talhao E2E/i });
    await expect(talhaoRow).toBeVisible();
    // area exibida na tela deve ser exatamente o valor areaHa retornado pela API
    // de criacao (string decimal simples, ex. "1.2345") — nao apenas "algum
    // numero decimal existe na pagina". Ver TalhaoColumns.tsx (accessorKey
    // "areaHa", sem formatacao) e apps/api/.../talhoes/router.py.
    await expect(talhaoRow.getByText(createdTalhao.areaHa, { exact: true })).toBeVisible();

    await page.screenshot({ path: 'tests/e2e/screenshots/talhoes-list.png', fullPage: true });
  });

  test('mapa e lista nao expoe talhao de outro tenant/usuario', async ({ page }) => {
    const suffix = Date.now();
    const password = 'senha-longa-segura';
    const ownerA = `talhao-tenant-a-${suffix}@example.com`;
    const ownerB = `talhao-tenant-b-${suffix}@example.com`;

    const apiA = await createActiveUser(ownerA, password);
    const apiB = await createActiveUser(ownerB, password);

    // Usuario A: login e organizacao pela UI (cookie de sessao/tenant ativo vive
    // no browser context de page; fazenda/talhao proprios via page.request, que
    // compartilha esses cookies).
    await page.goto('/');
    await page.getByLabel(/e-mail/i).fill(ownerA);
    await page.getByLabel(/senha/i).fill(password);
    await page.getByRole('button', { name: /entrar agora/i }).click();
    await expect(page.getByText(/sessao iniciada/i)).toBeVisible();

    const organizationRegion = page.getByRole('region', {
      name: 'Organizacoes e tenant ativo',
    });
    await page.getByLabel(/nome da organizacao/i).fill('Organizacao Talhao A');
    await organizationRegion.getByRole('button', { name: /^Criar$/i }).click();
    await expect(organizationRegion.getByText('Organizacao Talhao A')).toBeVisible();
    await organizationRegion.getByRole('button', { name: /selecionar/i }).click();
    await expect(page.getByText(/Tenant ativo: Organizacao Talhao A/i)).toBeVisible();

    const farmAResponse = await page.request.post(`${API_BASE}/v1/farms`, {
      data: { name: 'Fazenda Talhao A', uf: 'GO', municipioIbgeCode: MUNICIPIO_IBGE_CODE },
    });
    expect(farmAResponse.status(), await farmAResponse.text()).toBe(201);
    const farmA = (await farmAResponse.json()) as { id: string };

    const talhaoAResponse = await page.request.post(`${API_BASE}/v1/talhoes`, {
      data: { farmId: farmA.id, name: 'Talhao Usuario A', geometry: polygonNear(0, 0) },
    });
    expect(talhaoAResponse.status(), await talhaoAResponse.text()).toBe(201);

    // Usuario B: 100% via API direta (apiB), organizacao/fazenda/talhao proprios,
    // sem nunca participar da UI — usado so na verificacao de isolamento.
    const loginB = await apiB.post('/v1/auth/login', { data: { email: ownerB, password } });
    expect(loginB.ok()).toBeTruthy();
    const orgB = await apiB.post('/v1/organizations', { data: { name: 'Organizacao Talhao B' } });
    expect(orgB.status()).toBe(201);
    const orgBId = ((await orgB.json()) as { id: string }).id;
    const activateB = await apiB.post('/v1/organizations/active', {
      data: { organizationId: orgBId },
    });
    expect(activateB.ok()).toBeTruthy();

    const farmBResponse = await apiB.post('/v1/farms', {
      data: { name: 'Fazenda Talhao B', uf: 'GO', municipioIbgeCode: MUNICIPIO_IBGE_CODE },
    });
    expect(farmBResponse.status(), await farmBResponse.text()).toBe(201);
    const farmB = (await farmBResponse.json()) as { id: string };

    const talhaoBResponse = await apiB.post('/v1/talhoes', {
      data: { farmId: farmB.id, name: 'Talhao Usuario B', geometry: polygonNear(0.02, 0) },
    });
    expect(talhaoBResponse.status(), await talhaoBResponse.text()).toBe(201);

    // (a) Usuario A, logado, ve so o talhao da propria fazenda — nunca o do B.
    await page.goto(`/fazendas/${farmA.id}/talhoes`);
    await expect(page.getByText('Talhao Usuario A')).toBeVisible();
    await expect(page.getByText('Talhao Usuario B')).not.toBeVisible();

    // (b) Isolamento real de tenant: usuario A (via page.request, que carrega os
    // cookies/sessao de A) tenta acessar talhoes da fazenda do usuario B. Farm de
    // outro tenant nao resolve nenhuma linha — resposta vazia, nunca expoe o
    // talhao de B.
    const crossTenantList = await page.request.get(`${API_BASE}/v1/talhoes?farmId=${farmB.id}`);
    expect(crossTenantList.ok()).toBeTruthy();
    const crossTenantItems = ((await crossTenantList.json()) as {
      items: Array<{ name: string }>;
    }).items;
    expect(crossTenantItems.find((item) => item.name === 'Talhao Usuario B')).toBeUndefined();
    expect(crossTenantItems).toHaveLength(0);

    await apiA.dispose();
    await apiB.dispose();
  });
});
