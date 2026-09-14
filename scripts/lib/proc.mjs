import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

/** Raiz do repositório, independente de onde o script foi chamado. */
export const repoRoot = fileURLToPath(new URL('../../', import.meta.url));

/**
 * No Windows, os shims do Node (npm, npx, ...) são scripts `.cmd`, e `.cmd`
 * não é executável sozinho — precisa do `cmd.exe` para interpretar, mesmo
 * com o sufixo (Node child_process docs, "Spawning .bat and .cmd files on
 * Windows"). `shell: true` resolveria, mas depreca args em array (DEP0190,
 * risco de injeção). A forma recomendada é chamar `cmd.exe /c` diretamente,
 * mantendo os args do comando real em array, sem concatenar string alguma.
 * Binários nativos (docker, uv, git) continuam indo direto, sem essa camada.
 */
const WINDOWS_CMD_SHIMS = new Set(['npm', 'npx', 'pnpm', 'yarn']);

export const toSpawnArgs = (command, args) => {
  if (process.platform === 'win32' && WINDOWS_CMD_SHIMS.has(command)) {
    return { file: 'cmd.exe', args: ['/d', '/s', '/c', command, ...args] };
  }
  return { file: command, args };
};

/** Executa um comando herdando stdio e resolve com o código de saída. */
export const run = (command, args, options = {}) =>
  new Promise((resolve, reject) => {
    const { file, args: spawnArgs } = toSpawnArgs(command, args);
    const child = spawn(file, spawnArgs, {
      cwd: options.cwd ?? repoRoot,
      stdio: options.stdio ?? 'inherit',
      env: { ...process.env, ...options.env },
      windowsVerbatimArguments: process.platform === 'win32' && WINDOWS_CMD_SHIMS.has(command),
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
