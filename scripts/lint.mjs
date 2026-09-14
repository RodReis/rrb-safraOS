import { delegate } from './lib/delegate.mjs';

await delegate({
  step: 'lint',
  targets: [
    {
      name: 'apps/web',
      requires: ['apps/web/package.json', 'apps/web/eslint.config.js'],
      command: 'npm',
      args: ['run', 'lint', '--workspace', 'apps/web'],
    },
    {
      name: 'backend (ruff)',
      requires: ['pyproject.toml'],
      command: 'uv',
      args: ['run', 'ruff', 'check', '.'],
    },
  ],
});
