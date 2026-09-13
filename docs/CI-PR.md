# Política de CI para pull requests

**Revisão:** 2026-09-13

## Objetivo e desenho

Feedback rápido sem reduzir cobertura nem transformar ausência de teste em sucesso.

```text
quality ───────┐
test-regras ───┤
test-banco ────┼─> aggregate (artefatos; sem reexecutar) ─> gate
test-tela ─────┤
e2e ───────────┘
```

- Jobs independentes rodam em paralelo.
- O agregador valida schema, anti-drift e completude dos relatórios.
- `gate` usa `if: always()` e aceita apenas resultados explicitamente válidos.
- Job condicional só pode ficar `skipped` quando seu contrato disser que não se aplica.
- `gate` é o único required check; exigir workflow que pode não disparar deixa check pendente.

## Desempenho seguro

- `concurrency` cancela execução obsoleta da mesma PR.
- Cache armazena dependências, nunca PASS ou segredo; sem cache o resultado não muda.
- Artefatos transportam resultados. Ferramentas/actions usam versão fixada.
- Timeout explícito; comandos não interativos.
- PR acima de 15 min: medir fila, setup e job; comparar mediana/p95 de execuções equivalentes.

Filtro de paths decide categorias adicionais, mas não elimina `quality`/`gate`. Mudança em workflow, filtro ou gerador testa cenários que passam, falham e não se aplicam.

## Estado confiável

Check válido pertence ao SHA atual. Novo commit invalida a conclusão anterior. Lista vazia, watcher silencioso, `queued`, `in_progress` ou print antigo não são verde. Usar `gh pr checks <n> --watch` e reconfirmar head/PR antes do merge.

## Referências

- [GitHub — jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs)
- [GitHub — required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
- [GitHub — cache](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)

