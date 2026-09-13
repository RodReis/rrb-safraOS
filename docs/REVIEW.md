# Instruções de revisão

Objetivo: defeitos introduzidos pelo delta, verificáveis e acionáveis. Revisão não inventa requisito.

| Prioridade | Critério |
|---|---|
| P0 | corrupção ampla, vazamento entre tenants, segredo exposto, indisponibilidade sistêmica |
| P1 | função principal errada, autorização falha, duplicidade financeira, deploy quebrado, perda offline provável |
| P2 | defeito real relevante com impacto limitado |
| P3 | melhoria localizada que evita erro futuro; não usar para gosto |

P0/P1 bloqueiam. P2 bloqueia se viola aceite/contrato.

Revisar: tenant/objeto; transação/idempotência/concorrência; dinheiro/data/unidade/geometria; offline/retry; migration; contrato externo; logs/PII/segredo; testes; docs/telemetria.

Achado: `[P1] título`; arquivo/linha curta; cenário → comportamento → impacto; correção esperada em uma frase. Não relatar estilo automatizado, hipótese sem cenário, código anterior, duplicata ou elogio.

