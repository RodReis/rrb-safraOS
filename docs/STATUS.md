# Status do SafraOS

**Atualizado:** 2026-09-13
**Estado:** MVP0 especificado, planejado e com issues abertas; implementação não iniciada.
**Repositório:** `RodReis/rrb-safraOS` (GitHub, privado, branch padrão `main`).

## Agora

- Cinco issues de MVP0 (F1 a F5) abertas em `proplan:todo`, na ordem de implementação.
- Code inicia sempre pelo primeiro `todo` da ordem (issue #1, SPEC-001/F1).
- Não iniciar mobile: ele está adiado para o final do projeto (`docs/FORA-DE-ESCOPO.md`).

## Kanban

| Estado | Itens |
|---|---|
| Planejado | ADR-004, ADR-006, ADR-007 e ADR-008 (abertas) |
| Backlog | vazio |
| Todo | SPEC-001/F1 a SPEC-005/F5 do MVP0 (issues #1–#5) |
| Doing / Done / Finalizado | vazio |

O GitHub remoto prevalece para execução; esta tabela não substitui consulta ao board.

## Índice Fatia ↔ SPEC

| Sequência | MVP | Slice | SPEC | Fatia | Issue | Estado |
|---:|---|---|---|---|---|---|
| 001 | MVP0 | Fundação executável e CI | SPEC-001 | F1 | [#1](https://github.com/RodReis/rrb-safraOS/issues/1) | todo |
| 002 | MVP0 | Identidade, sessão e e-mail | SPEC-002 | F2 | [#2](https://github.com/RodReis/rrb-safraOS/issues/2) | todo |
| 003 | MVP0 | Organização, tenancy e auditoria | SPEC-003 | F3 | [#3](https://github.com/RodReis/rrb-safraOS/issues/3) | todo |
| 004 | MVP0 | Fazendas | SPEC-004 | F4 | [#4](https://github.com/RodReis/rrb-safraOS/issues/4) | todo |
| 005 | MVP0 | Talhões, GeoJSON e mapa | SPEC-005 | F5 | [#5](https://github.com/RodReis/rrb-safraOS/issues/5) | todo |

Próximo número disponível: `006`. Número reservado nunca é reutilizado. Detalhe histórico vai para `STATUS-ARQUIVO.md`.

## Decisões vigentes (resumo — texto integral em `docs/DECISIONS.md` e `docs/adr/`)

- ADR-001 — backend Python/FastAPI; Node 24/TS em web/mobile. Aceita.
- ADR-002 — monólito modular (nenhum serviço separado por deploy no MVP0). Aceita.
- ADR-003 — `docs/PRIVACIDADE.md` é documento autônomo, sem efeito sobre produto. Aceita.
- ADR-005 — Celery/Redis como processamento assíncrono do MVP. Aceita.
- ADR-009 — web antes do mobile; offline-first é meta do produto (PRD v2.1), não do MVP0. Aceita.
- PRD na versão 2.1 (emenda de 2026-09-13); documentos concorrentes (`BACKLOG.md`, `Arquitetura.md` v1.0, brief executivo) arquivados em `docs/historico/`, sem efeito de contrato.
- Paleta de marca é azul institucional (`docs/design/DESIGN-CLARO.md`/`DESIGN-ESCURO.md`); verde reservado ao semáforo (`docs/design-system/TOKENS.md`).

## Riscos imediatos

Portas locais serão definidas uma única vez na execução da F1 conforme `CLAUDE.md`, e registradas em `.env.example`.

Detalhes de itens adiados ou excluídos ficam em `docs/FORA-DE-ESCOPO.md`.
