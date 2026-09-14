import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { runOrExit, repoRoot } from './lib/proc.mjs';

// Contrato raiz (tests/**/*.test.mjs) sempre existe desde a SPEC-001 e não
// tem alvo condicional: nunca é not_run.
await runOrExit('node', ['--test', 'tests/**/*.test.mjs']);

if (existsSync(join(repoRoot, 'pyproject.toml'))) {
  // -m "not database" isola provas que exigem Postgres/Redis reais; rodam
  // à parte quando `npm run dev` está de pé (ver docs/TESTING.md).
  await runOrExit('uv', ['run', 'pytest', '-m', 'not database', '-q']);
} else {
  console.log('[safraos] test (backend): not_run (pyproject.toml ainda não existe nesta fatia)');
}

if (existsSync(join(repoRoot, 'apps/web/package.json'))) {
  await runOrExit('npm', ['run', 'test', '--workspace', 'apps/web']);
} else {
  console.log('[safraos] test (apps/web): not_run (apps/web ainda não existe nesta fatia)');
}
