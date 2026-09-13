# SPEC-004 — Cadastro web de fazendas

**MVP:** MVP0
**Fatia:** F4
**Estado:** pronta
**Dependência:** SPEC-003

## Resultado

Owner cadastra, consulta, altera e arquiva fazendas do tenant ativo por nome, UF e município.

## Regras

- fazenda pertence a uma organização e não contém CPF/CNPJ no MVP0;
- nome é obrigatório, normalizado para comparação, mas não é presumido único;
- UF é a sigla de duas letras (ex.: `GO`, `MT`, `MS`), validada contra a lista fixa das 27 UFs brasileiras;
- município é identificado pelo código IBGE de 7 dígitos e exibido pelo nome; a tabela de municípios (código, nome, UF) entra por seed carregado na primeira fatia que precisar (`CLAUDE.md` — dado de desenvolvimento entra por seed, sem hardcode);
- exclusão física não entra: arquivamento preserva vínculos e auditoria;
- lista padrão omite arquivadas e permite exibi-las explicitamente;
- troca de tenant limpa seleção e dados da interface anterior.

## Critérios de aceite

- CRUD e arquivamento funcionam por teclado e em viewport desktop;
- município inválido para a UF é rejeitado no backend;
- erro recuperável preserva dados do formulário;
- tenant B não lê, altera, arquiva nem infere fazenda do tenant A;
- estados loading, vazio, erro e sucesso são visíveis e acessíveis;
- ações de criar, alterar e arquivar são auditadas.
