# DESIGN-SYSTEM SafraOS — instruções de construção

**Natureza deste conjunto:** instrução de construção do design system, derivada da evidência em `docs/design/`. Não é contrato de produto. Onde divergir do PRD, **o PRD vence**. Onde divergir de `docs/DESIGN-UI.md`, a direção do PI vence e o documento é corrigido aqui.

**Autoridade da fonte.** As telas em `docs/design/claro/*/code.html` e `docs/design/escuro/*/code.html` são *referência visual*, não código de produção. Elas foram geradas por ferramenta de design e contêm divergências reais entre si. Este conjunto separa o que é **sistema** (regra) do que é **acidente da geração** (dívida a corrigir). Copiar markup dessas telas sem passar por este filtro reintroduz a dívida.

## Os documentos

| Documento | O que resolve |
|---|---|
| [TOKENS.md](TOKENS.md) | Tokens de cor, tipografia, espaçamento, raio e elevação. Valores canônicos claro/escuro. Como mapear para shadcn/ui e Tailwind. |
| [COMPONENTS.md](COMPONENTS.md) | Anatomia dos componentes que existem de fato, com a variante canônica escolhida entre as concorrentes. Componentes ausentes que precisam ser criados. |
| [PATTERNS.md](PATTERNS.md) | Layout, densidade, estados, semáforo regulatório, acessibilidade, mobile/campo, dado numérico e geoespacial. |
| [DEBITO.md](DEBITO.md) | Inventário das divergências encontradas nas telas de referência, com decisão e ação. Leia antes de portar qualquer tela. |

## Regra de ouro

Três regras não negociáveis, derivadas de `docs/DESIGN-UI.md` e confirmadas pela evidência:

1. **Nunca hex direto em feature.** Toda cor sai de token semântico. As telas que quebraram essa regra são exatamente as que não conseguiram ter tema escuro — a prova está em `DEBITO.md`.
2. **Cor nunca é o único sinal.** Todo estado carrega ícone + rótulo textual além da cor.
3. **shadcn/ui é a base**, estilizado pelos tokens SafraOS. Nunca componente nativo, nunca shadcn default sem passar pelos tokens.

## Ordem de leitura para implementar uma tela

`TOKENS.md` → `PATTERNS.md` → `COMPONENTS.md` → a tela de referência em `docs/design/` → `DEBITO.md` para conferir se o que você está copiando é padrão ou dívida.
