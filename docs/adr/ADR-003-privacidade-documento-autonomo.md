# ADR-003 — Privacidade em documento autônomo, sem efeito sobre produto

**Estado:** aceita
**Data:** 2026-09-13
**Decisor:** PI (Rodrigo Reis)

## Contexto

O PRD v2.0 e a arquitetura histórica traziam LGPD, RIPD, k-anonimato e retenção como requisitos de produto. O PI fixou a regra oposta: ninguém cria regra de LGPD, consentimento, aceite duplo ou amarra jurídica no projeto sem autorização explícita dele (`CLAUDE.md` §Regras do projeto). Havia um `docs/PRIVACIDADE.md` que descrevia governança de dados pessoais e uma cláusula que permitia a ele "afetar implementação quando classificar controle técnico aplicável" — o que reabriria a porta para a regra que o PI vetou.

## Decisão

`docs/PRIVACIDADE.md` existe como **documento isolado, sem efeito sobre produto**: não é referenciado por nenhuma SPEC, PRD, `CONVENTION.md` ou `ARCHITECTURE.md`, e não pode gerar controle técnico, funcionalidade, fatia ou critério de aceite por conta própria. A cláusula do `CLAUDE.md` que permitia esse efeito foi removida em 2026-09-13.

## Alternativas consideradas

- Remover o documento inteiramente: rejeitada pelo PI — o documento fica, mas sem efeito.
- Manter a cláusula de efeito técnico: rejeitada — contradizia a regra fixa do projeto.

## Consequências

- Segurança técnica (criptografia, isolamento por tenant, redaction de log) continua obrigatória como engenharia (`docs/ARCHITECTURE.md` §Persistência/§APIs), nunca justificada como "requisito de LGPD".
- Nenhuma SPEC pode citar `docs/PRIVACIDADE.md` como fonte de regra.

## Riscos / reversibilidade

Reversível a qualquer momento por decisão explícita do PI, que pode reativar o documento como fonte de regra se decidir tratar o tema formalmente.

## Evidência

Decisão original em `docs/DECISIONS.md` (2026-09-13); confirmação e correção da cláusula de efeito nesta sessão (Cowork), mesma data.

## Links

`CLAUDE.md` §Regras do projeto. `docs/PRIVACIDADE.md`.
