# Arquivo histórico de status

Append-only: correções ganham nova entrada.

## 2026-09-13 — baseline documental

- Inventariados PRD, backlog, arquitetura histórica, UI e governança.
- Criados contratos documentais faltantes do `CLAUDE.md`.
- Nenhuma SPEC/fatia/issue foi numerada.
- Registrados conflitos de stack e privacidade para o PI.
- Consultadas fontes oficiais de GitHub, NestJS, Expo, PostgreSQL, OWASP, OpenTelemetry e EUDR.

## 2026-09-13 — decisões de stack e privacidade

- PI definiu Python/FastAPI para API e Celery/Redis para processamento assíncrono.
- Node 24/TypeScript permanece em web/mobile.
- Privacidade foi retirada do PRD e isolada em documento autônomo de governança.
- ADR-001, ADR-003 e ADR-005 passaram a `aceita`.

## 2026-09-13 — contrato de frontend

- Criado `docs/FRONTEND.md`: stack de dados/UI (TanStack Query + Table, React Hook Form + Zod, Sonner, Recharts, React Leaflet), padrão de CRUD (Delete = arquivar com confirmação, físico só se a SPEC pedir), grids com paginação server-side, infinite scroll restrito a feeds, skeleton em vez de spinner genérico.
- `CLAUDE.md` passou a referenciar `docs/FRONTEND.md` nas convenções de código e nos documentos-chave.
- Decisão do PI, sem lacuna aberta.

## 2026-09-13 — resolução de incoerências e batch de especificação

Evidência: commit único em `main` (não referenciado por PR — documento é escrito direto pelo Cowork, conforme `CLAUDE.md`).

- **PRD** emendado para v2.1: princípio de offline-first passa a ser meta do produto, não do MVP0; MVP original renomeado para MVP-001; nova seção de escopo do MVP0 referenciando `docs/prd/mvp/MVP-000.md`.
- **Documentos concorrentes** (`docs/prd/BACKLOG.md`, `docs/prd/Arquitetura.md`, brief executivo do design) arquivados em `docs/historico/` com nota de superação; caminhos originais removidos.
- **ADR-002** (monólito modular) aceita pelo PI; deixou de ser decisão aberta.
- **ADR-001, ADR-002, ADR-003, ADR-005, ADR-009** passaram a ter arquivo próprio em `docs/adr/ADR-NNN-titulo.md`.
- **`docs/PRIVACIDADE.md`**: removida do `CLAUDE.md` a cláusula que permitia a ela gerar controle técnico; ADR-003 formaliza que o documento não tem efeito sobre produto.
- **`CLAUDE.md`**: corrigida linha quebrada `next → proximo` (não existe label; virou nota explicativa); removida data fabricada (18/08/2026) da decisão sobre gate de spec; registrado o repositório GitHub; documentada a instalação global de `gstack:*`/`impeccable` na máquina do PI.
- **`docs/DESIGN-UI.md`**: corrigida divergência de paleta — passou a citar azul institucional (já correto em `docs/design-system/TOKENS.md` e nas 24 telas de referência), não mais "verde carbono".
- **SPEC-004**: corrigido erro factual (UF não é código IBGE de duas letras — é a sigla; município passou a usar o código IBGE de 7 dígitos via seed).
- **SPEC-005** e **`docs/prd/mvp/MVP-000.md`**: preenchidas lacunas aprovadas pelo PI — bounding box do Brasil, área com 4 casas decimais, limite de 5 MB por GeoJSON, massa de teste de 500 talhões.
- **`docs/FORA-DE-ESCOPO.md`**: adicionada linha de MFA (dono/contador), adiado para o MVP-001.
- **Issues #1 a #5** criadas no board (`[MVP0][SPEC-NNN][Fn]`), em `proplan:todo`, atribuídas ao PI, na ordem F1→F5.
- **`docs/STATUS.md`**: índice Fatia↔SPEC atualizado com os números reais das issues; ADR-002 saiu de "planejado" (aceita); risco antigo sobre a ADR removido.

Limitações: nenhuma issue de código foi aberta ainda pelo Code; portas locais permanecem indefinidas até a execução da F1.

Entrada futura: data/evento; evidência (issue/PR/SPEC/SHA); limitações; decisão que alterou a ordem.
