# DÉBITO das telas de referência

As telas em `docs/design/` foram geradas por ferramenta de design e **contêm divergências reais**. Este documento separa o que é sistema do que é acidente. Leia antes de portar markup de qualquer tela.

**Regra:** encontrou nesta lista → não copie, aplique a correção.

---

## 1. Descoberta estrutural

Para as 9 telas pareadas, `claro/X/code.html` e `escuro/X/code.html` são o **mesmo markup byte-a-byte**, diferindo apenas em `<html class="dark">` e nos valores hex do `tailwind.config`. Os nomes de token são idênticos.

Consequência: **o tema escuro é de graça — desde que a tela use só token.** As telas que quebraram essa regra são exatamente as que não têm par escuro. Isso não é coincidência, é a prova da regra.

---

## 2. Divergências — inventário e decisão

### P0 — quebram o sistema

| # | Divergência | Evidência | Decisão |
|---|---|---|---|
| 1 | **Cores hardcoded** `emerald-*` (189×), `amber-*` (36×), `slate-*` | `compliance_eudr_rastreabilidade`, `custo_margem_por_talh_o`, `safraos_gest_o_de_talh_es`, `safraos_painel_b2b`, `vis_o_geral_da_safra` — as 5 sem par escuro | Substituir por tokens `status-*`. Nenhum hex de paleta crua em produção |
| 2 | **`rounded-full` redefinido para `0.75rem`** no config, mas usado 240+ vezes como círculo (avatar, ponto de status, pílula, FAB) | todas as telas | `rounded-full` = `9999px`. Quem precisava de 12px é `rounded-xl` |
| 3 | **`tabular-nums`: 0 ocorrências** apesar de exigido por `DESIGN-CLARO.md` | todas | Obrigatório em todo valor comparável em coluna |
| 4 | **Semáforo usa `secondary`/`tertiary`** — `secondary` claro é `#436082`, azul-acinzentado. "Conforme" não lê como conforme | 11 telas tokenizadas | Família `status-*` própria (TOKENS §2.3) |
| 5 | **Quarto estado ausente** — não existe `inconclusivo` | todas | Criar `status-unknown`. Sem dado nunca renderiza como "ok" |
| 6 | **Acessibilidade quase nula** — `aria-label` 1×, `aria-current` 2×, zero `role="tab"`; os 13 `role=` são dado de negócio (`role="operador"`) | todas | Construir do zero via shadcn/ui. Não portar |
| 7 | **SVG com stroke hex literal** (`#6ffbbe`) — sparkline não muda com o tema | `safraos_onboarding_da_fazenda_f1` e demais | `currentColor` ou variável CSS |
| 8 | **Backdrop de modal `bg-slate-900/60`** hardcoded | `gest_o_de_fazendas_crud_geoespacial`, `safraos_gest_o_de_talh_es` | Token de backdrop |

### P1 — inconsistência sistemática

| # | Divergência | Evidência | Decisão |
|---|---|---|---|
| 9 | **Três escalas de fonte simultâneas**: tokens + `text-xs`/`text-sm` (300+) + `text-[11px]`/`text-[10px]` (240+) | todas | Só a escala de TOKENS §3.1. `text-[Npx]` apenas para glifo de ícone |
| 10 | **Cinco densidades de linha de tabela**: `py-1`, `p-2.5`, `py-2.5`, `p-3`, `py-3` | 9 telas com `<table>` | 40px canônico (`py-2.5`); compacta como opção do usuário |
| 11 | **Quatro arquétipos de header**, com `z-30`/`z-40`/`z-50` e `backdrop-blur-xl`/`-md`/ausente | todas | Dois: desktop (sidebar+header) e campo (header+bottom nav) |
| 12 | **Cinco variantes de NavItem** (padding e hover concorrentes) | 6 telas com sidebar | `px-space-sm py-space-xs`, hover eleva um nível |
| 13 | **Quatro definições de checkbox** | várias | Uma, via shadcn |
| 14 | **Seis aparências de botão**, uma hex (`bg-[#e6eff4] text-[#0c161c]`) | várias | 4 variantes de COMPONENTS §3.1 |
| 15 | **Escala nomeada misturada com a crua**: `p-space-md` ao lado de `p-5`/`p-6` no mesmo tipo de card | várias | Só a escala nomeada |
| 16 | **Borda de header `border-b-[#e6eff4]`** | 4 telas | `outline-variant` |
| 17 | **Dois dialetos de badge** — mesmo dentro do tokenizado: `rounded`+`px-2.5 py-1` vs `rounded-full`+`px-2 py-0.5`, `font-semibold` vs `font-bold` | todas | StatusBadge único |
| 18 | **`max-h` arbitrário em modal**: `max-h-[921px]`, `[942px]`, `[870px]` | telas com modal | Altura pelo conteúdo, limite relativo ao viewport |

### P2 — ruído de geração

| # | Divergência | Decisão |
|---|---|---|
| 19 | `shadow-xs` — classe inexistente no Tailwind 3, renderiza nada (`custo_margem_por_talh_o`) | Remover |
| 20 | Plugins Tailwind inconsistentes: só `vis_o_geral_da_safra` carrega `?plugins=forms`, mas outras usam `form-input` | Config única no projeto |
| 21 | Material Symbols carregado 2× em vários arquivos, com axis diferentes | Um `<link>` |
| 22 | Pesos de fonte divergentes por tela; `font-bold` sobre peso não carregado → bold sintético | Um subset único |
| 23 | `custo_margem_por_talh_o` chama de "drawer" (`id="import-drawer"`) um card inline | Nomenclatura: drawer desliza e sobrepõe |
| 24 | Token `font-body` praticamente morto (1×) | Remover da escala |
| 25 | `body { min-height: max(884px,100dvh) }` só no par escuro de `safraos_campo_app_offline_first` | Artefato de captura. Descartar |

---

## 3. Ausências

Não existem em nenhuma tela e são obrigatórios: **EmptyState** (0 ocorrências de "nenhum"/"sem resultado"), **Skeleton/Loading**, **OfflineBanner desktop**, **PartialDataNotice**, **MapView real** (as telas geo simulam com SVG absoluto), **Pagination**, **PermissionDeniedState**, **StatusBadge `unknown`**, **Tabs acessível**, **Button como componente**.

Toast existe em 1 tela de 14 — precisa virar sistêmico.

---

## 4. O que aproveitar

O núcleo é bom. Reaproveite direto:

- **Conjunto de tokens M3 completo** com par claro/escuro e nomes idênticos — é o que faz o dark funcionar.
- **Escala tipográfica de 11 níveis** com as três famílias bem repartidas por função.
- **SyncQueueItem** e **SyncStatusHero** (`safraos_campo_fila_de_sincroniza_o`) — os componentes mais bem resolvidos do conjunto; modelo de como comunicar estado sem depender de cor.
- **BottomNav com FAB e badge de pendência** (`safraos_campo_app_offline_first`).
- **Linha de tabela com hover + borda esquerda na seleção** — cor *e* forma.
- **Anatomia do KPICard** (label uppercase → valor+unidade → delta → sparkline → chips mono).
- **Subsistema de campo**: viewport travado, safe areas, `tap-highlight` transparente, alvos 44px, `active:scale`.
- **Drawer de auditoria** de `safraos_usu_rios_rbac` — o padrão de drill-down sem perder contexto.

---

## 5. Ao portar uma tela

1. Confira a tela nesta lista.
2. Troque todo hex por token; se não houver token, proponha (com par claro/escuro).
3. Troque a escala de fonte pela canônica.
4. Aplique a densidade de tabela canônica.
5. Reconstrua o componente via shadcn/ui — não copie o markup.
6. Adicione os estados ausentes (vazio, loading, offline, parcial, sem permissão, inconclusivo).
7. Construa a acessibilidade do zero.
8. Prove nos dois temas (`PATTERNS.md` §12).
