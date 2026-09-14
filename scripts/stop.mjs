import { runOrExit } from './lib/proc.mjs';

// `docker compose down` age apenas sobre o projeto `safraos` declarado em
// compose.yaml: containers de outros projetos da máquina não são tocados.
// Sem `-v` de propósito — parar o ambiente não descarta dados locais.
await runOrExit('docker', ['compose', 'down', '--remove-orphans']);

console.log('[safraos] serviços locais encerrados (volumes preservados)');
