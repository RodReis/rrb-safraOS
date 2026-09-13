# Arquitetura do SafraOS

**Estado:** baseline de construção, sujeito às decisões em `DECISIONS.md`
**Fontes:** `docs/prd/PRD.md`, `CLAUDE.md` e ADRs aceitos
**Revisão:** 2026-09-13

## Precedência e conflito conhecido

O PRD define produto; SPEC define a fatia; ADR aceita define estrutura. Este documento não cria regra de produto. A arquitetura histórica em `docs/prd/Arquitetura.md` e o `CLAUDE.md` convergem em Python/FastAPI para API e Celery/Redis para processamento assíncrono. React/TypeScript e Expo continuam nas interfaces.

## Forma inicial

Começar como **monólito modular**, com workers separáveis. Microserviços no primeiro dia aumentariam deploy, observabilidade e consistência distribuída sem carga comprovada.

```text
Web React ─┐
App Expo ──┼─> API FastAPI ─> módulos Python ─> PostgreSQL/PostGIS
WhatsApp ──┘          │             │
Integrações externas ─┘             └─> outbox ─> Celery/Redis ─> workers
                                              └─> object storage
```

Módulos: identidade/tenancy; fazendas/talhões/safras; campo/sync; financeiro/fiscal; compliance/geodados; integrações/notificações; relatórios/auditoria. Fronteira de módulo não autoriza deploy independente; extração exige medição e ADR.

## Persistência e tenancy

- PostgreSQL 16 + PostGIS 3.4; geometrias canônicas em SIRGAS 2000 (SRID 4674) e índice GiST.
- Toda tabela de cliente tem `tenant_id` não nulo, FK e índice.
- RLS habilitada e forçada; sem política aplicável, negar. Tráfego normal não usa owner nem `BYPASSRLS`.
- A transação fixa o tenant; o caso de uso também autoriza o objeto. RLS é defesa em profundidade.
- Dinheiro usa inteiro na menor unidade ou `numeric` com escala; nunca `float`. Instantes técnicos em UTC.

## Consistência e assíncrono

- Caso de uso controla a transação; controller valida e delega.
- Estado e evento saem pela mesma transação usando transactional outbox.
- Consumidor é idempotente, aceita reentrega e registra chave processada.
- Retry tem backoff/limite; erro permanente vai para DLQ reprocessável e auditada.
- Lançamentos/evidências são append-only; correção gera compensação ou nova versão.
- Hash encadeado só vira prova após ADR definir canonicalização e verificação.

## Offline-first

O app Expo usa SQLite persistente e WAL. Cada operação possui `operation_id`, `device_id`, `tenant_id`, versão do schema, instantes, payload e estado (`pending`, `sending`, `acked`, `conflict`, `failed`). O servidor responde por item, aceita reenvio idempotente e fornece cursor.

Last-write-wins por campo não basta para dinheiro, estoque ou evidência. Campos críticos exigem conflito explícito ou compensação; a matriz pertence à SPEC de sync.

## APIs e segurança

- OpenAPI em `/v1`; DTO valida forma/limite e domínio valida invariantes.
- Erro `application/problem+json`: `type`, `title`, `status`, `code`, `correlationId`.
- Autorização por função e por objeto em toda operação; ID imprevisível não substitui autorização.
- Webhook valida assinatura, timestamp, replay, tamanho e idempotência.
- Certificado A1 usa envelope encryption; segredo fica em secret manager.
- Logs não carregam XML, token, certificado, áudio, coordenada precisa ou PII sem redaction.

## Observabilidade, resiliência e evolução

- OpenTelemetry para traces, métricas e logs correlacionados; reutilizar convenções semânticas oficiais.
- SLIs: disponibilidade, p95 do dashboard, atraso do pipeline, sucesso/idade da fila de sync e geração de relatório.
- Integrações têm timeout, retry seletivo, reconciliação e cobertura conhecida.
- Migração de banco usa expand/contract. Kubernetes, Kafka, sharding e multi-region exigem benchmark e ADR. Worker CPU-intensivo pode usar processo/serviço próprio sem romper o contrato dos eventos.

## Referências

- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryq.dev/)
- [Expo local-first](https://docs.expo.dev/guides/local-first/)
- [PostgreSQL 16: RLS](https://www.postgresql.org/docs/16/ddl-rowsecurity.html)
- [OWASP API Security](https://api-security.owasp.org/editions/2023/en/0x00-header/)
- [OpenTelemetry](https://opentelemetry.io/docs/concepts/semantic-conventions/)
