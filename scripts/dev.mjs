import { existsSync, copyFileSync } from 'node:fs';
import { join } from 'node:path';
import { runOrExit, repoRoot } from './lib/proc.mjs';

/** Primeira execução em checkout limpo não tem `.env`; derivar de `.env.example`. */
const ensureEnvFile = () => {
  const envPath = join(repoRoot, '.env');
  if (existsSync(envPath)) return;

  copyFileSync(join(repoRoot, '.env.example'), envPath);
  console.log('[safraos] .env criado a partir de .env.example');
};

ensureEnvFile();

// `--wait` bloqueia até todo serviço com healthcheck reportar `healthy`,
// e retorna código diferente de zero se algum não ficar saudável.
await runOrExit('docker', ['compose', 'up', '-d', '--wait']);

console.log('[safraos] serviços locais saudáveis');
