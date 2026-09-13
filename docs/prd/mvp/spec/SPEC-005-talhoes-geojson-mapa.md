# SPEC-005 — Talhões, GeoJSON e mapa web

**MVP:** MVP0
**Fatia:** F5
**Estado:** pronta
**Dependência:** SPEC-004

## Resultado

Owner cadastra talhão desenhando no mapa ou importando GeoJSON e visualiza os talhões da fazenda/tenant ativo com área calculada no backend.

## Regras

- geometria canônica é `MultiPolygon` SRID 4674;
- `Polygon` GeoJSON válido é normalizado; outros tipos são rejeitados;
- geometria é rejeitada quando vazia, autointersectada, com anéis inválidos, ou com qualquer coordenada fora do bounding box do Brasil (longitude entre -74,0 e -32,0; latitude entre -34,0 e 6,0);
- área canônica em hectares é calculada geodesicamente no backend e persistida com 4 casas decimais;
- nome é obrigatório e não é presumido único;
- arquivo aceita somente GeoJSON, até 5 MB por arquivo; acima disso a API rejeita com erro acionável; KML está fora;
- mapa nunca consulta ou mantém objetos de tenant anterior após troca.

## Critérios de aceite

- desenho e importação produzem a mesma geometria canônica para caso equivalente;
- prévia mostra polígono, mas valor de área do cliente não é confiado;
- backend retorna problema acionável para arquivo/tipo/geometria inválidos, incluindo os dois casos de tamanho (>5 MB) e bounding box (fora do Brasil);
- lista e mapa exibem apenas fazenda e tenant ativos;
- teste entre tenants cobre endpoints e RLS;
- fluxo completo do MVP0 passa em navegador real;
- desempenho do mapa é medido com massa de 500 talhões cadastrados numa única fazenda (decisão do PI, 2026-09-13), sem meta inventada além do PRD.
