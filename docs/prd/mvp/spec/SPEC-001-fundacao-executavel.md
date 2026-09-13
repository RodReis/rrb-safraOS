# SPEC-001 — Fundação executável e CI

**MVP:** MVP0
**Fatia:** F1
**Estado:** pronta
**Decisão do PI:** 2026-09-13

## Resultado

Uma instalação limpa sobe web, API, worker, PostgreSQL/PostGIS, Redis e Mailpit com um comando público, expõe health checks reais e executa o mesmo contrato de qualidade na máquina Windows do PI e na CI.

## Dentro

- monorepo com `apps/api`, `apps/web`, `apps/worker` e contratos raiz;
- Python/FastAPI, React/TypeScript, Celery/Redis, PostgreSQL/PostGIS e Mailpit;
- Docker Compose exclusivo do SafraOS, volumes e health checks;
- comandos `dev`, `stop`, `build`, `lint`, `typecheck`, `test` e `test:e2e`;
- correlação HTTP, resposta `application/problem+json` e smoke E2E;
- CI paralela com gate único e artefatos por categoria.

## Fora

Autenticação, modelo de tenant, fazendas e talhões. Nenhum serviço vazio deve fingir prova funcional: o worker executa uma tarefa de smoke observável.

## Contratos

- `GET /health/live`: processo responde.
- `GET /health/ready`: banco e Redis disponíveis; falha retorna status não saudável.
- Web exibe estado saudável/indisponível da API sem esconder erro.
- `correlationId` recebido ou gerado aparece na resposta e nos logs estruturados.

## Critérios de aceite

- checkout limpo executa `npm run dev` e todos os serviços ficam saudáveis;
- `npm run stop` encerra somente recursos do SafraOS;
- PostGIS responde a consulta de extensão instalada;
- tarefa Celery de smoke é processada uma vez e rastreada;
- lint, typecheck, testes, build e E2E passam localmente e no SHA atual da CI;
- falha deliberada de banco derruba readiness, não liveness;
- nenhum segredo ou porta real fica hardcoded fora de `.env.example`.
