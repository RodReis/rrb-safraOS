# Ordem de desenvolvimento

**Revisão:** 2026-09-13. Escopo vem do PRD; numeração vem do `STATUS.md`. Este documento não aloca `SPEC/F`.

## Entrada de uma fatia

Slice identificada; SPEC única/testável; dúvidas de produto resolvidas; par `SPEC-NNN/Fn` reservado; issue canônica; dependências conhecidas. Serviço externo pode usar dublê, mas a limitação fica explícita.

## Ordem técnica recomendada do MVP

| Ordem | Capacidade | Saída verificável |
|---:|---|---|
| 1 | monorepo e CI | lint, typecheck, testes e gate |
| 2 | tenancy, identidade, auditoria | teste negativo entre tenants |
| 3 | fazenda, talhão, geometrias | CRUD e geometria validada |
| 4 | app offline e sync | reenvio, conflito e retomada sem perda |
| 5 | lançamentos e custo | custo por talhão atualizado |
| 6 | plano de contas, rateio, DRE | reconciliação com planilha piloto |
| 7 | NF-e entrada | idempotência e conferência |
| 8 | WhatsApp confirmatório | corpus de 500 casos e fallback |
| 9 | ingestão/compliance | reprocessamento e cobertura por fonte |
| 10 | EUDR/portal | relatório versionado e verificável |
| 11 | LCDPR/exportações | arquivo aceito no piloto |
| 12 | onboarding e piloto | metas F1–F4 medidas |

O PI decide prioridade; mudança deve aparecer no board e no `STATUS.md`.

## Rotina e Definition of Done

Selecionar primeiro `todo` remoto; criar worktree; implementar/testar; revisar; abrir PR; validar SHA atual; squash com gate verde; confirmar merge; marcar `done`. DoD: aceite da SPEC provado, categorias aplicáveis concluídas, isolamento de tenant quando houver dados, migração segura, telemetria sem segredo, docs/evidências atualizadas e `refs #N`.

