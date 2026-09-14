import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

import { resolveBin } from '../../scripts/lib/proc.mjs';

const isWindows = process.platform === 'win32';

describe('resolveBin — portabilidade dos wrappers (SPEC-001)', () => {
  test('shims do Node recebem .cmd no Windows', () => {
    assert.equal(resolveBin('npm'), isWindows ? 'npm.cmd' : 'npm');
    assert.equal(resolveBin('npx'), isWindows ? 'npx.cmd' : 'npx');
  });

  test('binários nativos nunca recebem .cmd', () => {
    // Regressão: sufixar todo comando quebrava `spawn docker` com EINVAL,
    // porque o Docker publica docker.exe e não docker.cmd.
    for (const command of ['docker', 'uv', 'git', 'node']) {
      assert.equal(resolveBin(command), command);
    }
  });
});
