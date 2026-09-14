# APRENDIZADOS — rrb-safraOS

Consolidação da seção **Aprendizado** dos comentários de encerramento de card (ver "Encerramento de card" no `CLAUDE.md`). Não é histórico do projeto — é a lista curta do que ainda pode nos morder. Histórico mora em `docs/STATUS-ARQUIVO.md` e nas próprias issues.

## Protocolo

- **Quem mantém:** Cowork. Fonte única: a seção **Aprendizado** dos comentários de encerramento das issues. Nada entra aqui que não tenha saído de um comentário de encerramento.
- **Quando:** no fecho de cada MVP (card `[GATE]`) e imediatamente quando o mesmo aprendizado aparecer em dois cards.
- **Quem lê:** o Code no passo 1 de todo card (é curto, por isso é obrigatório); o Cowork antes de fechar uma spec.
- **Formato:** uma linha por aprendizado, agrupada por tema — `<lição> — fonte: <doc oficial | commit | log> (card #N)`.
- **Teto: 40 linhas.** Estourar o teto não apaga item: **promove**. Aprendizado que já virou regra sai desta lista e vai para o documento que manda — `CLAUDE.md` (processo), `docs/CONVENTION.md` (domínio), `docs/ARCHITECTURE.md` ou um ADR (estrutura) — e fica registrado em "Promovidos" com o destino. Esta lista é funil, não cemitério.
- Linha sem fonte verificável não entra. Aprendizado que não muda decisão futura não é aprendizado: é diário, e diário fica na issue.

## Ambiente Windows

- `spawn` de arquivo `.cmd` sem shell falha com `EINVAL` no Windows; chamar via `cmd.exe /c` explícito — fonte: doc do Node (card #1)

## Async e event loop (Python)

- `psycopg` async é incompatível com o `ProactorEventLoop`, que é o default do Windows — fonte: doc do psycopg (card #1)
- `uvicorn.run()` reintroduz o `ProactorEventLoop` mesmo com a policy já trocada; subir via `server.serve()` dentro de `asyncio.run()` — fonte: doc do uvicorn (card #1)

## API e CI

- CORS ausente na API passou pelos health checks e só apareceu no E2E ponta a ponta; smoke por serviço isolado não pega — fonte: execução do E2E (card #1)

## Promovidos (saíram desta lista)

_Nenhum._
