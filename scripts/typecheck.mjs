import { delegate } from './lib/delegate.mjs';

await delegate({
  step: 'typecheck',
  targets: [
    {
      name: 'raiz (playwright.config.ts, tests/e2e)',
      requires: ['tsconfig.json'],
      command: 'npx',
      args: ['tsc', '--noEmit'],
    },
    {
      name: 'apps/web: openapi anti-drift (extração estática, sem servidor)',
      requires: ['scripts/generate-openapi.mjs', 'apps/web/src/lib/api-types.ts'],
      command: 'node',
      args: ['scripts/generate-openapi.mjs', '--check'],
    },
    {
      name: 'apps/web',
      requires: ['apps/web/tsconfig.json'],
      command: 'npm',
      args: ['run', 'typecheck', '--workspace', 'apps/web'],
    },
    {
      name: 'backend (mypy)',
      requires: ['pyproject.toml'],
      command: 'uv',
      args: ['run', 'mypy', '.'],
    },
  ],
});
