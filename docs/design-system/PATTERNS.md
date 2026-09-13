# PATTERNS — SafraOS Design System

Regras transversais: layout, densidade, estados, dado, acessibilidade e campo. O que vale em toda tela, independente do componente.

---

## 1. Grid e breakpoints

Grade fluida de 12 colunas, dimensionada para operação densa e para análise geoespacial em tela dividida.

| Faixa | Colunas | Margem | Gutter | Comportamento |
|---|---|---|---|---|
| Desktop ≥1440px | 12 | `margin` (1.5rem) | `gutter` (1rem) | Mapa + tabela simultâneos; drawer lateral |
| Laptop 1024–1439px | 12 | 1.25rem | `space-md` | Painéis laterais viram overlay |
| Tablet/terminal 768–1023px | 8 | `gutter` | `space-sm` | Grupos de métrica colapsam 2×2 |
| Campo <768px | 4 | `space-md` | `space-sm` | Só checklists, aprovações e alertas |

Conteúdo tem largura máxima (~1400px) e centraliza; a densidade não cresce indefinidamente com o monitor.

## 2. Densidade

Densidade é requisito, não gosto: o usuário compara dezenas de talhões, lançamentos e polígonos. Espaço vertical desperdiçado custa scroll e custa decisão.

- Padding interno de componente: `space-sm`.
- Respiro entre linhas: `space-md`.
- Entre cards: `gutter`.
- Entre seções: `space-lg` / `space-xl`.

Nunca use a escala crua do Tailwind junto da escala nomeada no mesmo componente.

## 3. Hierarquia de conteúdo

Ordem fixa em toda tela analítica:

**Contexto** (safra, fazenda, período) → **Resumo** (KPIs) → **Evidência** (tabela/mapa) → **Histórico/auditoria** (drawer).

Regras:
- **Uma ação primária por contexto.** Ação destrutiva fica visualmente separada, nunca adjacente à primária.
- Todo valor exibe **unidade e período**. `R$ 1.240` não é informação; `R$ 1.240/ha · safra 2026/27` é.
- Toda métrica derivada expõe como foi calculada — via tooltip ou drawer. Em compliance e crédito, número sem procedência não sustenta decisão.

## 4. Estados de tela — os oito

Toda superfície que carrega dado desenha os oito. Faltar um é defeito, não omissão.

| Estado | Regra |
|---|---|
| **Loading** | Skeleton com a forma do conteúdo real. Nunca spinner sozinho em tela cheia |
| **Vazio** | Causa + próxima ação. Nunca só "Nenhum resultado" |
| **Parcial** | Dado incompleto **é exibido** com ressalva explícita do que falta e por quê |
| **Offline** | Estado visível e persistente; nunca bloqueia captura em campo |
| **Erro recuperável** | Mensagem junto do objeto + ação de retentativa. Toast só como aviso transitório |
| **Sem permissão** | Estado próprio, explicando o que falta. Nunca erro genérico nem tela em branco |
| **Sucesso** | Confirmação transitória + estado do objeto atualizado |
| **Inconclusivo** | Compliance sem dado ou fora de cobertura → `status-unknown`. **Nunca** cai em "ok" |

## 5. Semáforo regulatório

Quatro estados: `ok`, `warn`, `critical`, `unknown` (tokens em [TOKENS.md](TOKENS.md) §2.3).

Regras invioláveis:
1. **Cor nunca é o único sinal.** Sempre cor + ícone + rótulo textual.
2. Semáforo diz **estado do mundo** (a fazenda está embargada). Erro de sistema usa `error`, que é outra coisa (a requisição falhou).
3. Todo estado de compliance exibe **fonte e data da apuração**. "Conforme" sem data não é conforme — é conforme *quando foi checado*.
4. Ausência de dado é `unknown`, sempre. Um falso "ok" em EUDR trava um navio.

## 6. Dado numérico

- `tabular-nums` em todo valor comparável em coluna, sempre, qualquer família.
- Alinhamento à direita para número; à esquerda para texto.
- **Proibido float para dinheiro** (`CLAUDE.md`). A UI formata a partir de decimal/inteiro em centavos.
- Formatação PT-BR: `1.234,56` · `R$` · `ha` · `sc/ha` · `@` · `%` · data `dd/mm/aaaa`.
- Sinal explícito em delta (`+` / `−`), com período de comparação.
- Identificador técnico (chave NF-e 44 dígitos, CAR, WGS84, hash) em JetBrains Mono, com agrupamento legível e ação de copiar.

## 7. Geoespacial

Todo mapa exibe, sem exceção: **legenda, fonte, data de referência e cobertura** (`docs/DESIGN-UI.md`).

- Polígono nunca comunica estado só por preenchimento colorido: use padrão/contorno junto.
- Sobreposição (embargo, TI, PRODES) é camada nomeada, alternável, com fonte própria e data.
- Área fora de cobertura da base é `unknown` visível, não vazio silencioso.
- Coordenada em mono, com datum explícito.

## 8. Acessibilidade

Estado atual das referências: `aria-label` 1 ocorrência no repositório inteiro, `aria-current` 2, zero `role="tab"`. **Base próxima de zero — construir do zero, não portar.**

Mínimo obrigatório:
- Contraste AA: 4.5:1 texto normal, 3:1 texto grande e elemento gráfico portador de informação. Verificado nos **dois** temas.
- Navegação completa por teclado; foco sempre visível; `focus:outline-none` só com anel substituto.
- Drawer e modal: foco preso, `Esc` fecha, foco retorna ao gatilho.
- Nav ativa com `aria-current="page"`; tabs com semântica ARIA real.
- Toast `role="status"` / `role="alert"`.
- Ícone sem rótulo visível precisa de nome acessível; ícone decorativo é `aria-hidden`.
- Rótulo associado a todo campo; erro por `aria-describedby` + `aria-invalid`.
- Zoom até 200% sem perda de conteúdo ou função.
- Respeitar `prefers-reduced-motion` — inclusive no `animate-spin` do estado de sincronização.

## 9. Campo / mobile

Contexto real: sol forte, luva, uma mão, sem sinal.

- Alvo mínimo **44×44px**; nunca depender de hover.
- Feedback tátil no toque (`active:scale`).
- Safe areas respeitadas em header e nav.
- Rede, fila e **última sincronização** sempre visíveis — e nunca bloqueando a captura.
- GPS mostra **precisão**, não só coordenada.
- Rascunho preservado sempre; perder registro feito no campo é inaceitável.
- PT-BR simples e direto; áudio é alternativa legítima de entrada, não recurso secundário.

## 10. Movimento

Funcional apenas: transição de estado, entrada de drawer/modal, feedback de toque. 150–300ms, curva de saída. Sem movimento decorativo. Sem animação em dado — número não desliza nem conta.

## 11. Idioma

Interface em **PT-BR**; código e identificadores em **inglês** (`CLAUDE.md`). Termo de domínio em PT-BR e correto: talhão, safra, insumo, sacas, arroba, CAR, LCDPR, CPR, EUDR. Rótulo genérico de ferramenta de design ("Card", "Item") não sobrevive à implementação.

## 12. Prova visual obrigatória

Antes de marcar qualquer tela como pronta (`docs/DESIGN-UI.md`, `docs/TESTING.md`):

- [ ] Desktop, tablet e mobile
- [ ] **Tema claro e escuro** — os dois, na mesma tela
- [ ] Navegação por teclado completa
- [ ] Contraste verificado nos dois temas
- [ ] Zoom 200%
- [ ] Estados: vazio, parcial, offline, erro, sem permissão, inconclusivo
- [ ] Dados longos (nome de fazenda extenso, 44 dígitos, valores grandes) sem quebra
- [ ] Formatação de moeda, área e data em PT-BR
- [ ] Screenshot comparativa anexada à PR

A ferramenta de design propõe. **PRD, acessibilidade e tokens limitam.**
