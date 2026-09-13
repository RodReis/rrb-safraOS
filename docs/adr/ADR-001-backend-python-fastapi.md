# ADR-001 — Backend em Python/FastAPI

**Estado:** aceita
**Data:** 2026-09-13
**Decisor:** PI (Rodrigo Reis)

## Contexto

O projeto precisava fixar a linguagem/framework do backend antes de qualquer fatia executável. A arquitetura histórica (`docs/historico/Arquitetura-2026-09-12.md`) já recomendava Python/FastAPI pelo ecossistema geo/IA (PostGIS, geoprocessamento, pipelines de IA do Módulo B/C do PRD). A memória inicial do projeto registrava Node 24/TypeScript como stack única; o PI confirmou que essa não é a decisão vigente.

## Decisão

Backend em Python com FastAPI. Processamento assíncrono com Celery e Redis no MVP (ver ADR-005). Node 24.x/TypeScript permanece para web (React) e mobile (Expo), nunca para a API.

## Alternativas consideradas

- Node/TypeScript de ponta a ponta (backend e frontend): descartada por ser mais fraca no ecossistema geoespacial (PostGIS/Shapely/GeoPandas) e de IA (pipelines de NLU/transcrição) que os módulos B e C do PRD exigem.

## Consequências

- Dois runtimes no monorepo (Python no backend/worker, Node no web/mobile); CI precisa fixar versão de ambos sem intervalo flutuante (`docs/CI-PR.md`).
- Cliente TypeScript da API é gerado a partir do OpenAPI do FastAPI (`docs/FRONTEND.md` §2–3), não escrito à mão.

## Riscos / reversibilidade

Reversão exigiria reescrever toda a camada de API; alto custo. Mitigado por domínio independente de framework (`docs/ARCHITECTURE.md` §Consistência).

## Evidência

Decisão registrada em `docs/DECISIONS.md`, confirmada pelo PI em 2026-09-13 nesta sessão (Cowork).

## Links

PRD: `docs/prd/PRD.md` (Módulos B/C). Arquitetura: `docs/ARCHITECTURE.md`. Substitui a stack única Node/TS de memória anterior do projeto.
