# Direção de UI do SafraOS

**Natureza:** direção para o design system, não contrato funcional. Base visual: `docs/design/DESIGN.md` e `docs/design/*/screen.png`.

## Carbono Adaptativo

Robustez operacional e leitura ao sol, sem dashboard bancário genérico nem “verde sustentável” decorativo. Base neutra de alto contraste; verde carbono como marca/ação; semáforo reservado a `ok`, `atenção`, `crítico`, `inconclusivo`; números tabulares; mapa sempre com legenda, fonte, data e cobertura.

## Pipeline de accent

`token semântico -> estado/componente -> contraste -> tema -> prova visual`. Nunca usar hex direto em feature. Definir tokens de superfície, texto, borda, ação, foco e estados. Cor nunca é o único sinal.

## Componentes e hierarquia

- shadcn/ui como base, estilizado pelos tokens SafraOS;
- uma ação primária por contexto; destrutiva separada;
- valor mostra unidade/período; resumo antes de evidência/histórico;
- estados: loading, vazio, parcial, offline, erro recuperável, sem permissão e sucesso;
- toast para evento transitório; erro persistente junto do objeto;
- tabela densa com ordenação, filtro, paginação e exportação.

## Campo/mobile

Alvos amplos, alto contraste, uso com uma mão. Rede, fila e última sincronização visíveis sem bloquear captura. GPS mostra precisão. Rascunho é preservado. Texto PT-BR simples; áudio é alternativa.

## Prova

Desktop/tablet/mobile; teclado; contraste; zoom; erro/offline; dados longos; moeda/área/data; screenshot comparativa. Ferramenta de design propõe; PRD, acessibilidade e tokens limitam.
