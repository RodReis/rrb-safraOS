# Registro de itens fora de escopo

**Fonte única:** itens adiados ou excluídos de cada MVP
**Responsável:** Cowork
**Revisão:** 2026-09-13

Este documento evita que decisões de recorte desapareçam. Não é backlog paralelo: prioridade e estado de execução continuam no GitHub e no `docs/STATUS.md`.

## Regras

- Registrar o item no momento em que sair de um MVP.
- Informar destino somente quando houver decisão; não transformar expectativa em compromisso.
- Reentrada exige decisão do PI e atualização do MVP/SPEC correspondente.
- Issue ou SPEC só é criada quando o item entrar efetivamente em uma fatia.
- `adiado` significa que ainda pode voltar; `excluído` significa que saiu da direção atual.

## MVP0 — Fundação web

| Item | Situação | Motivo | Destino | Gatilho para reconsiderar | Decisão |
|---|---|---|---|---|---|
| Aplicativo Expo/mobile | adiado | duplicaria interface antes de validar domínio, tenancy e API | final do projeto | web e fluxos centrais estabilizados; prioridade explícita do PI | PI, 2026-09-13 |
| Sincronização offline | adiado | depende do aplicativo mobile | junto do mobile | protocolo e casos críticos aprovados | PI, 2026-09-13 |
| Importação KML | adiado | GeoJSON + desenho já validam o núcleo geoespacial | MVP posterior | necessidade real de onboarding/piloto | PI, 2026-09-13 |
| Deploy em nuvem | adiado | provedor, região e custo ainda não foram decididos | MVP posterior | ADR-008 aceita e fluxo local validado | PI, 2026-09-13 |
| Kubernetes, SQS e microserviços | adiado | complexidade operacional sem carga medida | sem destino definido | limite do monólito/infra demonstrado por métrica | PI, 2026-09-13 |
| WhatsApp e IA | adiado | não é necessário para provar a fundação | MVP posterior | domínio de lançamentos estável | PI, 2026-09-13 |
| Financeiro, NF-e e LCDPR | adiado | pertencem ao produto após a fundação | MVP posterior | MVP0 aceito e regras financeiras especificadas | PI, 2026-09-13 |
| CAR, Prodes, compliance e EUDR | adiado | dependem de fundação e decisões externas | MVP posterior | fontes, cobertura e critérios aprovados | PI, 2026-09-13 |
| CPF/CNPJ da fazenda | adiado | não agrega ao fluxo fundacional e antecipa regras fiscais | onboarding fiscal | integração fiscal especificada | PI, 2026-09-13 |
| Equipe, convites e papéis além de `owner` | adiado | o MVP0 valida somente propriedade e isolamento | MVP posterior | primeiro caso de colaboração aprovado | PI, 2026-09-13 |

## Campos obrigatórios para próximos MVPs

Toda nova linha deve preencher: item; situação (`adiado` ou `excluído`); motivo objetivo; destino decidido ou `sem destino`; gatilho verificável para reconsiderar; decisor e data real.
