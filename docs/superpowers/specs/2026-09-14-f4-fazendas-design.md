# F4 — SPEC-004 — Cadastro web de fazendas — Design

**Card:** issue #4 · SPEC-004 · depende de SPEC-003 (mergeada)
**Decisão do PI (2026-09-14):** seguir `docs/FRONTEND.md` à risca, mesmo divergindo do padrão simplificado usado em F3 (organizations). F3 não é retrofitada nesta fatia.

## Escopo

Entidade `Farm` (fazenda): nome, UF (sigla 2 letras, lista fixa 27), município (código IBGE 7 dígitos, seed próprio). CRUD + arquivamento, tenant-scoped via `organization_id`, auditado.

## Backend

### Domínio — `packages/backend/src/safraos/farms/model.py`

- `@dataclass(frozen=True) Farm`: `id`, `organization_id`, `name`, `uf`, `municipio_ibge_code`, `archived_at: datetime | None`.
- `create_farm(name, uf, municipio_ibge_code) -> Farm`: normaliza nome (mesmo padrão de `organizations`), valida UF contra lista fixa das 27 siglas, valida formato do código IBGE (7 dígitos numéricos). Existência do código na tabela `municipios` **não** é validada aqui (I/O) — repository confere via FK/join.
- `FarmError(ValueError)` com `code` (`farms.invalid_name`, `farms.invalid_uf`, `farms.invalid_municipio`).

### Erro HTTP — `application/problem+json`

Handler de exceção global em `apps/api/src/safraos_api/main.py` (`@app.exception_handler(DomainError)` — classe base que `FarmError`/`OrganizationError` podem herdar, ou handler dedicado só pra `FarmError` se subir a base for risco pra F3). Resposta: `{type, title, status, code, correlationId}`. **Só as rotas novas de farms usam esse formato** — `organizations` mantém `MessageResponse` como está, sem tocar.

### Infra — `apps/api/src/safraos_api/modules/farms/`

- `repository.py`: `FarmRepository(engine)`, mesmo padrão de `OrganizationRepository` — `set_config('app.current_user_id', ...)` por transação, um método por caso de uso (`create`, `list`, `get`, `update`, `archive`), auditoria em `audit_events` na mesma transação.
- `router.py`: `APIRouter(prefix="/v1/farms")`, autorização de sessão manual (igual F3), erros via `problem+json`.

### Migration — `infra/alembic/versions/<data>_0004_farms.py`

- Tabela `municipios`: `ibge_code char(7) PRIMARY KEY`, `name`, `uf`. Sem RLS (dado de referência). `GRANT SELECT` pra `safraos_app`. Seed via `op.execute(INSERT ... ON CONFLICT DO NOTHING)` — lista de municípios de UFs de interesse do agro (GO/MT/MS no mínimo, conforme exemplos da SPEC); volume completo de 5570 municípios fica a critério da implementação, mas nenhum hardcode fora da migration.
- Tabela `farms`: `id uuid PK`, `organization_id FK`, `name`, `uf`, `municipio_ibge_code FK municipios`, `archived_at timestamptz NULL`, `created_at`. RLS `ENABLE` + `FORCE`, policies `SELECT`/`INSERT`/`UPDATE` (arquivar = update) escopadas por membership da organização, igual padrão de `organizations`.

## Frontend

Infra nova (usada só por farms nesta fatia, disponível pra próximas):

- **Cliente OpenAPI**: trio `openapi-typescript` + `openapi-fetch` + `openapi-react-query` (pacotes MIT, sem serviço externo, geração 100% local — pesquisa de mercado registrada no PR). `openapi-typescript` gera `apps/web/src/lib/api-types.ts` (`paths`/`components`) a partir do schema exposto pela API (`/openapi.json`). Script `scripts/generate-openapi.mjs`, chamado em `npm run typecheck` (anti-drift: CI falha se gerado divergir do commitado). `openapi-fetch` (~6 kB, zero-overhead) cria o cliente fetch tipado pelos tipos gerados — não SDK completo. `openapi-react-query` envolve esse cliente e expõe `$api.useQuery(...)`/`$api.useMutation(...)` com type-safety ponta a ponta (path, params, body, response, erro), substituindo a necessidade de escrever wrappers manuais sobre TanStack Query.
- **TanStack Query**: `QueryClientProvider` no shell (`apps/web/src/App.tsx`). Toda leitura de farms via `$api.useQuery`, mutações via `$api.useMutation` + invalidação (ver acima).
- **TanStack Table + DataTable**: componente genérico `packages/frontend/src/components/DataTable.tsx`, reaproveitável por outras entidades depois. Paginação/ordenação/filtro: client-side nesta fatia (massa pequena, municípios/fazendas por tenant não justificam server-side ainda) — registrado como decisão consciente na PR.
- **RHF + Zod**: formulário de criar/editar fazenda, schema deriva do tipo gerado da API.
- **Sonner**: toast de sucesso/erro nas mutações.

Estrutura: `apps/web/src/features/farms/{api,components,hooks,schemas,routes}` conforme `docs/FRONTEND.md` §7.

## Testes

- `tests/rules/farms/test_farm_model.py` — domínio puro.
- `tests/rules/api/test_farms_router.py` — router com repository fake, erro problem+json, 401/404 tenant cruzado.
- `tests/database/test_farms_migration.py` — RLS cross-tenant, seed de municípios acessível, FK UF↔município rejeitada quando inválida.
- Frontend: testes de componente (loading/empty/error/success), formulário (validação Zod, preservação de dados em erro), tabela (ordenação/filtro refletidos na URL conforme §11).
- `tests/e2e/farms.spec.ts`: dois tenants, CRUD+arquivamento por teclado, screenshot.

## Fora de escopo desta fatia

- Retrofit de F3 (organizations) pro novo padrão de frontend — não pedido, não decidido pelo PI.
- Volume completo dos ~5570 municípios do IBGE no seed — entra o necessário pros testes/UFs de exemplo da SPEC; ampliar depois é reversível.
