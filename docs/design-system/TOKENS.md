# TOKENS — SafraOS Design System

Fonte: frontmatter de `docs/design/DESIGN-CLARO.md` e `docs/design/DESIGN-ESCURO.md`, confirmado contra o `tailwind.config` embutido nas 14 telas de referência. Os nomes de token são **idênticos** nos dois temas; só os valores mudam. Essa é a propriedade que faz o tema escuro funcionar sem markup paralelo — preserve-a.

## 1. Regra de uso

- Feature nunca escreve hex. Escreve nome de token.
- Token novo só nasce com par claro/escuro definido no mesmo commit.
- Se um valor não tem token, ou você usa o token aproximado, ou propõe token novo. Não existe terceira via.
- SVG (sparkline, mapa, ícone customizado) usa `currentColor` ou variável CSS, **nunca** stroke/fill hex literal — senão o gráfico não acompanha o tema.

## 2. Cor — paleta canônica

Sistema Material 3. Papel de cada família no SafraOS:

| Família | Papel no produto |
|---|---|
| `primary` | Ação institucional, navegação de topo, marca, KPI principal |
| `secondary` | Estado **conforme/concluído/positivo**, saúde de ativo |
| `tertiary` | Estado **pendente/atenção**, índices de mercado |
| `error` | Estado **crítico/bloqueio**, embargo, ação destrutiva |
| `surface-*` | Elevação por container, não por sombra |
| `outline` / `outline-variant` | Hairline estrutural de célula, card e divisor |

### 2.1 Tema claro

```
surface                     #f8f9ff      on-surface                  #181c21
surface-dim                 #d8dae2      on-surface-variant          #404752
surface-bright              #f8f9ff      inverse-surface             #2d3137
surface-container-lowest    #ffffff      inverse-on-surface          #eef0f8
surface-container-low       #f1f3fb      outline                     #707883
surface-container           #eceef6      outline-variant             #bfc7d3
surface-container-high      #e6e8f0      surface-variant             #e0e2ea
surface-container-highest   #e0e2ea      surface-tint                #0061a2
background                  #f8f9ff      on-background               #181c21

primary                     #005f9e      on-primary                  #ffffff
primary-container           #0078c6      on-primary-container        #fdfcff
inverse-primary             #9dcaff
secondary                   #436082      on-secondary                #ffffff
secondary-container         #b9d7fe      on-secondary-container      #405d7f
tertiary                    #904900      on-tertiary                 #ffffff
tertiary-container          #b55d00      on-tertiary-container       #fffbff
error                       #ba1a1a      on-error                    #ffffff
error-container             #ffdad6      on-error-container          #93000a

primary-fixed               #d1e4ff      on-primary-fixed            #001d35
primary-fixed-dim           #9dcaff      on-primary-fixed-variant    #00497c
secondary-fixed             #d1e4ff      on-secondary-fixed          #001d36
secondary-fixed-dim         #abc9f0      on-secondary-fixed-variant  #2b4969
tertiary-fixed              #ffdcc5      on-tertiary-fixed           #301400
tertiary-fixed-dim          #ffb783      on-tertiary-fixed-variant   #703700
```

### 2.2 Tema escuro

```
surface                     #101419      on-surface                  #e0e2ea
surface-dim                 #101419      on-surface-variant          #bfc7d3
surface-bright              #36393f      inverse-surface             #e0e2ea
surface-container-lowest    #0b0e14      inverse-on-surface          #2d3137
surface-container-low       #181c21      outline                     #8a919d
surface-container           #1c2025      outline-variant             #404752
surface-container-high      #272a30      surface-variant             #32353b
surface-container-highest   #32353b      surface-tint                #9dcaff
background                  #101419      on-background               #e0e2ea

primary                     #9dcaff      on-primary                  #003257
primary-container           #2d95eb      on-primary-container        #002b4c
inverse-primary             #0061a2
secondary                   #abc9f0      on-secondary                #113251
secondary-container         #2d4b6b      on-secondary-container      #9dbbe1
tertiary                    #ffb783      on-tertiary                 #4f2500
tertiary-container          #db7619      on-tertiary-container       #452000
error                       #ffb4ab      on-error                    #690005
error-container             #93000a      on-error-container          #ffdad6
```

Os tokens `*-fixed*` têm o **mesmo valor nos dois temas** — é a propriedade deles. Use-os quando o elemento precisa manter a mesma cor independente do tema (marca sobre superfície invertida, hero de status).

### 2.3 Semáforo regulatório — decisão obrigatória

Há um conflito real entre a direção escrita e a implementação:

- `DESIGN-CLARO.md` §Colors prescreve verde `#059669` / âmbar `#D97706` / vermelho `#DC2626`.
- As 11 telas tokenizadas usam `secondary` / `tertiary` / `error` — e `secondary` claro é `#436082`, **azul-acinzentado, não verde**.
- As 5 telas que usaram `emerald-*` / `amber-*` direto são exatamente as que não têm tema escuro.

**Decisão:** o semáforo é um eixo semântico próprio, com token próprio, e **não** reaproveita `secondary`/`tertiary`. Criar a família abaixo, com par claro/escuro, e usá-la exclusivamente para conformidade regulatória e estado operacional:

| Token | Significado | Claro | Escuro |
|---|---|---|---|
| `status-ok` | EUDR conforme, CAR validado, sincronizado | `#059669` | `#34d399` |
| `status-ok-container` | fundo do badge | `#ecfdf5` | `rgba(5,150,105,.15)` |
| `on-status-ok-container` | texto do badge | `#065f46` | `#34d399` |
| `status-warn` | DETER em análise, CAR pendente, fila com atraso | `#d97706` | `#fbbf24` |
| `status-warn-container` | | `#fffbeb` | `rgba(217,119,6,.15)` |
| `on-status-warn-container` | | `#92400e` | `#fbbf24` |
| `status-critical` | embargo ativo, desmate pós-2020, crédito bloqueado | `#dc2626` | `#f87171` |
| `status-critical-container` | | `#fef2f2` | `rgba(220,38,38,.15)` |
| `on-status-critical-container` | | `#991b1b` | `#f87171` |
| `status-unknown` | **inconclusivo** — sem dado, fora de cobertura, não apurado | `#707883` (`outline`) | `#8a919d` |
| `status-unknown-container` | | `#eceef6` | `#1c2025` |

`status-unknown` é exigência de `docs/DESIGN-UI.md` (semáforo tem quatro estados, não três) e **não existe em nenhuma tela de referência**. É criação obrigatória: sem ele, ausência de dado vira falso "ok" ou falso "crítico" — o pior defeito possível num produto de compliance.

`error` (M3) continua existindo e é coisa diferente: é **erro de sistema/validação** (campo inválido, falha de requisição). `status-critical` é **estado do mundo** (a fazenda está embargada). Não misture: um é bug, o outro é fato regulatório.

## 3. Tipografia

Três famílias, carregadas com subset e `display=swap`:

| Família | Papel |
|---|---|
| **Inter** | Interface, corpo, células de tabela, labels |
| **Plus Jakarta Sans** | Títulos, números de KPI, identidade |
| **JetBrains Mono** | Precisão auditável: chave NF-e 44 dígitos, CAR, coordenadas WGS84, hash CPR, códigos de talhão, **todo número em coluna** |

Pesos a carregar (união do que as telas usam — padronize em um só `<link>`): Inter 400;500;600;700 · Plus Jakarta Sans 500;600;700;800 · JetBrains Mono 400;500;600. Não aplique `font-bold` sobre um peso não carregado: o browser sintetiza e o resultado é sujo.

### 3.1 Escala

| Token | Família | Size/LH | Peso | Tracking | Uso |
|---|---|---|---|---|---|
| `display-lg` | Plus Jakarta Sans | 32/40 | 700 | -0.02em | Número de KPI, título de página |
| `headline-lg` | Plus Jakarta Sans | 24/32 | 600 | -0.015em | Título de seção |
| `headline-md` | Plus Jakarta Sans | 20/28 | 600 | -0.01em | Título de card analítico |
| `headline-sm` | Plus Jakarta Sans | 16/24 | 600 | -0.005em | Título de item, linha de destaque |
| `body-lg` | Inter | 16/24 | 400 | — | Texto de leitura, onboarding |
| `body-md` | Inter | 14/20 | 400 | — | Corpo padrão |
| `body-sm` | Inter | 12/16 | 400 | — | Metadado, auxiliar |
| `data-dense` | Inter | 13/16 | 500 | — | Célula de tabela textual |
| `code-mono-md` | JetBrains Mono | 13/18 | 500 | -0.01em | Chave NF-e, CAR, coordenada |
| `code-mono-sm` | JetBrains Mono | 11/14 | 500 | 0 | Valor numérico em coluna, chip de código |
| `badge-label` | Inter | 11/14 | 600 | 0.02em | Badge, cabeçalho de coluna (uppercase) |

**Escala fechada.** As telas de referência misturam três escalas simultâneas (token semântico + `text-xs`/`text-sm` + `text-[11px]`). Em produção só a coluna Token é válida. Exceção única: `text-[Npx]` para dimensionar glifo de ícone, que não é texto.

### 3.2 Numeração tabular — obrigatória

`tabular-nums` **não aparece em nenhuma tela de referência** (0 ocorrências), contrariando o que `DESIGN-CLARO.md` §Tabular Alignment Rules exige. As telas se salvam parcialmente porque JetBrains Mono já é monoespaçada — mas todo número que cai em `data-dense` (Inter) fica desalinhado.

Regra: **todo valor numérico comparável em coluna** (R$, ha, sc/ha, @, %, data) recebe `font-variant-numeric: tabular-nums` e `text-right`, independente da família. Aplique como utilitário base na célula numérica, não caso a caso.

## 4. Espaçamento

```
space-xs   0.25rem    space-lg   1.25rem    gutter   1rem
space-sm   0.5rem     space-xl   1.75rem    margin   1.5rem
space-md   0.75rem
```

Viés do sistema é **empacotamento compacto**: `space-sm` para padding interno de componente, `space-md` para respiro entre linhas, `gutter` entre cards. Densidade é requisito funcional (ver `PATTERNS.md` §Densidade), não preferência estética.

Proibido misturar a escala nomeada com a escala crua do Tailwind no mesmo componente (`p-space-md` ao lado de `p-5` é o defeito mais comum das telas de referência).

## 5. Raio — corrigido

O `tailwind.config` das telas redefine a escala de forma que **quebra**: `full: 0.75rem`. O markup usa `rounded-full` 240+ vezes esperando círculo — avatares, pontos de status, pílulas. Com 12px, um avatar de 32px vira quadrado arredondado.

Escala canônica (a de `DESIGN-*.md`, que está correta):

```
rounded-sm       0.125rem   chip inline, pill de coordenada
rounded          0.25rem    botão, input, linha de tabela, badge retangular
rounded-md       0.375rem   uso pontual
rounded-lg       0.5rem     card analítico, módulo, widget de mapa
rounded-xl       0.75rem    modal, drawer, seletor de safra
rounded-full     9999px     avatar, ponto de status, pílula, FAB
```

`rounded-full` é círculo/pílula. Sempre. Se um elemento precisava de 12px, ele é `rounded-xl`.

## 6. Elevação

O sistema evita sombra flutuante. Hierarquia vem de **container de superfície + hairline**, o que mantém grade densa legível em tela de campo sob sol e em monitor de mesa de operação.

| Nível | Claro | Escuro | Uso |
|---|---|---|---|
| 0 — canvas | `background` | `background` | Plano de fundo da app |
| 1 — superfície | `surface-container-lowest` + 1px `outline-variant`, **sem sombra** | idem | Card, tabela, painel |
| 2 — flyout/hover | `surface-container-low` + sombra técnica baixa | idem | Popover, hover elevado |
| 3 — drawer/sticky | `surface-container-lowest` + sombra ambiente lateral | idem | Drawer de auditoria, barra fixa |
| 4 — modal crítico | superfície nível 1 + backdrop | idem | Trava EUDR, assinatura CPR |

Backdrop de modal usa token (`inverse-surface` com alfa, ou variável dedicada). Nas telas de referência é `bg-slate-900/60` hardcoded — dívida, ver `DEBITO.md`.

## 7. Implementação — shadcn/ui

shadcn/ui consome variáveis CSS semânticas próprias. Mapeie os tokens SafraOS para elas em `globals.css`, com bloco `:root` (claro) e `.dark` (escuro), e mantenha **os tokens SafraOS como fonte** — a camada shadcn é derivada, nunca o contrário.

Mapeamento base:

| shadcn | SafraOS |
|---|---|
| `--background` / `--foreground` | `background` / `on-background` |
| `--card` / `--card-foreground` | `surface-container-lowest` / `on-surface` |
| `--popover` / `--popover-foreground` | `surface-container-low` / `on-surface` |
| `--primary` / `--primary-foreground` | `primary` / `on-primary` |
| `--secondary` / `--secondary-foreground` | `secondary-container` / `on-secondary-container` |
| `--muted` / `--muted-foreground` | `surface-container` / `on-surface-variant` |
| `--accent` / `--accent-foreground` | `surface-container-high` / `on-surface` |
| `--destructive` / `--destructive-foreground` | `error` / `on-error` |
| `--border` | `outline-variant` |
| `--input` | `outline-variant` |
| `--ring` | `primary` |
| `--radius` | `0.25rem` |

Os tokens sem equivalente shadcn (`tertiary*`, `status-*`, `*-fixed*`, escala `surface-container-*` completa) ficam como variáveis SafraOS próprias e são consumidos direto pelas variantes dos componentes.

Alternância de tema por `class="dark"` no `<html>` (é o que as telas de referência já fazem, `darkMode: "class"`). Persistir preferência e respeitar `prefers-color-scheme` na primeira visita.
