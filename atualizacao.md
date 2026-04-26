# Atualizações — Backend (branch `main`)

Resumo de todas as features, correções e melhorias implementadas no backend desde o commit inicial.

---

## Setup Inicial

### Commit `923f3f3` — Setup básico
- Configuração do projeto Django com estrutura de settings separada (`base`, `dev`, `prod`)
- Integração do **drf-spectacular** para documentação Swagger/OpenAPI
- Configuração do **pytest** com `pytest.ini`
- App `core` com endpoint de healthcheck (`GET /health/`)
- App `accounts` com estrutura inicial (models, views, URLs)
- `.gitignore` configurado

---

## App: `accounts`

### Modelos (`accounts/models/`)

**`user.py`**
- Model `User` customizado com autenticação por e-mail (sem `username`)
- Campo `role` com choices: `ELDER`, `CAREGIVER`, `GUARDIAN`, `PROFESSIONAL`, `INSTITUTION`
- Campos de endereço: `address_line`, `city`, `state`, `zip_code` (adicionado em #5)
- Campo `avatar` para foto de perfil (adicionado em `feb0f22`)
- Flags: `is_verified`, `onboarding_completed`, `show_email`, `show_phone`, `show_links`

**Perfis por papel** (cada um em arquivo próprio):
- `elder_profile.py` — `ElderProfile`: campos clínicos completos (mobilidade, cognição, medicações, alergias, contato de emergência, nível de cuidado)
- `caregiver_profile.py` — `CaregiverProfile`: bio, experiência em anos, disponibilidade, cidade/estado, tipos de cuidado
- `guardian_profile.py` — `GuardianProfile`: tipo de parentesco, se é responsável legal, contato preferencial
- `professional_profile.py` — `ProfessionalProfile`: profissão (com campo `OTHER`), registro profissional, modo de atendimento, valor/hora, bio
- `institution_profile.py` — `InstitutionProfile`: nome legal/fantasia, CNPJ, tipo de instituição, capacidade, website, número de licença
- `caregiver_care_type.py` — tabela de tipos de cuidado associados ao cuidador
- `notification.py` — `Notification`: tipo (`LINK_REQUEST`, `LINK_ACCEPTED`), leitura, ator, referência ao link

### Serializers (`accounts/serializers/`)
- `signup.py` — validação e criação de usuário com hash de senha
- `token_by_email.py` — autenticação via e-mail + senha
- `me.py` — serializer do perfil base do usuário autenticado (com upload de avatar)
- `elder_me.py`, `caregiver_me.py`, `guardian_me.py`, `professional_me.py`, `institution_me.py` — serializers CRUD por papel
- `user_serializers.py` — serializer de perfil público com controle de visibilidade

### Views (`accounts/views/`)
- `signup.py` — `POST /accounts/signup/` — cria usuário e perfil base
- `token_by_email.py` — `POST /auth/token/` — retorna JWT (access + refresh); cabeçalho Authorization ignorado na requisição
- `me.py` — `GET/PATCH /accounts/me/` — perfil base do usuário autenticado
- `elder_me.py` — `GET/PATCH /accounts/elder/me/`
- `caregiver_me.py` — `GET/PATCH /accounts/caregiver/me/`
- `guardian_me.py` — `GET/PATCH /accounts/guardian/me/`
- `professional_me.py` — `GET/PATCH /accounts/professional/me/`
- `institution_me.py` — `GET/PATCH /accounts/institution/me/`
- `complete_onboarding.py` — `POST /accounts/onboarding/` — preenche perfil por papel e marca `onboarding_completed = True`
- `elder_medical_record.py` — `GET /accounts/elder/<id>/medical-record/` — retorna prontuário; requer vínculo ativo entre solicitante e idoso
- `public_user.py` — `GET /accounts/users/<id>/` — perfil público com campos filtrados por privacidade
- `notifications.py` — `GET /accounts/notifications/`, `PATCH /accounts/notifications/<id>/read/`, `POST /accounts/notifications/read-all/`
- `password.py` — `POST /accounts/change-password/`

### Serviços (`accounts/services/`)
- `user_services.py` — lógica de criação de usuário, atualização de perfil, verificação de permissões
- `user_normalization.py` — normalização de campos (e-mail lowercase, CPF/CNPJ strip de formatação)

### URLs (`accounts/urls/`)
Estrutura modular com arquivos separados por domínio:
- `urls.py` — agrega todas as rotas de accounts
- `urls_auth.py` — rotas de autenticação (signup, token, refresh)
- `urls_elders.py`, `urls_caregivers.py`, `urls_guardians.py`, `urls_professionals.py`, `urls_institutions.py` — rotas `/me/` por papel
- `urls_profiles.py` — onboarding, medical record, change-password
- `urls_public_users.py` — perfil público e links públicos
- `urls_notifications.py` — notificações

### Permissões (`accounts/permissions.py`)
- `IsElder`, `IsCaregiver`, `IsGuardian`, `IsProfessional`, `IsInstitution` — permissões por papel para rotas restritas

---

## App: `links`

### Modelos (`links/models/`)
- `caregiver_elder_link.py` — vínculo Cuidador ↔ Idoso: valor/hora, notas, status (PENDING/ACTIVE/ENDED/CANCELLED)
- `guardian_elder_link.py` — vínculo Responsável ↔ Idoso: parentesco, responsável legal, permissões médicas/contratação; status incluindo ENDED (adicionado em `feb0f22`)
- `professional_elder_link.py` — vínculo Profissional ↔ Idoso: modo de serviço, metas, valor/hora
- `institution_elder_link.py` — vínculo Instituição ↔ Idoso: quarto, leito, data de admissão/saída
- `caregiver_elder_link_care_type.py` — tipos de cuidado por vínculo

### Serializers (`links/serializers/link_serializer.py`)
- `GenericLinkSerializer` — serializer de criação multi-tipo (determina tipo pelo campo `link_type`)
- `LinkListSerializer` — serializer de listagem com campos calculados:
  - `link_type`, `other_party_name`, `other_party_role`, `other_party_bio`, `other_party_extra`
  - `other_party_extra`: chips de informação extra por tipo (experiência + localização para cuidador; especialidade + registro para profissional; parentesco para responsável; tipo + capacidade para instituição)
  - `notes`: notas do solicitante visíveis apenas ao idoso em vínculos pendentes

### Serviços (`links/services/link_services.py`)
- `create_caregiver_link`, `create_guardian_link`, `create_professional_link`, `create_institution_link` — criação com validação de papel e unicidade
- `respond_to_*_link` — aceitar ou rejeitar vínculo; apenas o idoso pode responder
- Dispara notificações (`Notification`) ao criar e ao aceitar vínculos

### Views (`links/views/link_viewset.py`)
- `LinkViewSet` — ViewSet genérico com ações:
  - `list` — lista todos os vínculos do usuário autenticado (qualquer papel)
  - `retrieve` — lista vínculos ativos/encerrados de outro usuário (perfil público)
  - `create` — cria novo vínculo pelo `link_type` do payload
  - `respond` — aceitar/rejeitar vínculo (`POST /links/respond/`)
  - `end` — encerrar vínculo ativo (`POST /links/end/`); usando string literals (`'ACTIVE'`, `'ENDED'`) para evitar dependência de inner `Status` classes

---

## App: `posts`

### Modelos (`posts/models/`)
- `posts.py` — `Post`: texto, imagens (FK para `PostImage`), status (DRAFT/PUBLISHED), visibilidade, soft delete (`deleted_at`)
- `post_image.py` — `PostImage`: múltiplas imagens por post
- `post_like.py` — `PostLike`: curtidas com unicidade por usuário/post
- `post_comment.py` — `PostComment`: comentários com soft delete

### Serializers (`posts/serializers/`)
- `post_serializers.py` — CRUD de posts com upload de múltiplas imagens via `MultiPartParser`
- `feed_serializers.py` — serializer otimizado do feed: `author_id`, `author_name`, `author_avatar`, `author_role`, `liked_by_me`, `images[]`, `tags`
- `post_comment_serializers.py` — CRUD de comentários

### Seletores (`posts/selectors/feed.py`)
- `get_feed_queryset(user, filters)` — query otimizada com `select_related` + `prefetch_related`
- Filtra posts deletados, suporta filtros por `q` (busca textual), `role`, `tag`
- Cache de 60 segundos por chave composta (usuário + cursor + filtros)

### Serviços (`posts/services/`)
- `post_services.py` — criação e edição de posts com upload de imagens para S3 (`django-storages`)
- `post_like_services.py` — toggle de curtida (like/unlike)
- `post_comment_services.py` — CRUD de comentários com validação de propriedade

### Views (`posts/views/`)
- `post_views.py` — `GET/POST/PATCH/DELETE /posts/my-posts/` — CRUD de posts do usuário autenticado
- `feed_views.py` — `GET /posts/feed/` — feed paginado com cursor pagination
- `post_like_views.py` — `POST /posts/<id>/like/`, `DELETE /posts/<id>/unlike/`
- `post_comment_views.py` — `GET/POST /posts/<id>/comments/`, `PATCH/DELETE /posts/<id>/comments/<cid>/`
- `user_posts_view.py` — `GET /posts/user/<id>/` — posts públicos de outro usuário

### Permissões (`posts/permissions.py`)
- `IsPostOwner` — apenas o autor pode editar/deletar o próprio post

---

## App: `search`

### Serializers (`search/serializers/search.py`)
- Serializers por papel retornando campos relevantes por contexto:
  - `ElderSearchSerializer`, `CaregiverSearchSerializer`, `GuardianSearchSerializer`, `ProfessionalSearchSerializer`, `InstitutionSearchSerializer`
- Fallback para usuários sem perfil de papel

### Views (`search/views/search.py`)
- `GET /search/` — busca de usuários com filtros:
  - `q`: nome (busca textual)
  - `role`: papel do usuário
  - `city`, `state`: localização
  - `is_available`: disponibilidade (cuidadores/profissionais)
  - `experience_years`: mínimo de anos de experiência
  - `profession`: profissão (profissionais)
  - `service_mode`: modo de atendimento
  - `min_price`, `max_price`: faixa de valor/hora
- Paginação por cursor (`CursorPagination`)

---

## App: `core`

### Exceções (`core/exceptions/`)
- `domain.py` — exceções de domínio: `ValidationError`, `ConflictError`, `NotFoundError`, `PermissionError`
- `handlers.py` — handler DRF global que converte exceções de domínio para respostas HTTP padronizadas
- `responses.py` — helpers para respostas de erro padronizadas
- `codes.py` — catálogo de códigos de erro

### Paginação (`core/pagination/`)
- `feed_cursor_pagination.py` — `CursorPagination` para o feed (ordenado por `published_at`)
- `search_pagination.py` — `CursorPagination` para busca
- `default_pagination.py` — `PageNumberPagination` padrão

### Observabilidade
- `logging.py` — configuração de logging estruturado
- `middleware.py` — middleware de log de requisições (método, path, status, tempo de resposta)
- `cache.py` — helpers de cache com prefixo por domínio

### Management Commands (`core/management/commands/`)
- `seed_test.py` — comando `python manage.py seed_test` para popular banco com dados de teste

---

## Infraestrutura

### Configurações (`backend/settings/`)
- `base.py` — configurações compartilhadas: apps instaladas, DRF, JWT (SimpleJWT), CORS, drf-spectacular, logging, cache
- `dev.py` — banco SQLite, storage local, DEBUG=True
- `prod.py` — banco PostgreSQL, storage S3 (`django-storages`), Swagger desabilitado em produção, variáveis de ambiente via `os.environ`

### Docker e CI/CD
- `Dockerfile` — imagem Python com dependências do `requirements.txt`, `collectstatic`
- `.github/workflows/build-and-push.yml` — pipeline GitHub Actions: build da imagem Docker + push para registry

### URLs globais (`backend/urls.py`)
- Roteamento central com prefixos: `/api/v1/accounts/`, `/api/v1/links/`, `/api/v1/posts/`, `/api/v1/search/`
- Swagger UI em `/api/v1/docs/` (apenas em não-produção)

---

## Testes

Suite de testes automatizados com **pytest** + **pytest-django**:

| Arquivo | O que testa |
|---|---|
| `test_signup_flow.py` | Criação de conta e validações de campo |
| `test_elder_me_api.py` | CRUD do perfil do idoso |
| `test_caregiver_me_api.py` | CRUD do perfil do cuidador |
| `test_guardian_me_api.py` | CRUD do perfil do responsável |
| `test_professional_me_api.py` | CRUD do perfil do profissional |
| `test_institution_me_api.py` | CRUD do perfil da instituição |
| `test_caregiver_elder_link_api.py` | Criação de vínculos cuidador ↔ idoso |
| `test_caregiver_elder_link_respond.py` | Aceitar/rejeitar vínculo |
| `test_guardian_elder_link_api.py` | Vínculos responsável ↔ idoso |
| `test_guardian_elder_link_respond.py` | Aceitar/rejeitar vínculo responsável |
| `test_professional_elder_link_api.py` | Vínculos profissional ↔ idoso |
| `test_professional_elder_link_respond.py` | Aceitar/rejeitar vínculo profissional |
| `test_institution_elder_link_respond.py` | Aceitar/rejeitar vínculo instituição |
| `test_elder_links_api.py` | Listagem de vínculos do idoso |
| `test_generic_links_api.py` | Endpoint genérico de links |
| `test_link_list_api.py` | Listagem pública de vínculos |
| `test_my_posts_endpoints.py` | CRUD de posts |
| `posts/test_post_like_api.py` | Like/unlike |
| `posts/test_post_comment_api.py` | CRUD de comentários |
| `test_post_permissions.py` | Permissões de edição de post |
| `test_feed_cache.py` | Cache do feed |
| `test_search_api.py` | Busca de usuários |
| `test_search_filters.py` | Filtros de busca |
| `test_user_address.py` | Campos de endereço no cadastro |
| `test_account_services.py` | Serviços de conta |

---
