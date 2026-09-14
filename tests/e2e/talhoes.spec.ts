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

    await page.getByRole('button', { name: /salvar talhão/i }).click();

    await expect(page.getByText('Talhao E2E')).toBeVisible();
    // area formatada como string decimal simples vinda do backend (str(Decimal),
    // ponto decimal) — ex. "1.2345", nunca com virgula pt-BR. Ver
    // apps/api/src/safraos_api/modules/talhoes/router.py.
    await expect(page.getByText(/\d+\.\d+/)).toBeVisible();

    await page.screenshot({ path: 'tests/e2e/screenshots/talhoes-list.png', fullPage: true });
  });

  test('mapa e lista não mantêm talhões de outro tenant após troca de organização', async ({
    page,
  }) => {
    const suffix = Date.now();
    const password = 'senha-longa-segura';
    const owner = `talhao-tenant-${suffix}@example.com`;

    await createActiveUser(owner, password);

    // Login unico pela UI: o cookie de sessao/tenant ativo do navegador so muda
    // atraves de requisicoes feitas com page.request (compartilham os cookies do
    // browser context) ou de cliques na UI — nunca de um APIRequestContext a parte.
    await page.goto('/');
    await page.getByLabel(/e-mail/i).fill(owner);
    await page.getByLabel(/senha/i).fill(password);
    await page.getByRole('button', { name: /entrar agora/i }).click();
    await expect(page.getByText(/sessao iniciada/i)).toBeVisible();

    const organizationRegion = page.getByRole('region', {
      name: 'Organizacoes e tenant ativo',
    });

    // Organizacao A pela UI (cria e ativa), fazenda e talhao proprios via
    // page.request (herdando os cookies do tenant A recem-ativado).
    await page.getByLabel(/nome da organizacao/i).fill('Organizacao A E2E');
    await organizationRegion.getByRole('button', { name: /^Criar$/i }).click();
    await expect(organizationRegion.getByText('Organizacao A E2E')).toBeVisible();
    await organizationRegion
      .locator('li', { hasText: 'Organizacao A E2E' })
      .getByRole('button', { name: /selecionar/i })
      .click();
    await expect(page.getByText(/Tenant ativo: Organizacao A E2E/i)).toBeVisible();

    const farmAResponse = await page.request.post(`${API_BASE}/v1/farms`, {
      data: { name: 'Fazenda Org A', uf: 'GO', municipioIbgeCode: MUNICIPIO_IBGE_CODE },
    });
    expect(farmAResponse.status(), await farmAResponse.text()).toBe(201);
    const farmA = (await farmAResponse.json()) as { id: string };

    const talhaoAResponse = await page.request.post(`${API_BASE}/v1/talhoes`, {
      data: { farmId: farmA.id, name: 'Talhao Org A', geometry: polygonNear(0, 0) },
    });
    expect(talhaoAResponse.status(), await talhaoAResponse.text()).toBe(201);

    // Organizacao B: mesmo usuario, segunda organizacao com fazenda e talhao
    // proprios, tambem via UI + page.request (agora com o tenant B ativo).
    await page.getByLabel(/nome da organizacao/i).fill('Organizacao B E2E');
    await organizationRegion.getByRole('button', { name: /^Criar$/i }).click();
    await expect(organizationRegion.getByText('Organizacao B E2E')).toBeVisible();
    await organizationRegion
      .locator('li', { hasText: 'Organizacao B E2E' })
      .getByRole('button', { name: /selecionar/i })
      .click();
    await expect(page.getByText(/Tenant ativo: Organizacao B E2E/i)).toBeVisible();

    const farmBResponse = await page.request.post(`${API_BASE}/v1/farms`, {
      data: { name: 'Fazenda Org B', uf: 'GO', municipioIbgeCode: MUNICIPIO_IBGE_CODE },
    });
    expect(farmBResponse.status(), await farmBResponse.text()).toBe(201);
    const farmB = (await farmBResponse.json()) as { id: string };

    const talhaoBResponse = await page.request.post(`${API_BASE}/v1/talhoes`, {
      data: { farmId: farmB.id, name: 'Talhao Org B', geometry: polygonNear(0.02, 0) },
    });
    expect(talhaoBResponse.status(), await talhaoBResponse.text()).toBe(201);

    // Tenant B ainda ativo: a lista/mapa da fazenda B mostra o talhao B, nunca o A.
    await page.goto(`/fazendas/${farmB.id}/talhoes`);
    await expect(page.getByText('Talhao Org B')).toBeVisible();
    await expect(page.getByText('Talhao Org A')).not.toBeVisible();

    // Trocar tenant ativo de volta para a Organizacao A pela UI (OrganizationPanel
    // em "/") e confirmar que a lista da fazenda A mostra so o talhao A.
    await page.goto('/');
    await expect(organizationRegion.getByText('Organizacao A E2E')).toBeVisible();
    await organizationRegion
      .locator('li', { hasText: 'Organizacao A E2E' })
      .getByRole('button', { name: /selecionar/i })
      .click();
    await expect(page.getByText(/Tenant ativo: Organizacao A E2E/i)).toBeVisible();

    await page.goto(`/fazendas/${farmA.id}/talhoes`);
    await expect(page.getByText('Talhao Org A')).toBeVisible();
    await expect(page.getByText('Talhao Org B')).not.toBeVisible();

    // Isolamento tambem via API direta com o tenant A ativo: a fazenda B
    // pertence a outro tenant, entao listar talhoes por ela nao deve trazer o
    // talhao da organizacao B (repositorio filtra por organization_id do
    // farm_id, farm de outro tenant nao resolve nenhuma linha).
    const crossTenantList = await page.request.get(
      `${API_BASE}/v1/talhoes?farmId=${farmB.id}`,
    );
    expect(crossTenantList.ok()).toBeTruthy();
    const crossTenantItems = ((await crossTenantList.json()) as {
      items: Array<{ name: string }>;
    }).items;
    expect(crossTenantItems.find((item) => item.name === 'Talhao Org B')).toBeUndefined();
  });
});
