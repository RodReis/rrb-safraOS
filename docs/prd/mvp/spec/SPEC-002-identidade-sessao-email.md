# SPEC-002 — Identidade, sessão e e-mail assíncrono

**MVP:** MVP0
**Fatia:** F2
**Estado:** pronta
**Dependência:** SPEC-001

## Resultado

Usuário cria conta, confirma e-mail, autentica, encerra sessão e recupera senha por e-mails processados no Celery e visualizados no Mailpit local.

## Regras

- e-mail é normalizado e único; respostas de confirmação/recuperação não enumeram contas;
- senha é armazenada somente como hash Argon2id com parâmetros versionados;
- token externo é aleatório, armazenado apenas como hash, expira e é usado uma vez;
- confirmação não autentica automaticamente; usuário retorna ao login;
- sessão usa cookie `HttpOnly`; `Secure` fora de HTTP local; `SameSite=Lax`;
- operações mutáveis exigem CSRF; login rotaciona sessão; logout e reset revogam sessões;
- tentativa de e-mail é idempotente e retry só ocorre em falha transitória.

## Estados

`User`: `pending_verification -> active -> disabled`.
Token: `active -> consumed | expired`.
Sessão: `active -> revoked | expired`.

## Critérios de aceite

- fluxo cadastro → Mailpit → confirmação → login funciona em navegador real;
- login antes da confirmação é negado sem revelar dados adicionais;
- solicitação de recuperação retorna resposta neutra para e-mail existente ou inexistente;
- token expirado/usado é rejeitado; reset revoga sessões e tokens anteriores;
- CSRF ausente/inválido bloqueia mutação autenticada;
- reentrega Celery não envia efeito lógico duplicado;
- logs e respostas nunca contêm senha, token completo ou hash de senha.
