> **Superado em 2026-09-13.** Este brief se autointitulava "PRD CONSOLIDADO v2.1" com data futura (março de 2027) e listava requisitos que nenhuma SPEC ou o PRD real jamais aprovaram: fazendas de 100–5.000 ha, 96% de acurácia de transcrição, SLA de desembaraço <48h, integração SIGEF/INCRA e Terras Indígenas, CPR/Barter, câmbio PTAX, GPS RTK, exportador contábil Prosoft, importação direta de monitores John Deere/Trimble/Climate FieldView. Nada disso é contrato. É mantido como **referência visual e de brainstorm** para o design system (`docs/design-system/`), nunca como PRD. O PRD real é `docs/prd/PRD.md`.

---

# SAFRAOS — EXECUTIVE PROJECT BRIEF (referência de design, não PRD)
## Sistema Operacional Agro-Financeiro, Georreferenciamento & Compliance EUDR
**Autor original:** Produto & Design de Produto (SafraOS Core Team)

---

## 1. VISÃO GERAL & TESE DE PRODUTO
O **SafraOS** é uma plataforma agro-fintech que resolve a fragmentação entre o caderno de campo, a gestão contábil-fiscal e as exigências regulatórias internacionais da cadeia de suprimentos agrícolas no Brasil.

### 1.1 O Flywheel Estratégico
```
[ Campo (App Offline & WhatsApp IA) ]
                 ↓
[ Financeiro Real-Time & Custo/Talhão ]
                 ↓
[ Compliance Automatizado (CAR, PostGIS & EUDR) ]
                 ↓
[ Crédito Rural Barato, LCDPR sem Atrito & Liquidez ]
                 ↓
        (Retenção e Expansão de Área)
```

---

## 2. PERSONAS & JOBS-TO-BE-DONE (JTBD)

| Persona | Perfil & Contexto | Principal JTBD | Impacto Mensurável |
|---|---|---|---|
| **P1: Produtor / Gestor Rural** | Dono/CFO de 100 a 5.000 ha (grãos e pecuária) | "Saber o custo real por talhão em tempo real e nunca ter carga travada na trading por compliance ambiental." | Margem por talhão apurada continuamente; exportação EUDR em 1 clique. |
| **P2: Contador Rural Parceiro** | Escritório contábil com carteira de 20–60 produtores | "Eliminar a digitação manual de notas fiscais e fechar o LCDPR com conciliação bancária sem risco de malha fina." | Redução de 8–12h/semana por cliente; 20% de comissão recorrente vitalícia. |
| **P3: Encarregado / Operador** | Trabalhador no campo, sob sol forte e sem sinal de internet | "Registrar aplicações, horímetro e diesel em menos de 20 segundos sem precisar de caderno de papel." | Transcrição de áudio em linguagem rural com 96% de acurácia; app 100% offline. |
| **P4: Cooperativa / Trading** | Analistas de originação, ESG e exportação | "Auditar a cadeia de fornecedores e emitir dossiês de embarque com coordenadas geodésicas imutáveis." | SLA de desembaraço <48h; semáforo de risco automatizado sobre CAR/PRODES. |

---

## 3. ARQUITETURA DE TELAS & MAPA DO PRODUTO (ARTEFATOS CRIADOS)

### MÓDULO WEB DESKTOP (Gestão, Finanças & Governança)
1. **Visão Geral da Safra (Executive Dashboard)**
   - KPIs consolidados: Custo Realizado vs. Orçado, Margem Bruta Projetada/ha, Posição de Caixa (GND).
   - Semáforo regulatório EUDR (hectares aptos para exportação direta).
   - Feed operacional em tempo real (áudios de WhatsApp, NF-e distDFe capturadas e alertas DETER/INPE).
2. **Custo & Margem por Talhão (Analítico Geoespacial)**
   - Decomposição de despesas: defensivos, adubos, sementes, diesel, depreciação e rateio de indiretos.
   - Mapa temático com curvas de margem líquida (R$/ha) e ponto de equilíbrio agronômico (sc/ha).
3. **Conferência de NF-e & Livro Caixa (LCDPR)**
   - Varredura contínua SEFAZ distDFe com pré-classificação por IA no plano de contas CONAB.
   - Validador do leiaute RFB (Registros 0000 a 9999) e conciliação bancária automática.
4. **Compliance EUDR & Rastreabilidade Georreferenciada**
   - Motor espacial PostGIS cruzando polígonos com bases oficiais (PRODES pós-2020, embargos IBAMA/SEMA e Terras Indígenas).
   - Emissão da Due Diligence Statement (Regulamento UE 2023/1115) com assinatura digital ICP-Brasil e QR Code público.
5. **DRE & Análise Multiatividade (Grãos + Pecuária)**
   - Demonstração do Resultado do Exercício com segregação de receitas e custeio COE/COT.
   - Painel pecuário de confinamento (GPD, conversão alimentar e margem/@ produzida).
6. **Fluxo de Caixa Projetado & Simulação de Safra (Curva GND)**
   - Curva mensal de desembolso vs. receitas de colheita/CPR/Barter.
   - Simulador de estresse de mercado (sensibilidade a variação de preço da soja/milho e câmbio PTAX).
7. **Portal do Contador Parceiro & Fechamento LCDPR**
   - Painel multicliente com 38 fazendas da carteira, termômetro fiscal e comissionamento recorrente de 20%.
   - Exportadores homologados para Domínio Sistemas, Contmatic, Thomson Reuters e Prosoft.
8. **Gestão de Fazendas & Matrículas (CRUD Multi-Farm & Geo)**
   - Cadastro de propriedades, situação fundiária (SIGEF/INCRA), status SEFAZ e sincronização com o SICAR estadual.
9. **Gestão de Talhões & Georreferenciamento (CRUD Vetorial)**
   - Importação de shapefiles/KML/GeoJSON direto de monitores John Deere, Trimble e Climate FieldView.
   - Tabela de parcelas, metas de produtividade e cálculo de sobreposição cartorial.
10. **Usuários, Encarregados & Permissões Granulares (RBAC)**
    - Gestão de acessos com MFA mandatório, matriz de Segregação de Funções (SoD) e autorização de números WhatsApp para IA.
11. **Onboarding Guiado da Fazenda (Fluxo F1 <45 min)**
    - Configuração rápida: CNPJ → Upload KML → Certificado A1 SEFAZ → Primeiro Plano de Safra sugerido.
12. **Painel B2B de Originação para Cooperativas & Tradings**
    - Monitoramento em escala de cooperados/fornecedores, alocação de navios graneleiros e disparo de alertas em massa.

### MÓDULO MOBILE DE CAMPO (Operacional & Offline-First)
1. **SafraOS Campo — App Offline-First**
   - Botões de toque extra largo, modo "Sol Forte" (alto contraste para leitura a céu aberto).
   - Ações imediatas: defensivos, plantio, abastecimento de comboio e pluviômetro com geolocalização RTK.
2. **SafraOS Campo — Fila Local de Sincronização**
   - Banco de dados SQLite v4 embarcado, resolução de conflitos determinística *Last-Write-Wins (LWW)* por campo.
3. **SafraOS WhatsApp IA — Registro por Áudio**
   - Transcrição fonética do vocabulário do campo via NLU especializada com geração de extrato pré-validado e confirmação em 1 toque.

---

## 4. MODELO DE DADOS & ENTIDADES ESSENCIAIS (PostgreSQL / PostGIS)
```
Fazenda (id, cnpj, razao_social, sicar_id, status_sefaz, tenant_key)
  ├── Talhao (id, fazenda_id, geom GEOMETRY(Polygon, 4674), area_ha, cultura, safra_vigente)
  ├── Usuario (id, fazenda_id, perfil[RBAC], whatsapp_e164, mfa_secret, certificado_a1)
  ├── Lancamento (id, fazenda_id, talhao_id, tipo, insumo, qtd, valor, geo POINT, status_sync)
  ├── NFe (id, fazenda_id, chave_44, emitente, xml, cod_conab, status_lcdpr)
  ├── DueDiligenceEUDR (id, lote_codigo, talhoes_json, hash_sha256, status_ue, pdf_url)
  └── LotePecuaria (id, fazenda_id, raca, n_cabecas, gpd_medio, custo_arroba)
```

---

## 5. REQUISITOS NÃO FUNCIONAIS & CRITÉRIOS DE CONFORMIDADE
- **Segurança & Criptografia:** Criptografia AES-256 para dados em repouso e TLS 1.3 em trânsito; isolamento estrito por tenant.
- **Assinatura e ICP-Brasil:** Relatórios fiscais e declarações EUDR com carimbo de tempo e hash auditável.
- **Anti-Lock-in:** Exportação integral e descomplicada de dados espaciais (GeoJSON, SHP, KML) e contábeis (CSV, TXT LCDPR).
- **Disponibilidade e Resiliência:** Arquitetura offline-first no campo; tolerância a quedas da API da SEFAZ com filas de reprocessamento assíncrono.
