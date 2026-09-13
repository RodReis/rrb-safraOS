# Registro de decisões arquiteturais

**Revisão:** 2026-09-13. Estados: `proposta`, `aceita`, `substituída`, `rejeitada`. O silêncio não aprova uma decisão.

## Decisões aceitas pelo PI em 2026-09-13

| ADR | Estado | Decisão | Consequência |
|---|---|---|---|
| ADR-001 | aceita | API em Python/FastAPI | Node 24/TypeScript permanece apenas para web/mobile e ferramentas relacionadas. |
| ADR-002 | aceita | Monólito modular | Microserviços com deploy independente exigem medição de carga/falha/autonomia e nova ADR. |
| ADR-003 | aceita | Privacidade em documento autônomo, sem efeito sobre produto | `docs/PRIVACIDADE.md` existe isolado; não referenciado por nenhuma SPEC/PRD/CONVENTION/ARCHITECTURE e não gera controle técnico por conta própria. |
| ADR-005 | aceita | Celery + Redis no MVP | SQS/ECS ou outra fila gerenciada exige medição e nova ADR. |
| ADR-009 | aceita | Web completa primeiro; mobile no final do projeto | MVP0 não cria app Expo nem sincronização offline; PRD emendado para v2.1. |

Arquivo de cada ADR em `docs/adr/ADR-NNN-titulo.md`.

## Decisões abertas

| ADR | Estado | Pergunta | Recomendação técnica, não aprovada |
|---|---|---|---|
| ADR-004 | proposta | SQLite direto ou camada local-first? | Spike com `expo-sqlite`; decidir por perda zero, migração, conflito e observabilidade. |
| ADR-006 | proposta | Meta Cloud API ou BSP? | Comparar custo, templates, webhook, portabilidade, suporte e SLA em piloto. |
| ADR-007 | proposta | Como assinar ICP-Brasil? | Comparar provedor e custódia própria por validade, custo e disponibilidade. |
| ADR-008 | proposta | Qual cloud/região? | O PRD cita residência no Brasil; provedor/custo ainda não foram decididos. |

## Modelo de ADR

Criar `docs/adr/ADR-NNN-titulo.md` com: contexto; decisão; alternativas; consequências; riscos/reversibilidade; evidência; estado/data/decisor; links para PRD, SPEC, issue e ADR substituída. ADR registra o porquê, não replica implementação.
