# Status do SafraOS

**Atualizado:** 2026-09-13
**Estado:** MVP0 especificado e planejado; implementação não iniciada.

## Agora

- Revisar as cinco SPECs e o plano mestre do MVP0.
- Criar issues na ordem F1 → F5 somente após confirmação final do PI.
- Não iniciar mobile: ele está adiado para o final do projeto.

## Kanban

| Estado | Itens |
|---|---|
| Planejado | SPEC-001/F1 a SPEC-005/F5 do MVP0; ADR-002, ADR-004 e ADR-006 a ADR-008 |
| Backlog / Todo / Doing / Done / Finalizado | vazio |

O GitHub remoto prevalece para execução; esta tabela não substitui consulta ao board.

## Índice Fatia ↔ SPEC

| Sequência | MVP | Slice | SPEC | Fatia | Issue | Estado |
|---:|---|---|---|---|---|---|
| 001 | MVP0 | Fundação executável e CI | SPEC-001 | F1 | — | planejado |
| 002 | MVP0 | Identidade, sessão e e-mail | SPEC-002 | F2 | — | planejado |
| 003 | MVP0 | Organização, tenancy e auditoria | SPEC-003 | F3 | — | planejado |
| 004 | MVP0 | Fazendas | SPEC-004 | F4 | — | planejado |
| 005 | MVP0 | Talhões, GeoJSON e mapa | SPEC-005 | F5 | — | planejado |

Próximo número disponível: `006`. Número reservado nunca é reutilizado. Detalhe histórico vai para `STATUS-ARQUIVO.md`.

## Riscos imediatos

ADR-002 permanece aberta para formalizar monólito modular; portas locais serão definidas uma única vez na execução da F1 conforme `CLAUDE.md`.

Detalhes de itens adiados ou excluídos ficam em `docs/FORA-DE-ESCOPO.md`.
