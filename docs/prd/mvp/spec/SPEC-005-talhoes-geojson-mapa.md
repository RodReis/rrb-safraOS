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
- geometria vazia, autointersectada, fora de limites geográficos ou com anéis inválidos é rejeitada;
- área canônica em hectares é calculada geodesicamente no backend;
- nome é obrigatório e não é presumido único;
- arquivo aceita somente GeoJSON, com limite documentado; KML está fora;
- mapa nunca consulta ou mantém objetos de tenant anterior após troca.

## Critérios de aceite

- desenho e importação produzem a mesma geometria canônica para caso equivalente;
- prévia mostra polígono, mas valor de área do cliente não é confiado;
- backend retorna problema acionável para arquivo/tipo/geometria inválidos;
- lista e mapa exibem apenas fazenda e tenant ativos;
- teste entre tenants cobre endpoints e RLS;
- fluxo completo do MVP0 passa em navegador real;
- desempenho do mapa é medido com massa definida no plano, sem meta inventada além do PRD.
