import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

import { toSpawnArgs } from '../../scripts/lib/proc.mjs';

const isWindows = process.platform === 'win32';

describe('toSpawnArgs — portabilidade dos wrappers (SPEC-001)', () => {
  test('shims do Node passam por cmd.exe /c no Windows', () => {
    // Regressão: spawnar "npm.cmd" direto (sem shell) falha com EINVAL —
    // .cmd não é executável sozinho, precisa do cmd.exe para interpretar
    // (Node docs: "Spawning .bat and .cmd files on Windows").
    const result = toSpawnArgs('npm', ['run', 'build']);

    if (isWindows) {
      assert.deepEqual(result, {
        file: 'cmd.exe',
        args: ['/d', '/s', '/c', 'npm', 'run', 'build'],
      });
    } else {
      assert.deepEqual(result, { file: 'npm', args: ['run', 'build'] });
    }
  });

  test('binários nativos vão direto ao spawn, sem cmd.exe', () => {
    for (const command of ['docker', 'uv', 'git', 'node']) {
      assert.deepEqual(toSpawnArgs(command, ['--version']), {
        file: command,
        args: ['--version'],
      });
    }
  });
});
