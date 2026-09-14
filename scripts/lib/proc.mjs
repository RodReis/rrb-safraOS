import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

/** Raiz do repositório, independente de onde o script foi chamado. */
export const repoRoot = fileURLToPath(new URL('../../', import.meta.url));

/**
 * No Windows, os shims do Node são arquivos `.cmd` e o `spawn` sem shell não
 * os resolve sozinho; binários nativos (docker, uv, git) continuam `.exe` e
 * quebrariam com o sufixo. Só os shims conhecidos são reescritos, o que evita
 * depender de shell POSIX sem chutar a extensão de todo comando.
 */
const WINDOWS_CMD_SHIMS = new Set(['npm', 'npx', 'pnpm', 'yarn']);

export const resolveBin = (command) =>
  process.platform === 'win32' && WINDOWS_CMD_SHIMS.has(command) ? `${command}.cmd` : command;

/** Executa um comando herdando stdio e resolve com o código de saída. */
export const run = (command, args, options = {}) =>
  new Promise((resolve, reject) => {
    const child = spawn(resolveBin(command), args, {
      cwd: options.cwd ?? repoRoot,
      stdio: options.stdio ?? 'inherit',
      env: { ...process.env, ...options.env },
    });

    child.on('error', reject);
    child.on('close', (code) => resolve(code ?? 1));
  });

/** Executa e falha o processo atual se o comando retornar código diferente de zero. */
export const runOrExit = async (command, args, options) => {
  const code = await run(command, args, options);
  if (code !== 0) {
    console.error(`\n[safraos] comando falhou (${code}): ${command} ${args.join(' ')}`);
    process.exit(code);
  }
};
