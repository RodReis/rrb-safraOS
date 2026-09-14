import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const packageJsonPath = fileURLToPath(new URL('../../package.json', import.meta.url));

const readPackageJson = async () => JSON.parse(await readFile(packageJsonPath, 'utf8'));

/** Contrato público de comandos exigido pela SPEC-001. */
const REQUIRED_SCRIPTS = ['dev', 'stop', 'build', 'lint', 'typecheck', 'test', 'test:e2e'];

describe('contrato raiz do package.json (SPEC-001)', () => {
  test('expõe todos os comandos públicos da fatia', async () => {
    const pkg = await readPackageJson();
    const scripts = pkg.scripts ?? {};

    const missing = REQUIRED_SCRIPTS.filter((name) => !scripts[name]);

    assert.deepEqual(missing, [], `scripts ausentes no package.json: ${missing.join(', ')}`);
  });

  test('nenhum comando público está vazio', async () => {
    const pkg = await readPackageJson();
    const scripts = pkg.scripts ?? {};

    for (const name of REQUIRED_SCRIPTS) {
      assert.equal(
        typeof scripts[name] === 'string' && scripts[name].trim().length > 0,
        true,
        `script "${name}" precisa de um comando real`,
      );
    }
  });
});
