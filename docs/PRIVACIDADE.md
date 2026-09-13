# Governança de privacidade e proteção de dados

**Natureza:** documento autônomo de governança, fora do contrato de produto
**Responsável por decisões:** PI, apoiado por responsável jurídico/privacidade quando necessário
**Revisão:** 2026-09-13

Este documento não referencia, altera ou complementa requisitos de produto. Não cria funcionalidade, fatia, critério comercial ou aceite. Ele orienta como a organização deve avaliar e operar tratamento de dados pessoais. Segurança técnica continua obrigatória independentemente da classificação jurídica do dado.

Não constitui parecer jurídico. Base legal, papel dos agentes e prazo de retenção dependem do contexto real e devem ser validados antes da produção.

## 1. Escopo

Abrange dados relacionados a pessoa natural identificada ou identificável tratados pelo SafraOS ou por fornecedores, inclusive identidade, contato, documentos, voz, localização do dispositivo, autenticação, dados financeiros e registros de suporte.

Não classificar automaticamente dado de fazenda, CAR, talhão ou CNPJ como pessoal ou não pessoal: a combinação pode identificar produtor pessoa física ou outra pessoa natural.

## 2. Responsabilidades a definir

- identificar, por operação, controlador, operador e eventuais suboperadores;
- designar encarregado ou registrar formalmente a hipótese aplicável quando houver dispensa;
- manter canal para titulares e comunicações da ANPD;
- exigir contrato, finalidade, segurança, retenção e descarte dos fornecedores;
- registrar quem aprova mudanças materiais no tratamento.

## 3. Inventário mínimo de tratamento

Antes da produção, manter registro separado com: categoria de dado/titular; finalidade; agente responsável; hipótese legal validada; origem; destinatários; país/região; sistema; acesso; retenção; descarte; controles; risco; evidência da decisão.

“Necessário para o sistema” não é hipótese legal. Não escolher consentimento por conveniência: quando ele for a hipótese adequada, a manifestação precisa ser demonstrável, específica, destacada, revogável e separada de finalidades não necessárias.

## 4. Relatório de impacto

Avaliar a necessidade de RIPD quando houver determinação da ANPD ou tratamento com potencial alto risco, especialmente monitoramento/localização, dados financeiros, larga escala, decisões automatizadas ou combinação de bases. O controlador é responsável pelo documento.

Conteúdo mínimo recomendado: agentes; contexto/finalidade; dados e fluxo; necessidade/proporcionalidade; riscos aos titulares; medidas; risco residual; aprovadores; data e gatilho de revisão.

## 5. Direitos, retenção e eliminação

- disponibilizar canal autenticado e registrar pedido, identidade verificada, decisão, prazo e evidência;
- localizar cópias, projeções, arquivos, logs, backups e suboperadores afetados;
- eliminar ou anonimizar quando aplicável, preservando somente retenção amparada e documentada;
- responder também quando o pedido for negado ou parcialmente atendido, com fundamento validado;
- revogação de consentimento não implica apagar automaticamente dado mantido por outra hipótese válida;
- backup deve ter política de expiração e impedir restauração silenciosa de dado já eliminado.

Nenhum prazo fixo de eliminação é presumido neste documento. A matriz de retenção é aprovada fora do fluxo de produto.

## 6. Controles técnicos mínimos

- minimização na coleta e no log;
- autorização por objeto e isolamento por tenant;
- criptografia em trânsito e repouso, segredo em cofre e rotação;
- acesso administrativo temporário, justificado e auditado;
- ambientes não produtivos sem cópia irrestrita de dados reais;
- exportação e exclusão resistentes a enumeração, fraude e vazamento;
- telemetria com redaction de conteúdo pessoal/sensível;
- teste de restauração, resposta a incidente e descarte de mídia.

## 7. Incidentes

Manter playbook com detecção, contenção, preservação de evidência, avaliação de risco/dano, responsáveis, comunicação e lições aprendidas. Incidente com risco ou dano relevante pode exigir comunicação pelo controlador à ANPD e aos titulares. A Resolução CD/ANPD nº 15/2024 determina prazo de três dias úteis, ressalvada legislação específica, e registro dos incidentes por pelo menos cinco anos.

## 8. Gatilhos de revisão

Novo dado/finalidade/fornecedor/país; uso de IA com dado pessoal; mudança de autenticação ou rastreamento; incidente; solicitação da ANPD/titular; alteração normativa; revisão anual.

## 9. Fontes oficiais

- [ANPD — agentes de tratamento e encarregado](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-para-definicoes-dos-agentes-de-tratamento-de-dados-pessoais-e-do-encarregado)
- [ANPD — direitos dos titulares](https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares)
- [ANPD — relatório de impacto](https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/relatorio-de-impacto-a-protecao-de-dados-pessoais-ripd)
- [ANPD — comunicação de incidente](https://www.gov.br/anpd/pt-br/canais_atendimento/agente-de-tratamento/comunicado-de-incidente-de-seguranca-cis)
- [ANPD — regulamentações vigentes](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd)
