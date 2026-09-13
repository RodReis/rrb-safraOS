# Convenções de domínio

**Estado:** vocabulário inicial derivado do PRD; conflitos continuam pendentes.
**Revisão:** 2026-09-13

## Linguagem ubíqua

| Termo | Significado |
|---|---|
| Tenant | fronteira de isolamento de uma organização; não é sinônimo automático de fazenda |
| Fazenda | unidade administrativa/fiscal com talhões, atividades, safras e usuários autorizados |
| Talhão | área produtiva com geometria válida, pertencente a uma fazenda |
| Lançamento | fato de campo/financeiro append-only recebido de um canal |
| Operação de sync | comando idempotente criado no dispositivo e confirmado pelo servidor |
| Evidência | artefato versionado usado em verificação/due diligence |
| Verificação | resultado reproduzível entre fonte versionada e objeto avaliado |
| Semáforo | projeção explicável; nunca fonte primária |

## Invariantes

- Registro de cliente pertence a exatamente um tenant e nunca atravessa tenant.
- Área canônica deriva da geometria; divergência com valor informado é registrada.
- Lançamento confirmado não é sobrescrito; correção gera compensação/nova versão.
- A mesma operação externa não produz efeito duas vezes.
- Dinheiro não usa `float`; cálculo puro recebe relógio por parâmetro.
- Resultado derivado guarda versões das entradas e algoritmo necessárias à reprodução.
- Due diligence emitida é imutável; fato novo gera outra versão.

## Estados mínimos

```text
sync: pending -> sending -> acked | conflict | failed -> pending
NF-e: descoberta -> pre_lancada -> conferida -> lancada | rejeitada
verificação: processando -> ok | alerta | critico | inconclusiva
due diligence: rascunho -> gerando -> emitida | falhou; emitida -> substituida
```

## Nomes, unidades e auditoria

- Código em inglês; UI/docs em PT-BR. IDs UUID/ULID e códigos de erro estáveis.
- Área em hectare com precisão; massa conserva origem e normalização. Conversão de arroba exige regra explícita.
- Ação sensível registra ator, tenant, instante, origem, `correlationId` e resultado.
- Integração usa identidade própria. Portal público revela só o mínimo para validar hash/status.

## Questões que não podem ser inventadas

Relação tenant/grupo/fazenda; conflitos offline; rateio/arredondamento; precedência NF-e versus correção; critérios do semáforo. Privacidade é governada separadamente por `docs/PRIVACIDADE.md` e não cria regra de domínio neste arquivo.
