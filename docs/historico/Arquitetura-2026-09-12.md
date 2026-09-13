> **Superado em 2026-09-13.** Esta arquitetura (v1.0) propunha quatro serviços de domínio com deploy independente, Kubernetes/EKS, Terraform e AWS São Paulo desde o MVP — decisão nunca aceita pelo PI e substituída pelo monólito modular de `docs/ARCHITECTURE.md` (ADR-002, aceita em 2026-09-13). Mantido apenas como referência histórica das opções consideradas; **não é contrato**. A arquitetura vigente é `docs/ARCHITECTURE.md`.

---

# SafraOS — Documento de Arquitetura Técnica
**Versão 1.0 · 12/09/2026 · Escopo: MVP (Q1 2027) → V2 (2028)**

---

## 1. Princípios arquiteturais
1. **Offline-first ou nada** — o registro de campo é a fonte da verdade; o backend aceita sync assíncrono com conflitos por campo (last-write-wins + log). Nenhuma funcionalidade de campo exige rede.
2. **Lançamentos imutáveis** — todo `Lancamento` é append-only com hash encadeado (SHA-256 do payload + hash anterior). Isso sustenta a trilha de evidências do compliance (auditoria de "o que mudou, quando, quem") e o argumento anti-fraude para exportadores.
3. **Compliance como pipeline de dados** — verificação CAR é um job diário (ingest → cruzamento → semáforo → alerta), não uma consulta sob demanda. Eventos são dados de primeira classe.
4. **CQRS leve** — escrita (sync app/WhatsApp) e leitura (dashboards, relatórios) separadas por projeções assíncronas; dashboard p95 < 2 s vem de projeções, não de joins pesados.
5. **Segurança por padrão** — isolamento por tenant, privilégio mínimo, criptografia de dados sensíveis e trilha de auditoria.

---

## 2. Stack recomendado

| Camada | Escolha | Por quê |
|---|---|---|
| App de campo | React Native + SQLite (WatermelonDB) | Um codebase Android/iOS; sync incremental por campo; SQLite maduro offline |
| Web | React + TypeScript | Mercado de talentos; BFF dedicado |
| API | Python (FastAPI) | Ecossistema geo/IA forte, times-to-market |
| Serviços de IA | Pipeline próprio: Whisper (transcrição) + LLM Pt-BR fine-tunado com few-shot de vocabulário rural + regras de validação | Controle de confiança e fallback humano; custo previsível vs. API pura |
| Banco transacional | PostgreSQL 16 + PostGIS 3.4 | Tipos geoespaciais nativos (polígono, ST_Intersects, ST_Area) — coração do cruzamento CAR |
| Fila/jobs | Celery + Redis (MVP) → SQS + ECS (escala) | Reprocessamento por job, DLQ, retry |
| Object storage | S3-compatível (região Brasil) | XMLs de NF-e, evidências EUDR, snapshots mensais de shapes |
| Geodados | PostGIS + arquivamento shapefile versionado + pg_tileserv (mapas) | Versionamento mensal permite rollback e auditoria histórica |
| Infra | Kubernetes (EKS) + Terraform, região AWS São Paulo | IaC e autoscaling |
| Observabilidade | OpenTelemetry + Grafana + Loki/Sentry | SLA de verificação ≥99% em <24 h exige rastreabilidade de pipeline |
| CI/CD | GitHub Actions (testes, migrations, deploy canary) | Migrations com expand/contract (zero downtime) |

---

## 3. Topologia de serviços
Quatro serviços de domínio (monorepo, deploys independentes):

- **Serviço Financeiro** — plano de contas, rateio de indiretos, DRE/GND/LCDPR, integração contábil.
- **Serviço de Campo + IA** — endpoint do WhatsApp Cloud API, pipeline NLU (transcrever → extrair entidades → cartão de confirmação), sync engine do app (recebimento de operações, resolução de conflito, georreferência).
- **Serviço de Compliance** — consumo de eventos do pipeline geodados, semáforo por fazenda, compilação de evidências por lote, geração de due diligence EUDR, PDF assinado (ICP-Brasil) + portal de validação pública (hash → status, sem login).
- **Serviço de Integrações** — SEFAZ (distDFe de entrada, emissão NF-e/MDF-e), sistema contábil, OpenAPI pública v1 (`POST /verificacao/eudr`, `GET /compliance/{id}/status`, webhooks).

**API Gateway/BFF** centraliza auth (JWT/OAuth2, MFA para dono e contador), rate limit (600 req/min/tenant), WAF.

---

## 4. Fluxo de dados dos casos críticos

### F2 — Lançamento de campo (<20 s)
```
App offline: lançamento + GPS → fila local SQLite
  → sync (quando há rede): pacote de operações com timestamp local
  → Serviço de Campo: valida, resolve conflito por campo (last-write-wins + log)
  → grava Lancamento (append-only, hash encadeado) no PostgreSQL
  → evento "lançamento.confirmado" → fila
    → Serviço Financeiro: recalcula custo do talhão (projeção do ranking de margem)
    → (se insumo) atualiza estoque
```
WhatsApp segue o mesmo caminho, mas entra via Cloud API → pipeline NLU (confiança ≥0,75 confirma sozinho; abaixo disso, fallback humano em <2 h úteis).

### F4 — Alerta de compliance (<24 h, diário)
```
00:00–02:00 (agendado): jobs de ingestão
  SICAR (por UF) + Prodes/DETER (INPE) + embargos (IBAMA/UF) + UC/APP
  → normalização para GeoJSON/PostGIS → snapshot versionado no S3
  → cruzamento espacial: ST_Intersects(CAR, risco)
    flags: desmatamento pós-2020 · embargo · área inconsistente >5%
  → atualiza VerificacaoCompliance (append-only)
  → recalcula semáforo da fazenda
  → novo evento crítico? → WhatsApp/e-mail ao dono com polígono + área + recomendação
```
Ressiliência: DLQ + reprocessamento manual por job (E5-US1); se uma UF falhar, o restante do pipeline segue e a UF é reprocessada (transparência de cobertura no relatório).

### F3 — Venda a exportador (momento mágico)
```
NF-e de saída autorizada (SEFAZ) → evento
  → Serviço de Compliance identifica destinatário exportador/cooperativa
  → sugere geração da due diligence
  → compila evidências do lote (polígonos + histórico + NF-e + GTA) → hash único
  → PDF PT/EN assinado ICP-Brasil + QR → portal de validação pública
```

---

## 5. Modelo de dados espaciais e auditoria
- `talhao.geom (geometry POLYGON, SRID 4674 — SIRGAS 2000)`; índice GIST.
- Cada `VerificacaoCompliance` guarda o polígono do evento + versão do snapshot de dados usada (reprodutibilidade: "com esses dados, naquela data, esse era o resultado").
- `Lancamento` append-only: `hash = sha256(payload | prev_hash | tenant_id)` — verificação de cadeia em qualquer auditoria.
- Evidências da `DueDiligence` imutáveis; novo fato → nova versão com diff.

## 6. Segurança
MFA (dono/contador) · certificado A1 criptografado no KMS · TLS 1.3 · AES-256 em repouso · chaves por tenant (envelope) · trilha de auditoria append-only · pentest anual · exportação completa self-serve (anti-lock-in).

## 7. Escalabilidade (metas do plano)
| Marco | Fazendas | He usados | Ajuste de arquitetura |
|---|---|---|---|
| MVP (2027) | 360 | ~0,5 mi | 1 cluster pequeno, jobs em horário noturno |
| V2 (2028) | 1.260 | ~2 mi | SQS + workers horizontais; read replicas p/ dashboard |
| V3 (2029) | 2.700 | ~5 mi | Particionamento de Lancamento por safra; tile server próprio |
| V4 (2030) | 5.400 + LATAM | ~10 mi | Multi-region BR; fila de geodados em streaming (DETER) |

## 8. Decisões pendentes (ADRs a escrever na S1)
1. Event bus: Redis Streams (MVP) vs. Kafka (V2) — decisão na S2 com spike.
2. Assinatura ICP-Brasil: serviço próprio (AC) vs. API de terceiros (DocuSign BR/Vaultinum) — critério: custo por relatório × exigência do importador.
3. WhatsApp: Cloud API direta (Meta) vs. BSP (Twilio/360dialog) — critério: custo por conversa + suporte a templates em Pt-BR rural.
