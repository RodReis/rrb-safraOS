# SPEC-003 — Organização, tenancy e auditoria

**MVP:** MVP0
**Fatia:** F3
**Estado:** pronta
**Dependência:** SPEC-002

## Resultado

Usuário autenticado cria organizações, alterna o tenant ativo e acessa somente organizações às quais pertence como `owner`, com autorização no caso de uso, RLS e auditoria append-only.

## Regras

- organização é a raiz do tenant; usuário pode possuir mais de uma organização;
- `Membership(user_id, organization_id)` é única; único papel do MVP0 é `owner`;
- tenant ativo é selecionado entre memberships da sessão, nunca confiado por header livre;
- todas as tabelas de tenant têm `organization_id` não nulo;
- role normal da aplicação não é owner das tabelas nem possui `BYPASSRLS`;
- ausência de policy resulta em deny;
- auditoria registra ator, tenant, ação, objeto, resultado, instante e correlação, sem segredo.

## Critérios de aceite

- criar e listar organizações próprias funciona na web;
- alternar tenant muda o contexto sem criar nova identidade;
- IDs de outra organização não permitem leitura, escrita ou inferência;
- testes acessam banco pela mesma role da aplicação e comprovam RLS;
- tentativa negada e mutação aceita produzem auditoria correta;
- auditoria não pode ser alterada pela role da aplicação.
