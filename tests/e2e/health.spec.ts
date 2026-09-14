import { expect, test } from '@playwright/test';

// Smoke E2E da SPEC-001: abre a web e confirma que ela reporta o status real
// da API, não um placeholder. Prova de ponta a ponta: web → API → banco/Redis.
test('web exibe status saudável da API', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByText(/api saudável/i)).toBeVisible();
});
