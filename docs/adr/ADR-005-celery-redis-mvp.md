# ADR-005 — Celery + Redis para processamento assíncrono no MVP

**Estado:** aceita
**Data:** 2026-09-13
**Decisor:** PI (Rodrigo Reis)

## Contexto

O produto precisa de processamento assíncrono desde o MVP0 (confirmação/recuperação de e-mail via outbox) e, no MVP-001, para pipelines mais pesados (ingestão geoespacial diária, WhatsApp/IA, NF-e). A arquitetura histórica já cogitava "SQS + ECS" para escala futura.

## Decisão

Celery + Redis é a fila/worker do MVP. SQS, ECS ou qualquer outra fila gerenciada exige medição de carga real e nova ADR antes de substituir.

## Alternativas consideradas

- SQS/ECS desde o início: descartada — exige conta cloud e infraestrutura gerenciada que o MVP0 (100% local, Docker Compose) não usa; sem carga medida que justifique.
- Redis Streams vs. Kafka como event bus: pergunta em aberto, não decidida por esta ADR (ver `docs/historico/Arquitetura-2026-09-12.md` §8, item 1 — permanece como possível ADR futura se a carga justificar).

## Consequências

- `docker-compose` do MVP0 inclui Redis; Celery roda como processo `apps/worker` no monólito modular (ADR-002).
- Transactional outbox (`docs/ARCHITECTURE.md` §Consistência) é o padrão de publicação de eventos para os workers.

## Riscos / reversibilidade

Reversível: troca de fila é uma mudança de infraestrutura isolada atrás da interface de outbox/consumidor, não do domínio.

## Evidência

Registrada em `docs/DECISIONS.md` desde 2026-09-13.

## Links

`docs/ARCHITECTURE.md` §2 (stack), §Consistência e assíncrono. `docs/prd/mvp/MVP-000.md` §4.
