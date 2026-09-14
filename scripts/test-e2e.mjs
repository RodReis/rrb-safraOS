import { delegate } from './lib/delegate.mjs';

await delegate({
  step: 'test:e2e',
  targets: [
    {
      name: 'playwright',
      requires: ['playwright.config.ts'],
      command: 'npx',
      args: ['playwright', 'test'],
    },
  ],
});
