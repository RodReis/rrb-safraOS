# MVP0 Fundação Web Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar localmente o fluxo web autenticado organização → fazenda → talhão, com isolamento de tenant, PostGIS, Celery/Redis/Mailpit e CI rastreável.

**Architecture:** Monólito modular FastAPI com domínio independente do transporte e persistência PostgreSQL/PostGIS protegida por autorização e RLS. React oferece a interface web; transactional outbox alimenta tarefas Celery idempotentes. Cada SPEC gera uma PR independente e software executável.

**Tech Stack:** Python/FastAPI, SQLAlchemy/Alembic, PostgreSQL 16/PostGIS, Celery/Redis, React 19/TypeScript, Vite, shadcn/ui, React Leaflet, Leaflet-Geoman Free, Playwright, pytest e GitHub Actions.

---

## Mapa de arquivos

```text
package.json                         contratos públicos npm
compose.yaml                         serviços locais exclusivos
.env.example                         portas/variáveis após pergunta única ao PI
apps/api/src/safraos_api/main.py     composição FastAPI
apps/api/src/safraos_api/modules/    routers/adapters por domínio
apps/worker/src/safraos_worker/      Celery e tarefas
apps/web/src/                        React, rotas e telas
packages/backend/src/safraos/        domínio, casos de uso e portas
packages/frontend/src/               tokens/componentes compartilhados
infra/docker/                        Dockerfiles e configuração
scripts/                             wrappers portáveis
tests/e2e/                           fluxos Playwright
.github/workflows/ci.yml             jobs e gate
```

## F1 — SPEC-001: fundação executável

### Task 1: Contratos raiz e ambiente

**Files:** Create `package.json`, `.env.example`, `compose.yaml`, `scripts/dev.mjs`, `scripts/stop.mjs`; modify `README.md`.

- [ ] Escrever teste de contrato que carrega `package.json` e exige scripts `dev`, `stop`, `build`, `lint`, `typecheck`, `test`, `test:e2e`.
- [ ] Executar `npm test -- --runInBand` e confirmar falha por scripts ausentes.
- [ ] Criar os scripts raiz; wrappers usam `spawn` com argumentos em array e resolvem `.cmd` no Windows.
- [ ] Perguntar uma única vez as portas ao PI antes de preencher `.env.example`; validar que não colidem com containers existentes.
- [ ] Definir Compose com nomes/volumes do SafraOS e health checks de Postgres, Redis e Mailpit.
- [ ] Executar `npm run dev`; esperar todos os health checks; executar `npm run stop` e confirmar que containers alheios permanecem.
- [ ] Commit: `chore(fundacao): configure ambiente local do SafraOS`.

### Task 2: API, worker e web mínimos

**Files:** Create `pyproject.toml`, `uv.lock`, `apps/api/**`, `apps/worker/**`, `apps/web/**`, `infra/docker/**`.

- [ ] Criar teste FastAPI para `/health/live`, `/health/ready` e `correlationId`; esperado inicial: import falha.
- [ ] Implementar `APIRouter` de health e middleware de correlação; readiness consulta banco e Redis.
- [ ] Criar teste Celery que envia `smoke.ping` e exige resultado com o mesmo `correlationId`.
- [ ] Implementar tarefa idempotente `smoke.ping` sem efeito externo.
- [ ] Criar teste de componente web para estados loading, saudável e indisponível.
- [ ] Implementar shell React e cliente tipado do health.
- [ ] Rodar `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`; esperado: todos PASS.
- [ ] Commit: `feat(fundacao): integre api worker e web`.

### Task 3: CI e E2E de smoke

**Files:** Create `.github/workflows/ci.yml`, `tests/e2e/health.spec.ts`, `playwright.config.ts`; modify `docs/TESTING.md` se o comando final divergir.

- [ ] Escrever E2E que abre a web e encontra status saudável da API.
- [ ] Executar `npm run test:e2e`; confirmar falha antes do servidor orquestrado.
- [ ] Configurar Playwright para iniciar o contrato `npm run dev` e encerrar pelo projeto.
- [ ] Criar jobs `quality`, `test-regras`, `test-banco`, `test-tela`, `e2e`, agregador e `gate` com `if: always()`.
- [ ] Publicar JSON/coverage como artefato; agregador não reexecuta testes.
- [ ] Rodar todos os comandos raiz e validar workflow por parser/linter disponível.
- [ ] Commit: `ci(fundacao): valide o fluxo mínimo do MVP0`.

## F2 — SPEC-002: identidade, sessão e e-mail

### Task 4: Modelo e regras de identidade

**Files:** Create `packages/backend/src/safraos/identity/**`, migration Alembic, `tests/rules/identity/**`, `tests/database/test_identity_migration.py`.

- [ ] Testar e-mail normalizado/único, Argon2id, token hash/expiração/uso único e estados de usuário.
- [ ] Rodar testes e confirmar falha por domínio ausente.
- [ ] Implementar entidades/serviços puros e portas de relógio, token e hash.
- [ ] Criar migration de users, sessions e tokens com constraints.
- [ ] Testar migration forward em banco vazio e restrições reais.
- [ ] Commit: `feat(identidade): modele usuario sessao e tokens`.

### Task 5: Cadastro, confirmação e recuperação assíncrona

**Files:** Create `apps/api/src/safraos_api/modules/identity/**`, `apps/worker/src/safraos_worker/tasks/email.py`, templates de e-mail, testes de integração.

- [ ] Escrever testes de cadastro/outbox, resposta neutra, confirmação sem login automático e reset com revogação.
- [ ] Escrever teste de reentrega da mesma tarefa e falha SMTP transitória com retry limitado.
- [ ] Implementar endpoints, transactional outbox, dispatcher Celery e adapter Mailpit.
- [ ] Implementar cookie de sessão, CSRF, rotação e logout.
- [ ] Rodar integração real via Docker; inspecionar Mailpit por API no teste, sem validação manual.
- [ ] Commit: `feat(identidade): entregue autenticacao e email assincrono`.

### Task 6: Telas de autenticação

**Files:** Create `apps/web/src/features/auth/**`, rotas e testes; modify shell web.

- [ ] Testar estados e mensagens de cadastro, confirmação, login, logout, esqueci/redefinir senha.
- [ ] Implementar formulários controlados, cliente com cookie e token CSRF.
- [ ] Testar que erro recuperável preserva campos permitidos e nunca repõe senha.
- [ ] Criar E2E completo de identidade com Mailpit.
- [ ] Rodar qualidade, tela, segurança e E2E.
- [ ] Commit: `feat(web): entregue jornada de autenticacao`.

## F3 — SPEC-003: organização, tenancy e auditoria

### Task 7: Domínio, banco e RLS

**Files:** Create `packages/backend/src/safraos/organizations/**`, migration, policies RLS, testes de regras/banco.

- [ ] Testar organização, membership única e papel `owner`.
- [ ] Criar migration com `organization`, `membership`, `audit_event`; habilitar e forçar RLS.
- [ ] Criar role de aplicação sem owner/BYPASSRLS e helper transacional de contexto.
- [ ] Testar default deny e acesso cruzado usando a role real da aplicação.
- [ ] Implementar casos de uso e auditoria append-only.
- [ ] Commit: `feat(tenancy): isole organizacoes com rls e auditoria`.

### Task 8: API e web de organizações

**Files:** Create módulos API/web de organização, seleção de tenant e testes E2E.

- [ ] Testar criar/listar/selecionar somente memberships autorizadas.
- [ ] Implementar dependências FastAPI para sessão, tenant ativo e autorização do objeto.
- [ ] Implementar seletor web; troca limpa cache/seleção do tenant anterior.
- [ ] Executar E2E com dois usuários e IDs trocados; respostas não revelam existência.
- [ ] Commit: `feat(organizacoes): entregue contexto seguro de tenant`.

## F4 — SPEC-004: fazendas

### Task 9: Fazenda ponta a ponta

**Files:** Create domínio/API/web `farms`, migration e testes.

- [ ] Testar nome obrigatório, UF, município/IBGE, arquivamento e ausência de unicidade presumida.
- [ ] Criar migration com `organization_id` e RLS; testar tenant cruzado.
- [ ] Implementar casos de uso, router e auditoria.
- [ ] Implementar lista/formulário com loading, vazio, erro, sucesso e arquivadas.
- [ ] Criar E2E de CRUD/arquivamento por teclado e dois tenants.
- [ ] Rodar suíte e commit: `feat(fazendas): entregue cadastro por tenant`.

## F5 — SPEC-005: talhões, GeoJSON e mapa

### Task 10: Geometria e persistência

**Files:** Create domínio `fields`, parser GeoJSON, migration PostGIS e testes geoespaciais.

- [ ] Escrever fixtures para Polygon válido, MultiPolygon, vazio, autointerseção, anel inválido, tipo indevido e coordenada fora do limite.
- [ ] Testar normalização para MultiPolygon 4674 e área geodésica com tolerância documentada.
- [ ] Implementar parser/validador sem confiar em `area_ha` do cliente.
- [ ] Criar migration, GiST, RLS e constraints de vínculo fazenda/tenant.
- [ ] Testar endpoints e banco contra acesso cruzado.
- [ ] Commit: `feat(talhoes): valide geometria e area no backend`.

### Task 11: Mapa, desenho e importação

**Files:** Create `apps/web/src/features/fields/**`, adapter de mapa, upload GeoJSON e testes.

- [ ] Instalar React Leaflet e Leaflet-Geoman Free com versões registradas no lockfile; documentar suas licenças permissivas no inventário de dependências.
- [ ] Escrever testes de adapter para desenhar, importar, limpar e serializar geometria.
- [ ] Implementar mapa encapsulado; feature não depende diretamente da biblioteca escolhida.
- [ ] Implementar importação com limite/tipo, prévia e erro acionável.
- [ ] Testar troca de fazenda/tenant limpa layers e requisições anteriores.
- [ ] Criar E2E para desenho e importação equivalentes.
- [ ] Commit: `feat(web): entregue mapa e cadastro de talhoes`.

### Task 12: Gate e documentação do MVP0

**Files:** Modify `README.md`, `docs/DEVELOPMENT.md`, `docs/STATUS.md`, `docs/STATUS-ARQUIVO.md`; create evidências exigidas por `docs/TESTING.md`.

- [ ] Executar instalação limpa e todos os comandos públicos.
- [ ] Executar E2E completo com dois tenants e capturar evidência visual desktop.
- [ ] Confirmar JSONs de regras, banco, tela, segurança e E2E no SHA atual.
- [ ] Revisar diff completo conforme `docs/REVIEW.md`; corrigir P0/P1 e revalidar.
- [ ] Registrar limites reais; não promover `not_run` a PASS.
- [ ] Criar card `[MVP0][GATE]` somente quando as cinco fatias estiverem integradas; gate não recebe SPEC/F.
- [ ] Commit: `docs(mvp0): registre evidencias de homologacao`.

## Ordem e paralelismo

F1 → F2 → F3 → F4 → F5 → Gate. Dentro de cada fatia, domínio/testes podem avançar em paralelo com componentes visuais somente depois de os contratos estarem fixados. F4 e F5 não começam antes de RLS/tenant da F3; isso impediria testes falsamente seguros.

## Verificação final do plano

- SPEC-001: Tasks 1–3.
- SPEC-002: Tasks 4–6.
- SPEC-003: Tasks 7–8.
- SPEC-004: Task 9.
- SPEC-005: Tasks 10–11.
- Gate do MVP0: Task 12.
