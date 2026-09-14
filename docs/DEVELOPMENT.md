# Ordem de desenvolvimento

**Revisão:** 2026-09-13. Escopo vem do PRD; numeração vem do `STATUS.md`. Este documento não aloca `SPEC/F`.

## Entrada de uma fatia

Slice identificada; SPEC única/testável; dúvidas de produto resolvidas; par `SPEC-NNN/Fn` reservado; issue canônica; dependências conhecidas. Serviço externo pode usar dublê, mas a limitação fica explícita.

## Ordem técnica recomendada do MVP

| Ordem | Capacidade | Saída verificável |
|---:|---|---|
| 1 | monorepo e CI | lint, typecheck, testes e gate |
| 2 | tenancy, identidade, auditoria | teste negativo entre tenants |
| 3 | fazenda, talhão e mapa web | CRUD e geometria validada |
| 4 | lançamentos e custo | custo por talhão atualizado |
| 5 | plano de contas, rateio e DRE | reconciliação com planilha piloto |
| 6 | NF-e entrada | idempotência e conferência |
| 7 | WhatsApp confirmatório | corpus de 500 casos e fallback |
| 8 | ingestão/compliance | reprocessamento e cobertura por fonte |
| 9 | EUDR/portal | relatório versionado e verificável |
| 10 | LCDPR/exportações | arquivo aceito no piloto |
| 11 | onboarding e piloto web | metas web de F1–F4 medidas |
| 12 | app mobile offline e sync | reenvio, conflito e retomada sem perda |

O PI decide prioridade; mudança deve aparecer no board e no `STATUS.md`.

## Rotina e Definition of Done

Selecionar primeiro `todo` remoto; criar worktree; implementar/testar; revisar; abrir PR; validar SHA atual; squash com gate verde; confirmar merge; marcar `done`. DoD: aceite da SPEC provado, categorias aplicáveis concluídas, isolamento de tenant quando houver dados, migração segura, telemetria sem segredo, docs/evidências atualizadas e `refs #N`.

## Entrega finalizada — SPEC-002/F2

- Implementados domínio de identidade, Argon2id, tokens externos com hash, migration de users/sessions/tokens/outbox, API `/v1/auth/*`, tarefa Celery de e-mail e tela web de autenticação.
- Validação local executada: `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`, `uv run pytest -m database -q` e `npm run test:e2e`.
- Validação real de banco, Celery, Redis e Mailpit passou após iniciar Docker Desktop e aplicar `uv run alembic upgrade head`.

## Entrega em andamento — SPEC-003/F3

- Implementados domínio de organização, migration de `organizations`, `organization_memberships` e `audit_events`, role `safraos_app` sem `BYPASSRLS`, policies RLS por membership e auditoria append-only.
- Implementados endpoints `/v1/organizations` e `/v1/organizations/active` com sessão autenticada, seleção de tenant entre memberships e resposta neutra para tenant alheio.
- Implementado painel web para criar/listar organizações próprias e selecionar tenant ativo.
- Validação local executada até agora: `npm test`, `npm run lint`, `npm run typecheck`, `npm run build`, `npm run test:e2e` e `python -m pytest -m database tests/database/test_organizations_migration.py`.
