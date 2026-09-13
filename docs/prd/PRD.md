# SAFRAOS — PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Sistema operacional financeiro e regulatório do agro brasileiro
**Versão:** 2.0 · **Data:** 12 de setembro de 2026 · **Autor:** Produto · **Status:** Validado para build do MVP
**Público:** Engenharia, Design, Dados, Compliance, GTM, Founders

---
## SUMÁRIO EXECUTIVO
1. Contexto e oportunidade
2. Visão, missão e princípios de produto
3. Personas e jobs-to-be-done
4. Escopo do MVP e fora de escopo
5. Especificação funcional detalhada (Módulos A–D)
6. Histórias de usuário e critérios de aceite
7. Fluxos críticos (UX)
8. Modelo de dados (entidades principais)
9. Integrações e APIs
10. Requisitos não-funcionais
11. Modelo de precificação
12. Roadmap e releases
13. Métricas de produto
14. Riscos e mitigação
15. Apêndices (hipóteses, pesquisa, glossário)

---
# 1. CONTEXTO E OPORTUNIDADE
## 1.1 Problema
O produtor médio brasileiro (100–2.000 ha) opera com planilhas e caderno de campo. Consequências mensuráveis:
- Custo real por talhão só conhecido no fim da safra — margem reativa, não gerenciável.
- 8–12 h/semana do contador rural digitando notas e fechando LCDPR.
- Exportadores (UE) exigem due diligence de desmatamento (EUDR): zero desmatamento pós-31/12/2020, evidência georreferenciada por lote. CAR é autodeclaratório e <11% verificado.
- Compliance hoje é consultoria manual (US$ 5k+/ano) ou relatório estático gratuito (Selo Verde), desconectado da operação.

## 1.2 Por que agora
- EUDR aplicável a soja, carne, café, cacau, madeira, borracha; adiamentos acumularam demanda reprimida.
- CBAM pressiona cadeias de aço/cimento/alumínio; ESG de cadeia migra para agro.
- Rodadas de crédito rural 2025/26: R$ 329,2 bi — bancos demandam rastreabilidade.
- Concorrentes de gestão (Aegro, eProdutor) validaram o mercado mas ignoram compliance; players de compliance ignoram a fazenda. Ninguém une os dois.

## 1.3 Tese
Quem detém o dado operacional da safra detém o compliance — e o crédito. SafraOS nasce da operação (registro no campo) e escala para compliance auditável e rede de dados, num flywheel:
campo → financeiro → compliance → crédito → mais campo.

## 1.4 Métricas de mercado (resumo)
- TAM BR: ~R$ 4,3 bi (2030) · SAM: R$ 1,26 bi/ano · SOM 2030: R$ 38 mi ARR (3% do SAM)
- Alvo: ~180 mil operações médias/grandes + cooperativas; ARPU blended R$ 7.000/ano

---
# 2. VISÃO, MISSÃO E PRINCÍPIOS
**Visão (2030):** Toda fazenda média brasileira exportável opera sobre o SafraOS — do lançamento no talhão à declaração de due diligence.
**Missão do MVP:** Em 12 meses, 360 fazendas fecham sua primeira safra completa com custo por talhão e relatório EUDR gerado pelo sistema.

**Princípios de produto (decisões de design):**
1. **Offline-first ou nada** — o talhão não tem sinal. Se o registro depende de internet, o dado não existe.
2. **Zero digitação dupla** — toda informação entra uma única vez (WhatsApp, NF-e automática, telemetria).
3. **Compliance é consequência, não tarefa** — o sistema gera a due diligence a partir do que já foi registrado.
4. **Dado do produtor pertence ao produtor** — exportação completa, anti-lock-in explícito (argumento de venda).
5. **Preço transparente** — sem "sob consulta"; o canal de contadores depende disso.

---
# 3. PERSONAS E JOBS-TO-BE-DONE
| # | Persona | Perfil | JTBD principal | Dor quantificada | Como atingimos |
|---|---|---|---|---|---|
| P1 | Dono/administrador | 35–60 anos, 100–2.000 ha, grãos ± pecuária, exporta ou quer exportar | "Saber minha margem por talhão e nunca perder um comprador por falta de compliance" | Medo de exclusão UE; margem descoberta no fim | Módulo A (margem) + C (EUDR) |
| P2 | Contador rural | Escritório com 30–60 fazendas de carteira | "Zerar digitação e fechar LCDPR sem retrabalho" | 8–12 h/semana/fazenda | A.4/A.5 + canal com comissão 20% |
| P3 | Encarregado/gerente de campo | Funcionário sírio, baixo escolaridade, usa WhatsApp | "Lançar em 10 segundos sem internet" | Caderno → planilha à noite | B.1–B.3 |
| P4 | Comprador/cooperativa/exportador | Recebe exigência EUDR de clientes UE | "Auditar fornecedores sem custo próprio" | Planilhas de fornecedores, risco de multa | C.7 (painel B2B2C) |
| P5 | Banco/agente de crédito | Crédito rural com provisão por risco ESG | "Precificar risco com dados reais" | Ausência de histórico auditável | D.2 (score) |

---
# 4. ESCOPO DO MVP (Q1 2027)
## 4.1 Dentro do escopo
- Módulo A: A.1–A.6 · Módulo B: B.1–B.3 · Módulo C: C.1–C.3 · Integrações: SEFAZ, SICAR/CAR, Prodes, WhatsApp API
- Onboarding assistido por contador parceiro · App Android/iOS · Web dashboard

## 4.2 Fora de escopo do MVP (explícito)
- Telemetria de máquinas (A.7 — V1.1) · Carbon accounting (C.6 — V2) · Marketplace de insumos (D.3 — V2) ·
  Silvicultura completa (V2) · Piscicultura/granjas (V3) · Emissão de NF-e própria do produto rural (usa busca SEFAZ)

## 4.3 Hipóteses críticas a validar no MVP
| Hipótese | Teste | Critério de validação |
|---|---|---|
| H1: WhatsApp vence o caderno | 30 fazendas-piloto usam B.1 por 60 dias | ≥60% dos lançamentos via WhatsApp após 30 dias |
| H2: Compliance fecha venda | Oferta Exporta para quem vende p/ cooperativa exportadora | ≥30% de conversão Gestão→Exporta em 90 dias |
| H3: Contador é canal viável | 5 contadores piloto com comissão 20% | ≥3 novas fazendas/contador em 90 dias; CAC efetivo <R$ 2.000 |
| H4: CAR/Prodes permitem verificação contínua confiável | Pipeline de dados em 3 estados (MT, MS, GO) | Precisão ≥95% no cruzamento (amostra auditada manual) |

---
# 5. ESPECIFICAÇÃO FUNCIONAL DETALHADA

## MÓDULO A — GESTÃO FINANCEIRA DA SAFRA
### A.1 Plano de contas agrícola nativo
- Plano de contas padrão Conab (COE/COT) pré-carregado, customizável por fazenda.
- Estrutura: Safra → Atividade (grãos/pecuária/silvicultura) → Fase (preparo/plantio/cultura/colheita) → Talhão/Lote.
- DRE consolidada e por atividade; rateio automático de indiretos (sede, diesel, mão de obra permanente) por driver configurável (área, horas-máquina, receita).
- **Critério de aceite:** fechamento de safra 2026/27 de uma fazenda-piloto de 500 ha com DRE por talhão reproduzindo planilha de referência com divergência <2%.

### A.2 Custo por talhão / lote de rebanho
- Apuração contínua (não só no fechamento): a cada lançamento o custo do talhão atualiza.
- Pecuária: curva do lote (kg ganho/dia), custo por @ produzida, conversão alimentar.
- **Aceite:** usuário P1 visualiza ranking de talhões por margem/ha em <3 cliques a partir da home.

### A.3 Fluxo de caixa projetado (GND)
- Curva de necessidade de capital por mês de safra, com cenários de preço (insert Conab/série histórica).
- **Aceite:** simular safra 2027 com preço -10% recalcula GND em <5 s.

### A.4 Busca automática NF-e (entrada) + emissão (saída)
- Consulta diária à SEFAZ (distDFe) por CNPJ da fazenda: XMLs de entrada pré-lançados na fila de conferência (padrão eProdutor).
- Emissão NF-e/MDF-e ilimitada e gratuita (padrão Aegro); NFS-e por município (fase 2).
- **Aceite:** 0 digitação manual para notas de insumo; conferência em ≤30 s/nota.

### A.5 LCDPR + integração contábil
- Geração automática do Livro Caixa Digital do Produtor Rural (layout RFB) por ano-calendário.
- Exportação: Domínio Sistemas, Contmatic, Thomson Reuters (planilha padrão como fallback).
- **Aceite:** contador P2 baixa LCDPR pronto para transmitir sem edição em 100% das fazendas-piloto.

### A.6 Multiatividade (grãos + pecuária no MVP)
- Rateio de custos indiretos compartilhados entre atividades por driver configurável.
- **Aceite:** fazenda com soja + 300 cabeças gera DRE separada por atividade sem lançamento manual duplicado.

## MÓDULO B — REGISTRO DE CAMPO COM IA
### B.1 WhatsApp com IA confirmatória
- Número oficial SafraOS por fazenda; mensagens de texto/áudio/foto.
- Pipeline: NLU (Pt-BR, sotaques regionais) → extração de entidades (insumo, quantidade, talhão, máquina, valor) → confirmação em cartão (botões "Confirmar/Editar") → gravação.
- Treinamento por few-shot com vocabulário rural (ex.: "girei 400 litros de glifosato no talhão 12").
- Fallback: se confiança <0,75, rotear para humano (CSM) em <2 h úteis.
- **Aceite:** precisão de extração ≥90% em 500 lançamentos de teste; tempo médio lançamento <20 s.

### B.2 App offline-first
- Android/iOS (React Native); SQLite local; fila de sincronização com resolução de conflito por campo + timestamp (last-write-wins por campo, com log).
- Registro de campo com GPS (precisão configurável para economia de bateria).
- **Aceite:** 100% das funcionalidades de registro disponíveis offline; sincronização automática ao reconectar; zero perda de lançamento em teste de 30 dias.

### B.3 Georreferência automática
- Todo lançamento carrega coordenada (app) ou local declarado (WhatsApp).
- Base estrutural do compliance: talhão poligonal × lançamento.
- **Aceite:** 100% dos lançamentos georreferenciados; mapa de calor de atividade por talhão visível no dashboard.

## MÓDULO C — COMPLIANCE & RASTREABILIDADE (diferencial proprietário)
### C.1 Verificação contínua CAR
- Ingestão diássia: SICAR (CAR), Prodes/Prodes Cerrado (INPE), embargos IBAMA e estaduais, UC/APP (shapefiles IBGE/ICMBio).
- Motor de cruzamento espacial (PostGIS): polígono CAR × polígonos de risco → flags: desmatamento pós-2020, sobreposição com embargo, inconsistência de área (>5%).
- Alerta proativo (WhatsApp/e-mail) a cada novo evento; semáforo por fazenda.
- **Aceite:** pipeline diário com SLA de 24 h; precisão validada ≥95% em auditoria manual de 50 fazendas.

### C.2 Due diligence EUDR por lote
- Para cada lote comercializado: evidência compilada = polígono do talhão + histórico de lançamentos + notas de venda (NF-e) + GTA (pecuária) + verificação C.1.
- Declaração de due diligence (formato alinhado à Reg. UE 2023/1115, anexo de referência) gerada automaticamente; geolocalização e data de produção incluídas.
- **Aceite:** exportador-convidado aceita a declaração sem re-trabalho manual em ≥80% dos casos piloto.

### C.3 Relatório auditável exportável
- PDF PT/EN assinado digitalmente (ICP-Brasil), com hash de evidências e trilha de versionamento (o que mudou, quando, quem).
- Portal de verificação: QR code no relatório aponta para página pública de validação (hash + status).
- **Aceite:** relatório validável por terceiros sem acesso ao sistema; tempo de geração <60 s.

## MÓDULO D — REDE DE DADOS (V1 em diante)
- D.1 Benchmark anônimo: preço de insumo e custo/ha por região-cultura.
- D.2 Score de crédito rural (V2): regressão sobre histórico financeiro + compliance; prêmio de taxa negociado com 1 banco parceiro.
- D.3 Marketplace de insumos (V2): ofertas regionais, receita por lead qualificado.

---
# 6. HISTÓRIAS DE USUÁRIO (seleção priorizada — MVP)
| ID | História | Critério de aceite | Módulo |
|---|---|---|---|
| US-01 | Como encarregado (P3), quero lançar uma aplicação de defensivo por WhatsApp com áudio, para não usar caderno | Áudio transcrito e confirmado em <20 s; lançamento vinculado ao talhão | B.1 |
| US-02 | Como dono (P1), quero ver margem por talhão em tempo real, para decidir onde investir | Ranking atualizado a cada lançamento; exportável em PDF | A.2 |
| US-03 | Como contador (P2), quero que as NF-e de entrada entrem pré-lançadas, para não digitar | 0 digitação; conferência ≤30 s/nota | A.4 |
| US-04 | Como dono (P1), quero receber alerta se meu CAR tiver desmatamento novo, para agir antes do banco | Alerta em <24 h do evento Prodes, com polígono e área | C.1 |
| US-05 | Como dono (P1), quero gerar a declaração EUDR da minha soja em 1 clique, para vender à UE | Declaração PT/EN gerada <60 s, com evidências anexadas | C.2/C.3 |
| US-06 | Como cooperativa (P4), quero ver o semáforo de compliance dos meus 200 fornecedores, para cobrar quem está vermelho | Painel consolidado; drill-down por fazenda | C.5 (V1.1) |
| US-07 | Como encarregado (P3), quero lançar offline e sincronizar depois, para cobrir área sem sinal | 100% dos lançamentos offline preservados | B.2 |
| US-08 | Como dono (P1), quero baixar todos os meus dados, para não ficar refém do sistema | Exportação completa (CSV/JSON/geo) em <24 h, self-serve | NFR |

---
# 7. FLUXOS CRÍTICOS (UX)
## F1 — Onboarding da fazenda (meta: <45 min até primeiro valor)
1. Cadastro CNPJ → pré-preenchimento (CNPJá/Receita) · 2. Polígono de talhões: upload KML/GeoJSON ou desenho no mapa · 3. Conexão SEFAZ (certificado digital) · 4. Importação de NF-e últimos 90 dias · 5. Convite do contador · **Primeiro valor:** plano de safra sugerido com dados históricos de 90 dias.

## F2 — Lançamento de campo (meta: <20 s)
WhatsApp (áudio) → transcribe → cartão de confirmação → georreferência automática → custo do talhão atualiza em tempo real.

## F3 — Venda para exportador (o "momento mágico")
NF-e de venda emitida → sistema detecta destinatário exportador/cooperativa → sugere geração da due diligence → 1 clique → PDF PT/EN assinado → link enviado ao comprador.

## F4 — Alerta de compliance (proativo)
Novo polígono Prodes intersecta CAR → semáforo vira amarelo/vermelho → WhatsApp ao dono com mapa → recomendação de ação (contestar embargo, ajustar área, isolar talhão).

---
# 8. MODELO DE DADOS (entidades principais)
```
Fazenda(id, cnpj, nome, estado, municipio, plano)
  ├─ Talhao(id, fazenda_id, poligono_geojson, area_ha, cultura, safra)
  ├─ Atividade(id, fazenda_id, tipo[graos|pecuaria|silvicultura])
  ├─ LotePecuaria(id, atividade_id, n_animais, data_entrada, curva[])
  ├─ Lancamento(id, origem[whatsapp|app|nfe|telemetria], tipo, entidades_json,
  │              geo POINT, talhao_id?, timestamp_local, timestamp_sync, hash)
  ├─ NFe(id, fazenda_id, chave_acesso, xml, direcao[entrada|saida], emitente,
  │      valor, itens_json, status[pre_lancada|conferida|lancada])
  ├─ Safra(id, fazenda_id, ano, cultura, orcamento_json, fechamento_json)
  ├─ VerificacaoCompliance(id, fazenda_id, fonte[prodes|embargo|car], evento_geo,
  │                       area_ha, data_ref, status[ok|alerta|critico], evidencia_hash)
  ├─ DueDiligence(id, lote_ref, talhoes_json, nfes[], gtas[], hash_evidencias,
  │              pdf_url, assinatura, idioma[pt|en], created_by)
  ├─ Usuario(id, fazenda_id, papel[dono|gerente|contador], whatsapp_id)
  └─ ContadorParceiro(id, escritorio, comissao_pct, clientes[])
```
Princípios: todo lançamento imutável (append-only, com hash); dados espaciais em PostGIS; PII criptografada (AES-256); chaves por tenant.

---
# 9. INTEGRAÇÕES E APIs
| Sistema | Uso | Tipo | Prioridade | Risco |
|---|---|---|---|---|
| SEFAZ (distDFe + emissão NF-e) | NF-e entrada/saída | API REST + certificado A1 | MVP | Instabilidade estadual → fila com retry |
| SICAR/INCRA | CAR por estado | Download periódico / scraping assistido | MVP | Heterogeneidade estadual → parser por UF, começando MT/MS/GO |
| INPE (Prodes/TerraBrasilis) | Desmatamento anual | WFS/WCS + download shapefile | MVP | Atualização anual → verificação contínua via alertas DETER (quase tempo real) como complemento |
| IBAMA (embargos) | Lista de embargos | Download CSV/SHP | MVP | — |
| WhatsApp Business API (Meta) | Canal de registro e alertas | Cloud API | MVP | Política de templates → aprovação antecipada |
| Beweather / estações | Clima | API parceira | V1.1 | — |
| FieldView / John Deere / Stara | Telemetria | OAuth2 + webhooks | V1.1 | Dependência de parceria → começar com importação de arquivos (shapefile/CSV) |
| Domínio/Contmatic/Thomson | Contabilidade | Exportação planilha/API | MVP (planilha) | — |
| Serasa/experian ou banco parceiro | Score de crédito (D.2) | API | V2 | — |

## 9.1 API pública do SafraOS (para parceiros)
- `POST /v1/verificacao/eudr` — gera due diligence (autenticado por fazenda)
- `GET /v1/compliance/{fazenda_id}/status` — semáforo atual (para cooperativas P4)
- `POST /v1/webhooks/lancamento` — eventos para integradores
Rate limit: 600 req/min por tenant. Documentação OpenAPI pública.

---
# 10. REQUISITOS NÃO-FUNCIONAIS
| Categoria | Requisito |
|---|---|
| Disponibilidade | 99,9% mensal (API web); app de campo 100% offline |
| Performance | Dashboard <2 s (p95); geração de relatório EUDR <60 s; sync de 1.000 lançamentos <3 min |
| Segurança | AES-256 em repouso, TLS 1.3; MFA para dono/contador; trilha de auditoria append-only; pentest anual; assinatura ICP-Brasil nos relatórios |
| Escalabilidade | Multi-tenant; 5.400 fazendas até 2030; pipeline de geodados em fila (Celery/SQS) com reprocessamento |
| Acessibilidade/UX | App em Pt-BR simples (ler com 8 anos de escolaridade); áudio como alternativa a texto; modo "sol grande" (alto contraste) para uso a céu aberto |
| Anti-lock-in | Exportação completa self-serve <24 h (CSV/JSON/GeoJSON) |

---
# 11. MODELO DE PRECIFICAÇÃO
| Plano | Conteúdo | Preço | Alvo |
|---|---|---|---|
| Essencial | Financeiro safra + NF-e/LCDPR + app de campo (até 100 ha) | **Grátis** | Wedge: vencer a dor diária, gerar base de dados |
| Gestão | Essencial + multiatividade + IA WhatsApp + relatórios | R$ 5.000/ano | P1 não-exportador |
| Exporta | Gestão + Compliance EUDR/CAR + relatório auditável EN + alertas proativos | + R$ 4.000/ano | P1 exportador (ARPU blended R$ 7.000–9.000) |
| Cooperativa | Painel de compliance de fornecedores + due diligence consolidada | R$ 0,80–1,20/ha monitorado | P4 (contratos de R$ 200–800 mil/ano) |
| Implantação | Onboarding assistido com contador parceiro | R$ 2.500 (onboarding pago) | Custo de aquisição parcial |
| Comissão canal | Contador revende com 20% recorrente | — | CAC efetivo ~R$ 2.000 |

Regras: upgrade/downgrade pro-rata; compliance cobrado por fazenda (não por ha) para não punir escala; cooperativa exige SafraOS dos fornecedores (viral loop B2B2C).

---
# 12. ROADMAP
| Release | Janela | Escopo | Metas de negócio |
|---|---|---|---|
| **MVP** | Q1 2027 | A.1–A.6, B.1–B.3, C.1–C.3, integrações MVP | 360 fazendas · R$ 3 mi ARR · validar H1–H4 |
| **V1.1** | Q3–Q4 2027 | A.7 telemetria (arquivo→API), A.8–A.9, B.4–B.5, C.5 painel cooperativa, D.1 benchmark | 800 fazendas · NRR ≥105% |
| **V2** | 2028 | C.6 carbon accounting, C.7 verificação fornecedores, D.2 score crédito (1 banco), D.3 marketplace | 1.260 clientes · R$ 9 mi ARR · 2 contratos cooperativa |
| **V3** | 2029 | Carbon completo (escopo 3 da cadeia), prêmio de crédito por compliance, silvicultura | 2.700 clientes · R$ 19 mi ARR · EBITDA positivo |
| **V4** | 2030 | Expansão LATAM (Paraguai, Bolívia, Argentina — mesmo perfil exportador UE) | R$ 38 mi ARR · Série A internacional |

---
# 13. MÉTRICAS DE PRODUTO
**North star: hectares com custo de safra fechado no sistema por ano.**
| Métrica | Definição | Meta 2027 | Guarda |
|---|---|---|---|
| Ativação | Primeiro lançamento WhatsApp em <7 dias | ≥70% | — |
| Aha | Relatório de margem por talhão visto 3× em 30 dias | ≥50% | — |
| WA share | % de lançamentos originados no WhatsApp | ≥60% | — |
| EUDR adoption | % de clientes Gestão→Exporta | ≥40% | — |
| NRR | Receita líquida de retenção | ≥108% | <100% = alarme |
| Churn logo | Anual | <20% | — |
| CAC payback | Meses | <18 | >24 = revisar canal |
| Alerta SLA | Verificação compliance <24 h | ≥99% | — |

Instrumentação: eventos server-side + app; dashboard Metabase; revisão quinzenal de funnel.

---
# 14. RISCOS E MITIGAÇÃO
| Risco | Prob. | Impacto | Mitigação | Dono |
|---|---|---|---|---|
| Aegro lança compliance nativo | Média | Alto | Profundidade regulatória (evidências auditáveis, trilha, ICP); velocidade: 2 safras de lock-in de dados | Produto |
| Selo Verde vira padrão gratuito obrigatório | Baixa | Alto | Integrar como camada de dados pública dentro do produto; vender operação + evidência contínua que ele não tem | Dados |
| EUDR adiado novamente | Média | Médio | Tese não depende de 1 regulamento: CAR/embargo (crédito) + LCDPR + ESG de cadeia (carbon V2) seguem | Founders |
| Dados CAR/Prodes ruins por estado | Alta | Médio | Começar MT/MS/GO (melhores bases); parser por UF; transparência de cobertura no relatório | Dados |
| WhatsApp API restringe templates | Média | Baixo | Aprovar templates antecipadamente; app como canal paralelo desde o dia 1 | Eng |
| Sazonalidade de receita | Alta | Médio | Compliance é anual-contínuo; contratos de cooperativa anuais; NRR >108% absorve | Finanças |
| Canibalização por cooperativa própria | Baixa | Alto | Modelo B2B2C coop-friendly: vender a ferramenta dela, não competir | GTM |

---
# 15. APÊNDICES
## 15.1 Hipóteses de mercado (fonte: análise 12/09/2026)
TAM global farm management US$ 10,5 bi (2030) × ~7,5% BR = R$ 4,3 bi; SAM = 180 mil operações × ARPU R$ 7 mil = R$ 1,26 bi/ano; SOM 2030 = 3% SAM = R$ 38 mi ARR. Unit economics base: LTV R$ 26.250, CAC R$ 9.500, LTV/CAC 2,8x, payback 21,7 meses; otimista (compliance+canal): 7,1x / 11,3 meses.

## 15.2 Benchmarks de concorrentes (resumo)
Aegro: R$ 529/mês entrada, IA WhatsApp (Aegrozap), telemetria FieldView/Deere, crédito rural; lacuna: sem compliance, só agricultura. eProdutor: modular, multiatividade, NF-e SEFAZ automática, IoT; lacuna: sem IA conversacional, sem compliance, preço opaco. TOTVS/Agrotitan: ERP pesado, implantação complexa. Agrotools: geoespacial enterprise. Selo Verde: relatório estático gratuito, insuficiente p/ cadeia. Koltiva/Meridia: US$ 5k+/ano, sem campo.

## 15.3 Glossário
CAR (Cadastro Ambiental Rural) · Prodes (INPE, desmatamento anual) · DETER (alertas quase tempo real) · EUDR (Reg. UE 2023/1115) · CBAM (taxa carbono UE) · LCDPR (Livro Caixa Digital do Produtor Rural) · COE/COT (custo de produção Conab) · GND (garantia necessária de disponibilidade) · GTA (guia de trânsito animal) · @ (arroba = 15 kg) · NRR (net revenue retention).

---
*Documento vivo — revisões mensais durante o MVP, quinzenais na fase de tração. Decisões de escopo acima deste PRD exigem alteração formal de versão.*

*BACKLOG.md - documento de revisão das ÉPICOS e HISTÓRIAS.
*Arquitetura.md - documento de revisão da arquitetura.
