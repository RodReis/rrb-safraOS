import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { run, repoRoot } from './proc.mjs';

/**
 * Executa uma etapa de qualidade delegando ao alvo real quando ele existe.
 *
 * Enquanto a fatia que cria o alvo não foi entregue, a etapa reporta
 * `not_run` e sai com sucesso — SPEC-001 entrega o contrato de comandos, não
 * as implementações. O que nunca pode acontecer é o inverso: uma etapa cujo
 * alvo existe falhar em silêncio ou ser reportada como PASS sem rodar.
 */
export const delegate = async ({ step, targets }) => {
  const available = targets.filter(({ requires }) =>
    requires.every((path) => existsSync(join(repoRoot, path))),
  );

  const skipped = targets.filter((target) => !available.includes(target));
  for (const { name } of skipped) {
    console.log(`[safraos] ${step}: not_run (${name} ainda não existe nesta fatia)`);
  }

  if (available.length === 0) {
    console.log(`[safraos] ${step}: nenhum alvo executável no checkout atual`);
    return;
  }

  for (const { name, command, args, cwd } of available) {
    console.log(`[safraos] ${step}: ${name}`);
    const code = await run(command, args, cwd ? { cwd: join(repoRoot, cwd) } : undefined);
    if (code !== 0) {
      console.error(`[safraos] ${step} falhou em ${name} (código ${code})`);
      process.exit(code);
    }
  }
};
