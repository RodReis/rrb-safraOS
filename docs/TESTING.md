# Estratégia de testes e evidências

## Princípios

Teste prova requisito/risco. Ausência de ambiente/credencial é `not_run`, nunca `pass`. Resultado pertence ao SHA. Dublê valida nosso contrato, não o provedor. Evidência identifica SPEC, issue, categoria, comando, ambiente e resultado.

## Categorias

| Categoria | Prova |
|---|---|
| regras | invariantes, estados, arredondamento, idempotência |
| banco | migration, constraint, transação, RLS, tenant, PostGIS |
| tela | acessibilidade, responsividade e estados |
| E2E | fluxos F1–F4 tocados |
| contrato | OpenAPI, webhook, evento, provedor |
| resiliência | retry, timeout, DLQ, retomada, offline |
| segurança | autorização, upload, segredo, redaction, rate limit |
| performance | massa, ambiente, métrica e percentil declarados |

## Provas críticas

- Offline: reinício sem rede, reenvio sem duplicar, lote interrompido, cursor, conflito, schema e relógio incorreto.
- Financeiro/fiscal: soma/rateio/arredondamento; planilha versionada; XML duplicado/cancelado/fora de ordem.
- Geodados: geometria inválida, borda, CRS, dataset versionado, fonte incompleta vira `inconclusiva`.
- IA: corpus separado, precisão por entidade/cenário, limiar/fallback, prompt injection e replay de webhook.

## Relatório por runner

```json
{"schemaVersion":1,"issue":0,"spec":"SPEC-000","sha":"","category":"regras","status":"pass|fail|not_run","command":"","environment":"","durationMs":0,"summary":"","limitations":[]}
```

O agregador apenas consolida JSON; histórico é append-only. Alteração do gerador prova casos `pass`, `fail` e `not_run`.

## Gate

`quality`, `test-regras`, `test-banco`, `test-tela` e `e2e` rodam em paralelo quando aplicáveis. O agregador valida artefatos; `gate` usa `if: always()` e resultados explícitos. Cache só acelera dependência, nunca armazena PASS.

