# Convenções Git e GitHub

## Branches, worktrees e commits

- Uma issue por branch/worktree isolado; prefixo padrão `codex/`.
- Nunca limpar trabalho alheio; atualizar/reconciliar base antes da PR e quando `main` avançar.
- Commits pequenos, coerentes e executáveis; mensagem PT-BR, verbo no imperativo.
- Não versionar segredo, `.env`, PII, XML/certificado real ou artefato pesado.
- Não usar `[skip ci]` para contornar gate.

```text
feat(campo): persista operações offline por dispositivo
fix(financeiro): impeça duplicidade no reenvio do lançamento
docs(arquitetura): registre isolamento por tenant
```

## Integração

- Código entra por PR; docs do Cowork seguem a exceção do `CLAUDE.md`.
- Squash merge após gate verde do SHA atual.
- Rebase reaplica a branch sobre `main`; nunca desfaz alteração do Cowork.
- `--force-with-lease` só em branch própria, após conferir a divergência.
- PR usa `refs #N`, nunca `closes #N`; aceite/fechamento são do PI.

## Proteção e verificação

Ruleset, required checks, merge queue, review obrigatório ou auto-merge exigem autorização específica. Actions de terceiros devem usar referência imutável conforme política aprovada; `GITHUB_TOKEN` com permissões mínimas.

Antes de afirmar estado: consultar issue/PR no GitHub, confirmar head SHA e rodar `gh pr checks <n> --watch`. Após merge, confirmar `mergedAt` e `mergeSha`.

Referências: [pull requests](https://docs.github.com/en/pull-requests/get-started/about-pull-requests) e [padronização/rulesets](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/managing-and-standardizing-pull-requests).

