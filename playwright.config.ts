import { delimiter } from 'node:path';

import { defineConfig, devices } from '@playwright/test';

const WEB_PORT = Number(process.env.SAFRAOS_WEB_PORT ?? 8183);
const API_PORT = Number(process.env.SAFRAOS_API_PORT ?? 5183);

// path.delimiter é ";" no Windows e ":" no POSIX — PYTHONPATH usa o mesmo
// separador do PATH da plataforma, então um valor fixo quebra em um dos dois.
const PYTHON_PATH = ['apps/api/src', 'apps/worker/src', 'packages/backend/src'].join(delimiter);

// SPEC-001: o E2E inicia pelo contrato público `npm run dev` — o mesmo
// comando que sobe Postgres/Redis/Mailpit para desenvolvimento — e a partir
// dele sobe API e web. Nenhuma orquestração de infra é duplicada aqui.
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI
    ? [['json', { outputFile: 'test-results/e2e.json' }], ['list']]
    : 'list',
  use: {
    baseURL: `http://localhost:${WEB_PORT}`,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      // `npm run dev` só retorna depois que Postgres/Redis/Mailpit reportam
      // healthy (--wait do Compose); não expõe HTTP, então não há `url` de
      // prontidão — o próprio comando bloqueando é a garantia de prontidão.
      command: 'npm run dev',
      reuseExistingServer: true,
      timeout: 180_000,
    },
    {
      command: 'uv run python -m safraos_api',
      url: `http://localhost:${API_PORT}/health/live`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: { PYTHONPATH: PYTHON_PATH },
    },
    {
      command: 'npm run dev --workspace apps/web',
      url: `http://localhost:${WEB_PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
});
