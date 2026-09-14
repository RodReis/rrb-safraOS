import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { delimiter, join, resolve } from 'node:path';

import { run } from './lib/proc.mjs';

/**
 * openapi-typescript exige `typescript@^5.x` em tempo de execução (usa
 * `ts.factory` da API interna do compilador), incompativel com o
 * `typescript@^7` fixado na raiz do monorepo para o restante do projeto.
 * Rodar via `npx --package` pinado isola essa dependência sem forçar o
 * projeto inteiro a uma versão de TypeScript mais antiga — `npx` cacheia os
 * pacotes localmente após o primeiro download, então runs subsequentes (CI
 * com cache quente) não pagam custo extra de rede.
 */
const OPENAPI_TYPESCRIPT_VERSION = '7.13.0';
const TYPESCRIPT_PEER_VERSION = '5.9.3';

const OUTPUT_PATH = resolve('apps/web/src/lib/api-types.ts');

const PYTHONPATH_ENTRIES = ['apps/api/src', 'apps/worker/src', 'packages/backend/src'];

/**
 * O schema vem direto de `app.openapi()` (extração estática via Python), não
 * de uma requisição HTTP a um servidor uvicorn. `create_async_engine` no
 * `main.py` só monta o pool de conexão em memória — não conecta de verdade
 * até a primeira query — então isso funciona sem Postgres/Redis/uvicorn de
 * pé, tanto localmente quanto no job `quality` do CI (que roda
 * `npm run typecheck` sem nenhuma infra de banco).
 */
async function extractSchema(schemaPath) {
  const pythonCode =
    'import json; from safraos_api.main import app; ' +
    `open(${JSON.stringify(schemaPath)}, "w", encoding="utf-8").write(json.dumps(app.openapi()))`;

  const code = await run('uv', ['run', 'python', '-c', pythonCode], {
    env: { PYTHONPATH: PYTHONPATH_ENTRIES.join(delimiter) },
  });

  if (code !== 0) {
    console.error(
      '[safraos] generate:openapi: falhou ao extrair o schema OpenAPI via ' +
        '`uv run python -c "... app.openapi() ..."`. Verifique se `uv sync` foi rodado ' +
        'e se o pacote `safraos_api` importa sem erros.',
    );
    process.exit(code);
  }
}

async function main() {
  const checkOnly = process.argv.includes('--check');

  console.log(
    `[safraos] generate:openapi: ${checkOnly ? 'verificando' : 'gerando'} tipos a partir do schema OpenAPI (extração estática, sem servidor)`,
  );

  const tmpDir = mkdtempSync(join(tmpdir(), 'safraos-openapi-'));
  const schemaPath = join(tmpDir, 'openapi.json');

  try {
    await extractSchema(schemaPath);

    const code = await run('npx', [
      '--yes',
      `--package=openapi-typescript@${OPENAPI_TYPESCRIPT_VERSION}`,
      `--package=typescript@${TYPESCRIPT_PEER_VERSION}`,
      '--',
      'openapi-typescript',
      schemaPath,
      '-o',
      OUTPUT_PATH,
      ...(checkOnly ? ['--check'] : []),
    ]);

    if (code !== 0) {
      if (checkOnly) {
        console.error(
          '[safraos] generate:openapi: apps/web/src/lib/api-types.ts esta desatualizado. ' +
            'Rode `npm run generate:openapi` e commite o resultado.',
        );
      } else {
        console.error('[safraos] generate:openapi: falhou ao gerar os tipos.');
      }
      process.exit(code);
    }

    if (!checkOnly) {
      console.log(`[safraos] generate:openapi: escrito em ${OUTPUT_PATH}`);
    } else {
      console.log('[safraos] generate:openapi: OK, sem drift.');
    }
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
}

main();
