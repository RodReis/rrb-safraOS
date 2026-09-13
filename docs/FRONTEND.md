# Contrato de frontend web do SafraOS

**Natureza:** contrato de engenharia da interface web (`apps/web`). Toda tela passa por aqui.
**Escopo:** web React/TypeScript. Mobile (Expo) terá contrato próprio quando entrar (ADR-009).
**Precedência:** PRD e SPEC definem *o que* a tela faz; este documento define *como* ela é construída; `docs/DESIGN-UI.md` e `docs/design-system/` definem *como ela parece*. Onde divergirem, essa é a ordem.
**Decisão do PI:** 2026-09-13
**Revisão:** 2026-09-13

## 1. Objetivo

Telas modernas, limpas e consistentes, com foco em experiência do usuário, performance percebida, estado previsível e tipagem de ponta a ponta. Nada aqui é sugestão: item que não se aplica a uma tela é registrado na PR como não aplicável, nunca ignorado em silêncio.

## 2. Stack fixada

| Preocupação | Escolha | Regra |
|---|---|---|
| Componentes | shadcn/ui (via MCP `shadcn`) estilizado pelos tokens de `docs/design-system/TOKENS.md` | Nunca componente HTML nativo cru (`<select>`, `<input>`, `<dialog>`, `<table>` sem wrapper) nem shadcn default sem token |
| Estado de servidor | TanStack Query | Todo dado remoto passa por `useQuery`/`useMutation`; sem `useEffect + fetch`; sem Redux/RTK Query/SWR |
| Estado local/global de UI | `useState`/`useReducer`; Zustand só se dois ramos distantes da árvore precisarem do mesmo estado | Estado de servidor nunca é copiado para store local |
| Formulários | React Hook Form + Zod (`zodResolver`) | Schema Zod é a única fonte de validação no cliente; mensagens em PT-BR |
| Tabelas/listas | TanStack Table sobre `DataTable` do shadcn | Ordenação, filtro e paginação server-side por padrão; client-side só com massa pequena e finita, declarada na SPEC |
| Notificações | Sonner (toast do shadcn) | `info`, `success`, `warning`, `error`; nunca `alert`/`confirm`/`prompt` |
| Gráficos | shadcn Charts (Recharts) | Nunca `<canvas>`/SVG manual para gráfico de dados |
| Mapa | React Leaflet + Leaflet-Geoman Free, encapsulados em adapter | Feature não importa Leaflet diretamente |
| Roteamento | React Router com code splitting por rota (`React.lazy` + `Suspense`) | Toda rota carrega sob demanda |
| Cliente HTTP | Cliente TypeScript gerado do OpenAPI do FastAPI (`openapi-typescript` + fetch tipado) | Proibido `fetch` manual com tipo escrito à mão para endpoint que existe no OpenAPI |
| Máscaras | Biblioteca de máscara integrada ao RHF | Date, R$, CPF, CNPJ, telefone, e-mail — sempre máscara **e** validação Zod |
| Datas | `date-fns` com locale `pt-BR` | Valor de API em ISO 8601 UTC; exibição no fuso do usuário |
| Dinheiro | Valor da API em inteiro (centavos) ou string decimal; formatação com `Intl.NumberFormat('pt-BR', { currency: 'BRL' })` | Nunca `number` float para cálculo no cliente |

Versões são fixadas no lockfile; troca de biblioteca desta tabela exige ADR.

## 3. Tipagem

- `strict: true`, `noUncheckedIndexedAccess: true`; proibido `any` implícito ou explícito; dado externo entra como `unknown` e passa por Zod.
- Tipos de API vêm do OpenAPI gerado; o gerador roda em `npm run typecheck` e a CI falha se o arquivo gerado divergir do commitado (anti-drift).
- Schema Zod do formulário deriva do tipo da API (`z.object` que satisfaz o DTO), não o contrário.
- Props de componente são `interface` exportada; sem `React.FC`; children explícito.
- Enum de domínio (estados, papéis, semáforo) é união literal vinda do OpenAPI; nunca string solta.

## 4. Padrão de tela CRUD

Toda entidade administrável tem quatro telas ou estados, com o mesmo esqueleto:

**Read (lista).** `DataTable` com: busca, filtros persistidos na URL (`?page=&sort=&q=`), ordenação por coluna, paginação server-side com tamanho de página selecionável, coluna de ações por linha (`DropdownMenu`: ver, editar, arquivar), ação primária única no topo (`Novo`), exportação quando a SPEC pedir. Linha clicável abre detalhe. Estado `empty` tem texto e ação; estado `error` tem retry.

**Read (detalhe).** Resumo antes de evidência/histórico (`DESIGN-UI.md`). Valor sempre com unidade e período.

**Create / Update.** Mesmo formulário (`Sheet` ou página, conforme complexidade), RHF + Zod, campos com máscara, erro por campo e `aria-describedby`, botão primário desabilitado só durante `submitting` (nunca por validação pendente sem feedback). Erro recuperável preserva os dados; campo de senha nunca é reposto. Sucesso: toast + invalidação da query da lista + navegação para o detalhe ou lista.

**Delete.** Nunca imediato. `AlertDialog` de confirmação nomeando o objeto. Padrão do projeto é **arquivar** (soft delete auditado, `SPEC-004`); exclusão física só quando a SPEC da entidade disser, e então com confirmação por digitação do nome. Toast de sucesso com `Desfazer` quando a operação for reversível.

**Infinite scroll** só em feeds (timeline de lançamentos, alertas); nunca em grid de CRUD.

## 5. Estados e feedback

- Toda consulta representa `loading`, `empty`, `error`, `partial` (dado com cobertura incompleta), `offline` (quando aplicável) e `success`; toda mutação representa `idle`, `submitting`, `success`, `error`.
- `loading` de leitura usa **Skeleton** com a forma do conteúdo final; spinner só em botão durante `submitting`.
- Mutação usa atualização otimista quando a reversão é trivial (toggle, arquivar); caso contrário, aguarda e mostra `submitting`.
- Erro `application/problem+json` da API é mapeado por `code` para mensagem PT-BR; `correlationId` aparece no toast de erro para suporte. Erro persistente fica junto do objeto; toast é para evento transitório.
- Sem dado nunca renderiza como "ok": semáforo tem quarto estado `inconclusivo` (`DEBITO.md` §5).

## 6. Performance

- Code splitting por rota; componentes pesados (mapa, gráficos, editor) em `lazy` com Skeleton.
- Lista acima de 200 linhas renderizadas usa virtualização (TanStack Virtual).
- `staleTime` por query declarado; sem refetch em foco para dados que não mudam por outros usuários.
- Imagens e tiles com `loading="lazy"`; ícones via sprite/tree-shaking, nunca pacote inteiro.
- Orçamento: bundle inicial ≤ 250 kB gzip; LCP ≤ 2,5 s e INP ≤ 200 ms em desktop de referência, medidos no E2E de smoke. Estourou: a PR registra a causa e o plano.

## 7. Componentização

- Estrutura por feature: `apps/web/src/features/<entidade>/{api,components,hooks,schemas,routes}`; `packages/frontend` guarda só o que duas features usam.
- Componente é criado uma vez e reaproveitado: `DataTable`, `FormField` com máscara, `StatusBadge`, `ConfirmDialog`, `PageHeader`, `EmptyState`, `ErrorState`, `MapAdapter`. Duplicar um deles é P2 em revisão.
- Nenhum hex, tamanho de fonte ou espaçamento fora dos tokens; `tabular-nums` em todo valor comparável em coluna.
- Nada de manipulação direta do DOM; refs só para foco e medida.

## 8. Acessibilidade e responsividade

- Navegável por teclado, foco visível, `aria-*` correto em diálogo, tabela e menu; contraste conforme `TOKENS.md`.
- Desktop-first no MVP0 (SPEC-004/005), mas layout não quebra em tablet; mobile web é modo de leitura.
- Texto de interface em PT-BR simples; cor nunca é o único sinal.

## 9. Referência visual obrigatória

Antes de construir uma tela, consultar a tela equivalente em `docs/design/claro/*/code.html` e `docs/design/escuro/*/code.html` e passar por `docs/design-system/DEBITO.md`: o que estiver lá é dívida, não padrão. Ordem de leitura: `TOKENS.md` → `PATTERNS.md` → `COMPONENTS.md` → tela de referência → `DEBITO.md`. Paleta oficial é a azul institucional de `docs/design/DESIGN-CLARO.md`/`DESIGN-ESCURO.md`.

## 10. Skills obrigatórias em tarefa de UI

`document-skills:frontend-design` antes de desenhar a tela; `impeccable` e `gstack:design-review` para acabamento **quando existirem no ambiente** — ausência da skill não dispensa a disciplina: a PR inclui screenshot desktop e prova E2E do estado. `context7` para documentação de biblioteca.

## 11. Prova por tela (entra na PR)

- teste de componente cobrindo `loading`, `empty`, `error` e `success`;
- teste de formulário: validação Zod, máscara, erro por campo, preservação de dados;
- teste de tabela: ordenação, filtro e paginação refletidos na URL;
- E2E do fluxo da SPEC em navegador real, com screenshot;
- typecheck com cliente OpenAPI atualizado;
- nenhuma violação de tokens/`DEBITO.md` no diff.
