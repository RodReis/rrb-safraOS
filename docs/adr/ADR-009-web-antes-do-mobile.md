# ADR-009 — Web completa primeiro; mobile e offline no final do projeto

**Estado:** aceita
**Data:** 2026-09-13
**Decisor:** PI (Rodrigo Reis)

## Contexto

O PRD v2.0 fixava "offline-first ou nada" como princípio 1 e incluía app Android/iOS no escopo do MVP (Q1 2027). Construir mobile e sincronização offline antes de provar domínio, tenancy e API duplicaria interface e risco antes de qualquer coisa estar validada. O PI decidiu inverter a ordem: fundação web primeiro (MVP0), mobile/offline por último.

## Decisão

MVP0 é 100% web. Mobile (Expo) e sincronização offline são adiados para o final do projeto, depois que web e fluxos centrais estiverem estabilizados. O PRD foi emendado (v2.1) para registrar essa inversão: o princípio "offline-first ou nada" permanece meta do *produto* final, não requisito do MVP0.

## Alternativas consideradas

- Mobile/offline dentro do MVP0 ou logo após F5: rejeitada pelo PI nesta sessão — mantém a ordem original (web primeiro).
- Conviver com o PRD v2.0 inalterado e o MVP0 divergente: rejeitada — pela regra do projeto ("onde SPEC/plano divergir do PRD, o PRD vence"), isso deixaria o Code livre para implementar offline-first por conta própria, contradizendo a intenção real.

## Consequências

- `docs/FORA-DE-ESCOPO.md` registra "Aplicativo Expo/mobile" e "Sincronização offline" como adiados, com gatilho "web e fluxos centrais estabilizados; prioridade explícita do PI".
- PRD v2.1 (`docs/prd/PRD.md`) traz nota de versão e princípio 1 reescrito.
- MVP-001 (`docs/prd/mvp/MVP-001.md`) mantém as fatias de campo/offline (Slice 1.3) como parte do produto descrito no PRD, mas a ordem de execução real (mobile "no final do projeto") é a desta ADR, não a ordem de slices do MVP-001.

## Riscos / reversibilidade

Reversível por decisão do PI a qualquer momento — basta reordenar o board. O custo de reversão é baixo porque nenhuma linha de código mobile foi escrita ainda.

## Evidência

Registrada em `docs/DECISIONS.md` desde 2026-09-13; PRD emendado para v2.1 nesta sessão (Cowork), mesma data.

## Links

`docs/prd/PRD.md` (nota de versão 2.1, princípio 1). `docs/prd/mvp/MVP-000.md`. `docs/FORA-DE-ESCOPO.md`.
