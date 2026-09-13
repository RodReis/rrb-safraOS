# COMPONENTS — SafraOS Design System

Inventário dos componentes que **existem de fato** nas telas de referência, com a variante canônica escolhida quando havia concorrentes. Base shadcn/ui estilizada pelos tokens de [TOKENS.md](TOKENS.md).

Formato de cada entrada: **papel** → **anatomia** → **regra** → **onde ver**.

---

## 1. Estrutura de aplicação

### 1.1 AppShell

Quatro arquétipos de header coexistem nas referências. **Canônico: dois**, escolhidos por plataforma.

**Desktop (`sidebar + header`)** — Gestão, Finanças, Governança.
- Sidebar fixa, largura `288px` (`w-72`), superfície nível 1, header interno `h-16` alinhado ao header principal.
- Header fixo à direita da sidebar, `h-16`, superfície nível 1 com leve translucidez + blur, `z` acima do conteúdo e abaixo de drawer/modal.
- Área de conteúdo com largura máxima e `margin` lateral conforme breakpoint (ver `PATTERNS.md` §Grid).

**Mobile de campo (`header + bottom nav`)** — Campo, Fila de Sync, WhatsApp IA.
- Header fixo `w-full` com `padding-top: env(safe-area-inset-top)`.
- Bottom nav fixa `h-80px` com `padding-bottom: env(safe-area-inset-bottom)`.
- Sem sidebar, sem tabela.

Ordem de `z`: conteúdo < header/nav < drawer < modal < toast.

Onde ver: `escuro/dre_an_lise_multiatividade_gr_os_pecu_ria`, `escuro/safraos_campo_app_offline_first`.

### 1.2 Sidebar / NavItem

- Item: linha com ícone + rótulo, `rounded-lg`, altura de alvo mínima 36px desktop.
- Estado padrão: texto `on-surface-variant`; hover eleva superfície um nível e texto vai a `on-surface`.
- Estado ativo: fundo `primary-container`, texto `on-primary`, peso 600, **e** `aria-current="page"`.
- Grupos de navegação separados por rótulo `badge-label` uppercase em `on-surface-variant`.

As referências têm 5 variantes concorrentes de padding no item. Canônico: `px-space-sm py-space-xs` com `gap-space-sm`.

### 1.3 Seletor de Safra (contexto global)

Componente de header presente em todo módulo de gestão. Exibe o contexto operacional vigente — ex. `Safra 2026/27 — Soja & Milho Safrinha`.

- Pílula `primary` com texto `on-primary` e ícone de acento.
- É um **combobox**, não um rótulo: trocar a safra recarrega o escopo de toda a tela.
- Obrigatório em qualquer tela cujo dado dependa de safra. Sem ele, o número na tela é ambíguo.

---

## 2. Dado

### 2.1 KPICard

O componente mais repetido do produto. Anatomia fixa:

1. **Label** — `badge-label`, uppercase, `tracking-wider`, `on-surface-variant`.
2. **Valor** — `display-lg`, `primary`, peso 700, com **unidade** em `body-md` `on-surface-variant` ao lado (nunca número nu).
3. **Delta** — badge no topo direito, com sinal, período e semáforo (`+4,2% sc/ha vs. safra anterior`).
4. **Sparkline** — opcional, SVG com `currentColor`.
5. **Rodapé** — chips de decomposição em `code-mono-sm`.

Container: superfície nível 1, `rounded-lg`, `p-space-md`, hairline `outline-variant`, sem sombra. Grid: `grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-gutter`.

Regra: **valor sempre mostra unidade e período**. Delta sem período de comparação é proibido.

### 2.2 DataTable (densa)

Componente central dos módulos financeiros e de compliance.

- **Cabeçalho:** superfície `surface-container`, `badge-label` uppercase `tracking-wider` `on-surface-variant`, borda inferior 1px `outline-variant`, sticky no scroll.
- **Linha:** altura canônica **40px** (`py-2.5`); hover eleva para `surface-container-low`. As referências têm 5 densidades diferentes — 40px é a de `DESIGN-*.md` e a escolhida.
- **Linha selecionada:** `border-l-4 border-primary` + fundo `primary-fixed/10`. Cor **e** borda, nunca só cor.
- **Célula numérica:** `text-right`, `tabular-nums`, `code-mono-sm`.
- **Célula de identificador técnico** (chave NF-e, CAR, coordenada): `code-mono-md`, clicável, abre Drawer de verificação.
- Obrigatórios: ordenação, filtro, paginação, exportação (`docs/DESIGN-UI.md`).
- Variante densidade compacta (`py-1`) permitida em DRE/demonstrativo, como opção do usuário — não como default divergente por tela.

### 2.3 StatusBadge

Único componente de estado. Substitui os dois dialetos concorrentes das referências.

- Pílula `rounded-full`, altura 22px, `px-space-sm`, tipografia `badge-label`.
- Conteúdo obrigatório: **ponto ou ícone + rótulo textual**. Cor sozinha é proibida.
- Variantes por token de `TOKENS.md` §2.3: `ok`, `warn`, `critical`, `unknown`.

| Variante | Exemplo de uso |
|---|---|
| `ok` | EUDR Conforme · CAR Validado · Sincronizado |
| `warn` | CAR Em Análise · DETER em apuração · Fila com atraso |
| `critical` | Embargo Ativo · Desmate pós-2020 · Crédito bloqueado |
| `unknown` | Sem cobertura · Não apurado · Fora de vigência |

A variante `unknown` não existe nas referências e é obrigatória: em compliance, "não sei" nunca pode renderizar como "ok".

### 2.4 Sparkline / Chart

Não há biblioteca nas referências — todos são SVG manual com **stroke hex literal**, o que os deixa presos ao tema claro.

Regra: gráfico usa `currentColor` ou variável CSS de token. Nenhum hex. Paleta de série derivada dos tokens, com diferenciação que não dependa só de matiz (traço/marcador), e legenda sempre presente.

---

## 3. Ação e entrada

### 3.1 Button

As referências **não têm um componente botão** — têm 6 aparências avulsas, uma delas hex hardcoded. Definir via shadcn `Button`:

| Variante | Aparência | Uso |
|---|---|---|
| `primary` | fundo `primary`, texto `on-primary` | **Uma por contexto.** Ação principal |
| `secondary` | superfície nível 1 + hairline `outline-variant`, texto `on-surface` | Ação de apoio |
| `ghost` | sem fundo, hover eleva superfície | Ação em linha, ícone-botão |
| `destructive` | fundo `error`, texto `on-error` | Embargo, congelamento, rejeição. **Sempre separada visualmente da primária** |

Alturas: `h-9` (36px) desktop — é o padrão de fato das referências e o de `DESIGN-*.md`. `h-11` (44px) mobile/campo. Ícone-botão quadrado: `size-8` desktop, `size-11` campo.

Feedback: hover em desktop; `active:scale-[0.98]` em campo (toque não tem hover).

### 3.2 Input / Select / Combobox

- Altura `h-9` desktop / `h-11` campo, `rounded`, hairline `outline-variant`, superfície `surface-container-low`, texto `on-surface`.
- Foco: anel `primary` visível — nunca `focus:outline-none` sem substituto.
- Máscara e validação obrigatórias em Data, R$, CPF, CNPJ, telefone, e-mail (`CLAUDE.md` §Convenções).
- Erro: mensagem textual junto do campo + `aria-invalid` + `aria-describedby`. Borda vermelha sozinha não basta.

### 3.3 Checkbox / Radio / Switch

As referências têm **4 definições concorrentes de checkbox**. Usar o shadcn `Checkbox` estilizado por token, uma definição só. Alvo mínimo 24px desktop / 44px campo, com área clicável incluindo o rótulo.

### 3.4 Tabs / SegmentedControl

**Zero `role="tab"` nas referências.** Usar shadcn `Tabs` (acessível por teclado: setas navegam, Home/End, `aria-selected`).

- `Tabs`: navegação entre seções de conteúdo, indicador `border-b-2 border-primary`.
- `SegmentedControl`: escolha de cenário/filtro mutuamente exclusivo (ex. cenário de simulação), pílula `primary` no item ativo.

---

## 4. Sobreposição

### 4.1 Drawer de auditoria (drill-down lateral)

Componente de assinatura do produto. Ancorado à direita, largura `540px` / `600px` (`w-full` em mobile), superfície nível 3.

Permite auditar polígono, imagem de satélite com data, árvore XML de NF-e e cadeia de custódia **sem perder o contexto do dashboard** — é isso que o justifica sobre um modal.

Requisitos: foco preso enquanto aberto, `Esc` fecha, foco retorna ao gatilho, `role="dialog"` + `aria-modal`, título associado.

Nota: `custo_margem_por_talh_o` chama de "drawer" um card inline. Não é. Drawer desliza e sobrepõe.

### 4.2 Modal

Reservado a decisão crítica e bloqueante: trava de não conformidade EUDR, assinatura de CPR, confirmação destrutiva.

Superfície nível 1 em `rounded-xl`, backdrop por **token** (as referências usam `bg-slate-900/60` hardcoded — dívida). Sem `max-height` arbitrário: altura pelo conteúdo, com limite relativo ao viewport e scroll interno.

Mesmos requisitos de foco/teclado do Drawer.

### 4.3 Toast

Existe em 1 tela de 14; precisa ser sistêmico. Canto inferior direito desktop, topo em campo.

- Variantes `info`, `warn`, `error`, `success`, com ícone + texto.
- **Só para evento transitório.** Erro persistente mora junto do objeto que falhou, nunca só no toast (`docs/DESIGN-UI.md`).
- `role="status"` (informativo) / `role="alert"` (erro). Nunca `alert()` nativo (`CLAUDE.md`).

---

## 5. Campo / mobile

### 5.1 BottomNav

5 itens, `h-20`, safe-area inferior, FAB central elevado para a ação de captura. Badge de pendência no item de sincronização (ponto `status-warn` + contagem acessível por texto).

### 5.2 SyncStatusHero

Card invertido (`primary` / `on-primary`) no topo da fila. Mostra: contagem de pendentes, estado da conexão por **ícone + cópia** (`wifi_off`, `cloud_off`), progresso, e prova de integridade textual ("gravado com hash SHA-256 e GPS imutável").

É o componente mais bem resolvido das referências — use-o como modelo de como comunicar estado de sistema sem depender de cor.

### 5.3 SyncQueueItem

Card em três faixas:
1. Ícone de tipo + título (`headline-sm`, truncado) + subtítulo + hash curto em chip `code-mono-sm`.
2. GPS **com precisão** + timestamp, em `code-mono-sm` `on-surface-variant`.
3. StatusBadge + ação "Auditar".

Regra: GPS sempre exibe precisão; rascunho é preservado; nada bloqueia nova captura.

### 5.4 Modo Sol Forte

Variante de alto contraste para leitura a céu aberto. Não é o tema escuro nem o claro — é um terceiro modo com contraste ampliado e alvos maiores. Precisa de par de tokens próprio quando for implementado.

---

## 6. Ausentes — criar

Não existem em nenhuma referência e são obrigatórios:

| Componente | Por quê |
|---|---|
| **EmptyState** | 0 ocorrências. Toda lista, tabela e mapa precisa de estado vazio com causa e próxima ação |
| **Skeleton / Loading** | Estado de carregamento não está desenhado |
| **OfflineBanner** | Estado offline e "sem permissão" exigidos por `DESIGN-UI.md`, ausentes no desktop |
| **PartialDataNotice** | Estado "parcial" — dado incompleto exibido com ressalva |
| **MapView** | Nenhum mapa real; as telas geo simulam com SVG. Precisa de legenda, fonte, **data** e cobertura (`DESIGN-UI.md`) |
| **Pagination** | Tabelas densas sem paginação desenhada |
| **StatusBadge `unknown`** | Quarto estado do semáforo |
| **PermissionDeniedState** | "Sem permissão" é estado de tela, não erro genérico |
