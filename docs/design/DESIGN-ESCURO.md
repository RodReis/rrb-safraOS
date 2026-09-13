---
name: Agro-Fintech Institutional
colors:
  surface: '#101419'
  surface-dim: '#101419'
  surface-bright: '#36393f'
  surface-container-lowest: '#0b0e14'
  surface-container-low: '#181c21'
  surface-container: '#1c2025'
  surface-container-high: '#272a30'
  surface-container-highest: '#32353b'
  on-surface: '#e0e2ea'
  on-surface-variant: '#bfc7d3'
  inverse-surface: '#e0e2ea'
  inverse-on-surface: '#2d3137'
  outline: '#8a919d'
  outline-variant: '#404752'
  surface-tint: '#9dcaff'
  primary: '#9dcaff'
  on-primary: '#003257'
  primary-container: '#2d95eb'
  on-primary-container: '#002b4c'
  inverse-primary: '#0061a2'
  secondary: '#abc9f0'
  on-secondary: '#113251'
  secondary-container: '#2d4b6b'
  on-secondary-container: '#9dbbe1'
  tertiary: '#ffb783'
  on-tertiary: '#4f2500'
  tertiary-container: '#db7619'
  on-tertiary-container: '#452000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d1e4ff'
  primary-fixed-dim: '#9dcaff'
  on-primary-fixed: '#001d35'
  on-primary-fixed-variant: '#00497c'
  secondary-fixed: '#d1e4ff'
  secondary-fixed-dim: '#abc9f0'
  on-secondary-fixed: '#001d36'
  on-secondary-fixed-variant: '#2b4969'
  tertiary-fixed: '#ffdcc5'
  tertiary-fixed-dim: '#ffb783'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#703700'
  background: '#101419'
  on-background: '#e0e2ea'
  surface-variant: '#32353b'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  data-dense:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
  code-mono-md:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  code-mono-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0em
  badge-label:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.02em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  margin: 1.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 1.75rem
---

## Brand & Style

The design system embodies the rigor of institutional fintech merged with the environmental scale of modern precision agriculture. It projects unwavering authority, high-density data legibility, and audit-grade regulatory compliance. Tailored for commodity traders, agricultural credit risk desks, farm conglomerate CFOs, and ESG compliance officers, the interface communicates reliability and institutional competence without superfluous decorative distraction.

The visual style blends **Corporate / Modern** precision with **Tactile Data Density**:
- **Information Architecture:** Compact, modular data grids, clear information hierarchy, and zero wasted vertical space.
- **Atmosphere:** Deep sovereign sky-blue tones balanced by clinical slate neutrals, evoking both the breadth of agribusiness production and the analytical security of core banking platforms.
- **Audit Rigor:** Specialized visual treatment for high-stakes regulatory verifications (EUDR deforestation compliance, CAR statuses, SIGEF land titles, and Ibama embargoes).

## Colors

The palette balances clean agronomic blue with surgical fintech neutrals, anchored by a strict regulatory traffic-light taxonomy.

### Core Swatches
- **Primary (`#0285da`):** Sovereign Sky Blue. Represents institutional permanence, primary actions, top-level navigation, and master brand framing.
- **Secondary (`#5c799c`):** Muted Steel. Used for positive financial deltas, completed operations, and active asset health.
- **Tertiary (`#c76702`):** Harvest Amber / Maize. Reserved for financial pending states, attention notices, and market commodity indexes.
- **Neutral Primary (`#74777e`):** Muted Slate Ink. High-contrast typography and critical data readouts.

### Regulatory & Compliance Semaphores
- **Compliance Compliant (`#059669`):** EUDR certified zero-deforestation, CAR validated, active non-embargo certification.
- **Compliance Warning (`#D97706`):** DETER alert in analysis, overlapping buffer zone, CAR pending review.
- **Compliance Critical (`#DC2626`):** Post-2020 deforestation vector detected, active Ibama/ICMBio embargo, blocked credit issuance.

### Surfaces & Boundaries
- **App Background:** `#12161c` (Dark Mode Canvas) - Neutral low-strain dark canvas.
- **Surface Elevation 0:** `#181c21` (Deep Surface) - Crisp card backgrounds and table lines.
- **Structural Borders:** `#2d3137` (Dark Mode Border) - Hairline dividers maintaining strict cell boundaries.
- **Muted Text:** `#94a3b8` (Slate 400) - Metadata, secondary metrics, and column descriptors.

## Typography

The typographic hierarchy solves for two demands: executive clarity and uncompromising technical accuracy.

- **Primary Interface & Numerics (`Inter`):** Selected for numerical balance, tabular lining figures (`tnum`), and effortless scanning across large financial tables and ledger sheets.
- **Headers & Identity (`Plus Jakarta Sans`):** Provides structured geometric authority for analytical card headers, module titles, and crop selector modals.
- **Audit & Cryptographic Precision (`JetBrains Mono`):** Dedicated to technical strings where zero character confusion is mandatory: 44-digit NF-e access keys, Brazilian CAR registration numbers, WGS84 polygon coordinates, CPR hashes, and blockchain audit trails.

### Tabular Alignment Rules
All numerical data columns (credit amounts, yields in sc/ha, hedged volumes, and compliance dates) must use `font-variant-numeric: tabular-nums` to enable immediate vertical scanning.

## Layout & Spacing

The layout utilizes an enterprise 12-column fluid grid system engineered for high-density operations, operational dashboards, and split-screen geospatial analysis.

### Grid & Breakpoints
- **Desktop (>= 1440px):** 12 columns, `1.5rem` margins, `1rem` gutters. Accommodates simultaneous map/table workspaces and lateral drill-down drawers.
- **Laptop (1024px - 1439px):** 12 columns, `1.25rem` margins, `0.75rem` gutters. Density remains compact; side panels become collapsible overlay drawers.
- **Tablet / Field Terminals (768px - 1023px):** 8 columns, `1rem` margins, `0.5rem` gutters. Multi-column metric groups collapse to 2x2 cards.
- **Mobile Handheld (< 768px):** 4 columns, `0.75rem` margins, `0.5rem` gutters. Strictly prioritizes status check lists, approvals, and alert feeds.

### Layout Rhythms
Spacing is biased toward compact packing (`space-sm` for component internal padding, `space-md` for row spacing) to maximize the visible volume of ledger items and plot polygon lists without requiring continuous scrolling.

## Elevation & Depth

This design system deliberately eschews excessive floating drop shadows in favor of a **structured hairline border and low-contrast surface container** methodology, optimized for dark mode. This keeps dense grids legible under field laptops and bright trading desk screens.

### Elevation Levels
- **Level 0 (App Canvas):** `#12161c`. Unbacked base dark plane.
- **Level 1 (Operational Surface):** `#181c21` card, table, and panel surface encased in a crisp 1px hairline border of `#2d3137`. No shadow.
- **Level 2 (Interactive Flyouts & Hover):** `#1f242c` with a subtle technical drop: `0px 2px 4px -1px rgba(0, 0, 0, 0.3), 0px 4px 6px -1px rgba(0, 0, 0, 0.2)` and `#383f4a` border.
- **Level 3 (Audit Drawers & Filter Bars):** Fixed lateral drawers and sticky header bars. Background `#181c21` with ambient left-drop `0px 10px 25px -5px rgba(0, 0, 0, 0.5)`.
- **Level 4 (Critical Incident Modals):** Central dialogs (e.g., EUDR Non-Compliance Lock, CPR Signature block). Dark overlay backdrop `rgba(0, 0, 0, 0.8)` with card shadow `0px 20px 25px -5px rgba(0, 0, 0, 0.6)`.

## Shapes

The design system employs **Soft (`1`)** roundedness. Curvature is intentionally subtle and architectural:

- **Component Corners (`rounded-sm` / `0.25rem`):** Buttons, inputs, inline status chips, table rows, and geospatial coordinate pills.
- **Card Containers (`rounded-lg` / `0.5rem`):** Analytical dashboard cards, regulatory summary modules, and map widget frames.
- **Dialogs & Drawers (`rounded-xl` / `0.75rem`):** Audit modals and top-level harvest switchers.

This low-radius language prevents wasted space at column corners and reinforces the precision instrument feel required by financial risk and regulatory inspectors.

## Components

### Buttons
- **Primary:** Background `#0285da`, text `#FFFFFF`, radius `0.25rem`, height `36px` (desktop compact). Hover: `#0271bc`. Focus: 2px ring `#5c799c`.
- **Secondary / Technical:** Background `#181c21`, border `1px solid #2d3137`, text `#74777e`. Hover: `#232830`.
- **Critical Regulatory:** Background `#DC2626`, text `#FFFFFF`. Reserved strictly for embargo actions, credit freezes, or rejecting environmental manifests.

### Data Tables (High-Density)
- Row height fixed at `40px`. Alternating rows maintain subtle hover tone `#1f242c`.
- Top header: Uppercase `Inter` 11px font, tracking `0.05em`, color `#94a3b8`, background `#12161c`, bottom border `1px solid #2d3137`.
- Direct integration with monospaced hashes for CAR and NF-e cells, clickable to reveal lateral verification drawers.

### Regulatory Compliance Badges
- **Pill format:** Height `22px`, horizontal padding `8px`, typography `badge-label`.
- **EUDR Conforme:** Background `rgba(5, 150, 105, 0.15)`, text `#34d399`, border `1px solid rgba(5, 150, 105, 0.3)`, dot indicator `#059669`.
- **CAR Em Análise:** Background `rgba(217, 119, 6, 0.15)`, text `#fbbf24`, border `1px solid rgba(217, 119, 6, 0.3)`, dot indicator `#D97706`.
- **Embargo Ativo:** Background `rgba(220, 38, 38, 0.15)`, text `#f87171`, border `1px solid rgba(220, 38, 38, 0.3)`, dot indicator `#DC2626`.

### Inputs & Filters
- **Text & Dropdowns:** Height `36px`, font `13px`, border `1px solid #2d3137`, background `#181c21`, text `#eef0f8`. Active border `#0285da`.
- **Crop Season Selector (Global Header Component):** Embedded segmented control or combobox displaying current operational context (e.g., `Safra 2026/27 — Soja & Milho Safrinha`). Styled with `#0285da` pill container, white text, and golden icon accent (`#F59E0B`).

### KPI Cards with Sparklines
- Enclosed in `0.5rem` border `#2d3137`. Features primary metric in `Plus Jakarta Sans` 24px bold, with an adjacent micro-chart (sparkline) showing 7-day grain price trend or biomass vegetation index (NDVI).
- Status delta tag located at top right corner (`+4.2% sc/ha` in `#059669`).

### Lateral Drill-down Drawers
- Right-anchored sheet (width: `480px` or `640px`) used to audit specific farm polygons, view satellite imagery timestamps, inspect NF-e electronic xml trees, and review environmental chain-of-custody without losing dashboard context.