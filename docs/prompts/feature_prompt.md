Você é um backend sênior. Vamos implementar uma feature pequena, mas completa, em Django + DRF.

Feature escolhida: LIKE/UNLIKE de posts (toggle)  [troque aqui se quiser: salvar post, report, views counter]

Requisitos:
1) Modelagem:
   - modelo `PostLike` com FK para Post e User
   - unique constraint (user, post)
   - timestamps
2) API:
   - POST `/posts/{id}/like/` -> curtir (idempotente)
   - DELETE `/posts/{id}/like/` -> descurtir (idempotente)
   - incluir no serializer do post: `likes_count` e `liked_by_me`
3) Regras:
   - respeitar `CanViewPost` (não pode curtir se não pode ver)
   - performance: evitar N+1 (annotations/subquery)
4) Tests:
   - curtir/descurtir
   - idempotência
   - contagem e flag `liked_by_me`
5) Documentação OpenAPI (drf-spectacular): exemplos de resposta e erros
6) Segurança: evitar enumeração (404 vs 403 se aplicável), validações robustas

Entregue tudo: models, migrations (descritas), serializers, views/urls, selectors/services e testes pytest.
