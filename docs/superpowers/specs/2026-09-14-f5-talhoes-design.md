# F5 — SPEC-005 — Talhões, GeoJSON e mapa web — Design

**Card:** issue #5 · SPEC-005 · depende de SPEC-004 (mergeada)

## Escopo

Entidade `Talhao`: nome, geometria canônica `MultiPolygon` SRID 4674, área geodésica calculada no backend. Owner desenha no mapa ou importa GeoJSON; lista/mapa mostram só talhões da fazenda/tenant ativo.

## Backend

### Domínio — `packages/backend/src/safraos/talhoes/model.py`

- `@dataclass(frozen=True) Talhao`: `id`, `farm_id`, `organization_id`, `name`, `area_ha: Decimal | None`, `archived_at: datetime | None`.
- `normalize_talhao(name, geometry) -> tuple[str, dict]`: normaliza nome (mesmo padrão de `farms`), valida que `geometry` é dict GeoJSON com `type` em `{"Polygon", "MultiPolygon"}` (rejeita outros tipos aqui — validação de forma). Validação de geometria em si (autointerseção, anéis, vazio, bbox Brasil) é responsabilidade do PostGIS no repository — é I/O, não regra pura.
- `TalhaoError(ValueError)` com `code` (`talhoes.invalid_name`, `talhoes.invalid_geometry_type`).

### Erro HTTP

Mesma convenção de `farms`: `application/problem+json` via `ProblemDetailError`. Códigos novos: `talhoes.invalid_geometry` (PostGIS rejeitou: vazia/autointersectada/anel inválido), `talhoes.out_of_bounds` (fora do bbox do Brasil), `talhoes.payload_too_large` (>5 MB).

### Infra — `apps/api/src/safraos_api/modules/talhoes/`

- `repository.py`: `TalhoesRepository(engine)`, mesmo padrão de `FarmRepository` — `set_config('app.current_user_id', ...)` por transação, auditoria em `audit_events` na mesma transação, um método por caso de uso: `create`, `list` (por `farm_id`), `archive`.
- `create`: `INSERT INTO talhoes (..., geom) VALUES (..., ST_Multi(ST_GeomFromGeoJSON(:geojson)))`. Antes do insert, valida em SQL: `ST_IsValid(geom)` (rejeita autointerseção/anéis inválidos/vazio) e bbox Brasil via `ST_Within(geom, ST_MakeEnvelope(-74.0, -34.0, -32.0, 6.0, 4674))`. Falha em qualquer checagem vira `ProblemDetailError` com o `code` correspondente — nunca deixa o Postgres estourar exceção genérica pro cliente.
- Área: `ST_Area(geography(geom)) / 10000`, arredondado a 4 casas decimais, persistida em `area_ha numeric(12,4)`.
- `router.py`: `APIRouter(prefix="/v1/talhoes")`. Payload JSON (não multipart) tanto pro desenho quanto pro import — o front lê o arquivo `.geojson` no browser e envia a `geometry` extraída no mesmo formato do desenho manual. Tamanho do corpo (5 MB) checado no router via `Content-Length`/leitura do body antes de tocar banco → `talhoes.payload_too_large` (413).

### Migration — `infra/alembic/versions/<data>_0005_talhoes.py`

- `CREATE EXTENSION IF NOT EXISTS postgis` (idempotente; imagem `postgis/postgis:16-3.4` já traz a lib).
- Tabela `talhoes`: `id uuid PK`, `farm_id uuid FK farms(id) ON DELETE CASCADE`, `organization_id uuid FK organizations(id) ON DELETE CASCADE` (denormalizado pra RLS direta, mesmo padrão de `farms.organization_id`), `name text NOT NULL`, `geom geometry(MultiPolygon,4674) NOT NULL`, `area_ha numeric(12,4) NOT NULL`, `archived_at timestamptz NULL`, `created_at timestamptz NOT NULL DEFAULT now()`.
- Índice GiST em `geom`; índice em `organization_id` e `farm_id`.
- RLS `ENABLE` + `FORCE`, policies `SELECT`/`INSERT`/`UPDATE` escopadas por membership da organização — mesma forma das policies de `farms` (`EXISTS (... organization_memberships ...)`).
- `GRANT SELECT, INSERT, UPDATE ON talhoes TO safraos_app`.

## Frontend

Estrutura: `apps/web/src/features/talhoes/{api,components,hooks,schemas,routes}` (FRONTEND.md §7).

- **MapAdapter** (`apps/web/src/components/map/MapAdapter.tsx`, novo): encapsula React-Leaflet + Leaflet-Geoman Free. Feature `talhoes` nunca importa Leaflet/Geoman diretamente (FRONTEND.md §2). Expõe props: geometrias existentes pra exibir, callback `onDraw(geojson)`, controle de tenant ativo (remonta ao trocar — nunca mantém objeto de tenant anterior).
- **Desenho**: Geoman desenha polígono no mapa, gera GeoJSON no browser. Prévia mostra o polígono; valor de área do cliente é só ilustrativo, nunca enviado nem confiado — a área exibida como "oficial" vem da resposta do backend após salvar.
- **Import**: `<input type="file" accept=".geojson,application/geo+json">`, `FileReader` no browser valida tamanho (>5 MB rejeita antes de ler) e faz `JSON.parse`, extrai `geometry` da Feature/FeatureCollection (primeira feature; múltiplas features fora de escopo desta fatia — cada import é um talhão), mesma forma de payload do desenho.
- **Cliente OpenAPI + TanStack Query**: mesma infra de `farms` (`$api.useQuery`/`useMutation`), key inclui `organization_id`/`farm_id` — troca de tenant invalida a query, mapa remonta sem objetos do tenant anterior.
- **Lista**: `DataTable` com nome, área (ha, `tabular-nums`), ação arquivar via `ConfirmDialog`.
- **Formulário**: RHF + Zod, schema deriva do tipo OpenAPI gerado; campo nome com máscara/validação; erro do backend mapeado por `code` pra mensagem PT-BR.

## Testes

- `tests/rules/talhoes/test_talhao_model.py` — domínio puro (nome, tipo de geometria).
- `tests/rules/api/test_talhoes_router.py` — router com repository fake, erro problem+json, payload >5 MB.
- `tests/database/test_talhoes_migration.py` — RLS cross-tenant, geometria autointersectada rejeitada, fora do bbox Brasil rejeitada, área geodésica calculada corretamente para caso conhecido, `Polygon` normalizado pra `MultiPolygon`.
- Frontend: componente (loading/empty/error/success), formulário (validação Zod, preservação de dados em erro), import (arquivo válido/inválido/>5MB).
- `tests/e2e/talhoes.spec.ts`: desenho e import do mesmo polígono produzem geometria equivalente; dois tenants sem vazamento no mapa/lista; screenshot.
- Performance: massa de 500 talhões numa fazenda, medição registrada na PR (decisão do PI 2026-09-13) — sem meta numérica inventada além do que consta no PRD.

## Fora de escopo desta fatia

- KML e Shapefile (mock visual mostra, SPEC-005 restringe a GeoJSON) — não implementado.
- Múltiplos talhões por arquivo importado (FeatureCollection com N features) — cada import é 1 talhão nesta fatia.
- Integração com máquinas (John Deere/Trimble) mostrada no mock visual — não é requisito da SPEC-005.
