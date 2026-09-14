# Medição de desempenho — 500 talhões (F5)

**Data:** 2026-09-14
**Massa:** 500 talhões numa única fazenda (`Fazenda Perf <timestamp>`, UF GO), organização dedicada de teste (`Perf Talhoes <timestamp>`). Polígonos pequenos (~0,05° x 0,05° de lado, mesmo padrão de `tests/e2e/talhoes.spec.ts`), deslocados incrementalmente em 0,001° de longitude a cada talhão, todos dentro do bbox -49.0 a -48.5 / -16.5 a -16.0.

**Ambiente:** app local via `npm run dev` (docker compose: Postgres/Redis/Mailpit) + `uv run python -m safraos_api` (API) + `npm run dev --workspace apps/web` (web), mesmos comandos usados pelo `webServer` do Playwright (`playwright.config.ts`). Sem dados pré-existentes na fazenda de teste.

## Resultados

- **Criação dos 500 talhões** (`POST /v1/talhoes`, sequencial via HTTP direto): 500/500 sucesso, 0 falha, **24.444 ms no total** (~48,9 ms/talhão). Não é o critério medido pela task — registrado só como contexto de geração de massa.
- **Tempo de resposta `GET /v1/talhoes?farmId=<id>`** com os 500 registros: **73 ms**.
- **Tempo até a `TalhoesPage` renderizar todos os polígonos no mapa** (navegação até a página + resposta do `GET /v1/talhoes` + os 500 `<path>` do Leaflet aparecerem no DOM, medido via Playwright/`page.waitForFunction`): **541 ms**.
- **Observações:** sem gargalo perceptível. A resposta da API (73 ms) é uma fração pequena do tempo total de renderização (541 ms) — a maior parte do tempo é navegação/render do React + Leaflet, não a consulta ao banco. Lista (tabela) e mapa carregaram juntos sem travamento visível; screenshot full-page confirma as 500 linhas na tabela renderizadas.

## Método

Script ad-hoc descartável (Node, `fetch` puro para criação de massa; Playwright para medição de mapa) que:
1. Registrou um usuário de teste via `POST /v1/auth/register`, confirmou e-mail lendo o Mailpit (`GET /api/v1/messages` + `/api/v1/message/:id`), autenticou via `POST /v1/auth/login`.
2. Criou organização (`POST /v1/organizations`), ativou como tenant (`POST /v1/organizations/active`), criou uma fazenda (`POST /v1/farms`).
3. Disparou 500 `POST /v1/talhoes` sequenciais com polígonos válidos e não sobrepostos.
4. Mediu `GET /v1/talhoes?farmId=<id>` com `Date.now()` antes/depois da resposta.
5. Abriu a `TalhoesPage` real num browser Chromium (Playwright), logou pela UI, selecionou a organização de teste, navegou para `/fazendas/<id>/talhoes` e mediu o tempo até `document.querySelectorAll('.leaflet-overlay-pane path').length >= 500`.

O script não foi commitado (ferramenta de medição descartável, sem convenção de `scripts/` de seed ad-hoc no projeto — `scripts/` do repo é reservado a build/dev/lint/typecheck/test, conforme `package.json` e `docs/DEVELOPMENT.md`).

## Limpeza dos dados de teste

- Os **500 talhões** e a **fazenda de teste** foram removidos do banco de desenvolvimento (`DELETE FROM talhoes ...`, `DELETE FROM farms ...`), confirmado por contagem zero após a limpeza.
- A **organização de teste**, o **vínculo de membership** e o **usuário de teste** (`identity_users`) **não** foram removidos: `audit_events` é append-only (trigger `forbid_audit_event_mutation`) e referencia a organização por FK, então apagar a organização exigiria violar esse invariante — o que não é uma decisão livre do agente. Ficaram no banco local de desenvolvimento:
  - Organização: `Perf Talhoes <timestamp>` (id `441ddf4a-48ea-41a8-9568-0db2d70d58fb`)
  - Usuário: `perf-talhoes-<timestamp>@example.com` (id `addfd03f-9bfd-4ac9-a75b-580ac6584a3b`)
  - Isso é o mesmo resíduo que qualquer execução de `tests/e2e/talhoes.spec.ts` já deixa no ambiente de dev (usuários/organizações de teste acumulam ali por causa do append-only). Não polui produção; é limpável manualmente com `docker compose down -v` do stack `safraos-*` caso o ambiente de dev precise ser resetado.

## Conclusão

Sem meta numérica definida pela SPEC (decisão do PI, 2026-09-13) — apenas registro da medição. Os números observados (73 ms na API, 541 ms até o mapa renderizar 500 polígonos) não indicam gargalo que justifique um `[FIX]` nesta fatia.
