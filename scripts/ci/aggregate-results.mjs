/**
 * Consolida os artefatos de teste (JUnit XML / JSON) baixados pelos jobs
 * paralelos. Não reexecuta suíte alguma — só confirma que cada categoria
 * obrigatória produziu evidência rastreável (docs/TESTING.md).
 */

import { existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const artifactsDir = process.argv[2];
if (!artifactsDir) {
  console.error('uso: node aggregate-results.mjs <diretório de artefatos>');
  process.exit(1);
}

const REQUIRED_ARTIFACTS = [
  'test-regras-results',
  'test-banco-results',
  'test-tela-results',
  'e2e-results',
];

const missing = REQUIRED_ARTIFACTS.filter((name) => !existsSync(join(artifactsDir, name)));

if (missing.length > 0) {
  console.error(`[aggregate] artefatos ausentes: ${missing.join(', ')}`);
  console.error('[aggregate] job condicional só pode faltar quando seu contrato disser que não se aplica.');
  process.exit(1);
}

for (const name of REQUIRED_ARTIFACTS) {
  const dir = join(artifactsDir, name);
  const files = readdirSync(dir);
  console.log(`[aggregate] ${name}: ${files.join(', ') || '(vazio)'}`);
  if (files.length === 0) {
    console.error(`[aggregate] ${name} está vazio — evidência ausente é falha, não sucesso.`);
    process.exit(1);
  }
}

console.log('[aggregate] todos os artefatos obrigatórios presentes e não vazios.');
