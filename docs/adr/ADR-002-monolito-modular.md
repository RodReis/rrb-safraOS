# ADR-002 — Forma de deploy: monólito modular

**Estado:** aceita
**Data:** 2026-09-13
**Decisor:** PI (Rodrigo Reis)

## Contexto

A arquitetura histórica (`docs/historico/Arquitetura-2026-09-12.md`) propunha quatro serviços de domínio com deploy independente desde o MVP (Financeiro, Campo+IA, Compliance, Integrações), com Kubernetes/EKS. O `docs/ARCHITECTURE.md` já assumia monólito modular como forma inicial, e o MVP0 (SPEC-001, MVP-000 §4) foi especificado sobre essa premissa antes da ADR ser formalmente aceita — risco registrado em `docs/STATUS.md`.

## Decisão

Começar como **monólito modular**: uma API FastAPI com módulos internos (identidade/tenancy, fazendas/talhões, campo/sync, financeiro/fiscal, compliance/geodados, integrações/notificações, relatórios/auditoria) e workers Celery separáveis por processo, mas sem deploy independente por módulo.

## Alternativas consideradas

- Quatro serviços com deploy independente (arquitetura histórica): descartada para o MVP0/MVP-001 por aumentar deploy, observabilidade e consistência distribuída sem carga comprovada (360 fazendas, ~0,5 mi ha no ano 1).

## Consequências

- Fronteira de módulo não autoriza deploy independente; extração de um módulo para serviço próprio exige medição de carga/falha/autonomia e nova ADR (`docs/ARCHITECTURE.md` §Forma inicial).
- CI/infra do MVP0 permanece simples (um serviço web, um worker), reduzindo custo de manter o gate verde.

## Riscos / reversibilidade

Reversível: a extração de um módulo em serviço próprio é prevista como evolução natural, não como retrabalho de reescrita, desde que as fronteiras de módulo (contratos internos) sejam respeitadas desde o início.

## Evidência

Recomendação técnica registrada em `docs/DECISIONS.md` desde 2026-09-13; aceite formal do PI nesta sessão (Cowork), 2026-09-13.

## Links

`docs/ARCHITECTURE.md` §Forma inicial. `docs/prd/mvp/MVP-000.md` §4. Substitui a topologia de 4 serviços de `docs/historico/Arquitetura-2026-09-12.md` §3.
