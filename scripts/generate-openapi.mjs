import { resolve } from 'node:path';

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

const API_BASE_URL = process.env.VITE_API_BASE_URL ?? 'http://localhost:5183';
const OUTPUT_PATH = resolve('apps/web/src/lib/api-types.ts');

async function main() {
  const schemaUrl = `${API_BASE_URL}/openapi.json`;
  const checkOnly = process.argv.includes('--check');

  console.log(
    `[safraos] generate:openapi: ${checkOnly ? 'verificando' : 'buscando'} schema em ${schemaUrl}`,
  );

  const code = await run('npx', [
    '--yes',
    `--package=openapi-typescript@${OPENAPI_TYPESCRIPT_VERSION}`,
    `--package=typescript@${TYPESCRIPT_PEER_VERSION}`,
    '--',
    'openapi-typescript',
    schemaUrl,
    '-o',
    OUTPUT_PATH,
    ...(checkOnly ? ['--check'] : []),
  ]);

  if (code !== 0) {
    if (checkOnly) {
      console.error(
        '[safraos] generate:openapi: apps/web/src/lib/api-types.ts esta desatualizado ' +
          'ou a API nao respondeu em ' +
          schemaUrl +
          '. A API precisa estar rodando (`npm run dev` + servidor uvicorn de pe). ' +
          'Rode `npm run generate:openapi` e commite o resultado.',
      );
    } else {
      console.error(
        `[safraos] generate:openapi: falhou ao buscar ${schemaUrl}. ` +
          'A API precisa estar rodando (`npm run dev` + servidor uvicorn de pe).',
      );
    }
    process.exit(code);
  }

  if (!checkOnly) {
    console.log(`[safraos] generate:openapi: escrito em ${OUTPUT_PATH}`);
  } else {
    console.log('[safraos] generate:openapi: OK, sem drift.');
  }
}

main();
