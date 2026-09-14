import { delegate } from './lib/delegate.mjs';

await delegate({
  step: 'build',
  targets: [
    {
      name: 'apps/web',
      requires: ['apps/web/package.json'],
      command: 'npm',
      args: ['run', 'build', '--workspace', 'apps/web'],
    },
  ],
});
