# AMPARO — Documentação da API

Plataforma de rede de cuidados voltada para idosos, cuidadores, responsáveis legais, profissionais de saúde e instituições. Desenvolvida com **Django REST Framework** e autenticação via **JWT**.

---

## Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Padrão de Resposta](#padrão-de-resposta)
- [Enums e Tipos](#enums-e-tipos)
- [Rotas de Autenticação](#rotas-de-autenticação)
- [Perfil do Idoso](#perfil-do-idoso)
- [Perfil do Cuidador](#perfil-do-cuidador)
- [Perfil do Responsável](#perfil-do-responsável)
- [Perfil do Profissional de Saúde](#perfil-do-profissional-de-saúde)
- [Perfil da Instituição](#perfil-da-instituição)
- [Posts](#posts)
- [Likes](#likes)
- [Comentários](#comentários)
- [Feed](#feed)
- [Vínculos (Links)](#vínculos-links)
- [Busca](#busca)
- [Health Check](#health-check)

---

## Visão Geral

**Base URL:** `http://localhost:8000/api/v1/`

**Autenticação:** JWT Bearer Token (`Authorization: Bearer <access_token>`)

**Documentação interativa (dev):**
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`

---

## Autenticação

Todos os endpoints (exceto os marcados como **público**) exigem o header:

```
Authorization: Bearer <access_token>
```

O token é obtido via `POST /api/v1/auth/token/` e renovado via `POST /api/v1/auth/token/refresh/`.

---

## Padrão de Resposta

### Sucesso

```json
{
  "success": true,
  "data": { ... }
}
```

### Erro

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Erro de validação nos dados enviados.",
    "details": { ... }
  },
  "request_id": "uuid-do-request"
}
```

---

## Enums e Tipos

### `role` (tipo de usuário)
| Valor | Descrição |
|-------|-----------|
| `ELDER` | Idoso |
| `GUARDIAN` | Responsável |
| `CAREGIVER` | Cuidador |
| `INSTITUTION` | Instituição |
| `PROFESSIONAL` | Profissional de saúde |

### `gender` (ElderProfile)
| Valor | Descrição |
|-------|-----------|
| `MALE` | Masculino |
| `FEMALE` | Feminino |
| `OTHER` | Outro |
| `NOT_INFORMED` | Não informado |

### `mobility_level` (ElderProfile)
| Valor | Descrição |
|-------|-----------|
| `INDEPENDENT` | Independente |
| `NEEDS_ASSISTANCE` | Necessita assistência |
| `WHEELCHAIR` | Cadeira de rodas |
| `BEDRIDDEN` | Acamado |

### `cognitive_status` (ElderProfile)
| Valor | Descrição |
|-------|-----------|
| `LUCID` | Lúcido |
| `MILD_IMPAIRMENT` | Comprometimento leve |
| `DEMENTIA` | Demência |
| `NOT_INFORMED` | Não informado |

### `relationship` (GuardianProfile / GuardianElderLink)
| Valor | Descrição |
|-------|-----------|
| `CHILD` | Filho(a) |
| `SPOUSE` | Cônjuge |
| `SIBLING` | Irmão(ã) |
| `RELATIVE` | Parente |
| `LEGAL_GUARDIAN` | Responsável legal |
| `OTHER` | Outro |

### `profession` (ProfessionalProfile)
| Valor | Descrição |
|-------|-----------|
| `PHYSIOTHERAPIST` | Fisioterapeuta |
| `SPEECH_THERAPIST` | Fonoaudiólogo(a) |
| `OCCUPATIONAL_THERAPIST` | Terapeuta ocupacional |
| `PSYCHOLOGIST` | Psicólogo(a) |
| `NUTRITIONIST` | Nutricionista |
| `OTHER` | Outro |

### `service_mode` (ProfessionalProfile / ProfessionalElderLink)
| Valor | Descrição |
|-------|-----------|
| `HOME` | Domiciliar |
| `CLINIC` | Clínica |
| `ONLINE` | Online |
| `OTHER` | Outro |

### `institution_type` (InstitutionProfile)
| Valor | Descrição |
|-------|-----------|
| `ILPI` | ILPI (Longa Permanência) |
| `SHELTER` | Abrigo |
| `CLINIC` | Clínica |
| `HOSPITAL` | Hospital |
| `OTHER` | Outro |

### `care_types` (CaregiverProfile)
| Valor | Descrição |
|-------|-----------|
| `HOME` | Cuidado domiciliar |
| `HOSPITAL` | Cuidado hospitalar |
| `NIGHT_SHIFT` | Plantão noturno |
| `DAY_SHIFT` | Plantão diurno |
| `COMPANION` | Acompanhante |

### `status` (Vínculos)
| Valor | Descrição | Onde se aplica |
|-------|-----------|----------------|
| `PENDING` | Pendente | Todos |
| `ACTIVE` | Ativo | Todos |
| `ENDED` | Finalizado | Cuidador, Profissional |
| `CANCELLED` | Cancelado | Todos |
| `DISCHARGED` | Alta/saída | Instituição |
| `TRANSFERRED` | Transferido | Instituição |
| `OTHER` | Outro | Instituição |

### `visibility_scope` (Post)
| Valor | Descrição |
|-------|-----------|
| `PUBLIC` | Público |
| `CAREGIVERS` | Apenas cuidadores |
| `ELDERS` | Apenas idosos |
| `INSTITUTIONS` | Apenas instituições |
| `PROFESSIONALS` | Apenas profissionais |
| `GUARDIANS` | Apenas responsáveis |
| `PRIVATE` | Privado |

### `status` (Post)
| Valor | Descrição |
|-------|-----------|
| `DRAFT` | Rascunho |
| `PUBLISHED` | Publicado |
| `ARCHIVED` | Arquivado |
| `BLOCKED` | Bloqueado |
| `DELETED` | Deletado |

---

## Rotas de Autenticação

**Prefixo:** `/api/v1/auth/`

---

### `POST /api/v1/auth/signup/`

> **Público** — Cria uma nova conta de usuário.

**Request Body:**
```json
{
  "email": "usuario@email.com",
  "password": "SenhaSegura123",
  "full_name": "João da Silva",
  "phone": "11987654321",
  "role": "ELDER",
  "address_line": "Rua das Flores, 123",
  "city": "São Paulo",
  "state": "SP",
  "zip_code": "01310100"
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `email` | string | ✅ | Email único |
| `password` | string | ✅ | Senha |
| `full_name` | string | ✅ | Nome completo |
| `phone` | string | ❌ | Telefone |
| `role` | enum | ✅ | Tipo de usuário |
| `address_line` | string | ❌ | Endereço |
| `city` | string | ❌ | Cidade |
| `state` | string | ❌ | UF (2 caracteres) |
| `zip_code` | string | ❌ | CEP (8 dígitos) |

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "usuario@email.com",
    "full_name": "João da Silva",
    "phone": "11987654321",
    "role": "ELDER",
    "address_line": "Rua das Flores, 123",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01310100"
  }
}
```

---

### `POST /api/v1/auth/token/`

> **Público** — Realiza login e retorna tokens JWT.

**Request Body:**
```json
{
  "email": "usuario@email.com",
  "password": "SenhaSegura123"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "access": "<access_token>",
    "refresh": "<refresh_token>"
  }
}
```

---

### `POST /api/v1/auth/token/refresh/`

> **Público** — Renova o access token usando o refresh token.

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response 200:**
```json
{
  "access": "<novo_access_token>"
}
```

---

### `GET /api/v1/auth/me/`

> Retorna os dados do usuário autenticado.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "usuario@email.com",
    "full_name": "João da Silva",
    "phone": "11987654321",
    "role": "ELDER",
    "is_verified": false,
    "address_line": "Rua das Flores, 123",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01310100"
  }
}
```

---

### `PATCH /api/v1/auth/me/`

> Atualiza parcialmente os dados do usuário autenticado.

**Request Body** (todos os campos são opcionais):
```json
{
  "full_name": "João Silva Atualizado",
  "phone": "11999990000",
  "address_line": "Rua Nova, 456",
  "city": "Campinas",
  "state": "SP",
  "zip_code": "13020010"
}
```

**Response 200:** Dados atualizados do usuário (mesmo formato do GET `/me/`).

---

### `POST /api/v1/auth/password/change/`

> Altera a senha do usuário autenticado.

**Request Body:**
```json
{
  "old_password": "SenhaAntiga123",
  "new_password": "NovaSenha456"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": null
}
```

---

## Perfil do Idoso

**Prefixo:** `/api/v1/elders/`  
**Requer role:** `ELDER`

---

### `GET /api/v1/elders/me/`

> Retorna o perfil completo do idoso autenticado.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "preferred_name": "João",
    "birth_date": "1950-05-15",
    "gender": "MALE",
    "mobility_level": "NEEDS_ASSISTANCE",
    "cognitive_status": "LUCID",
    "has_fall_risk": true,
    "needs_medication_support": true,
    "requires_24h_care": false,
    "medical_conditions": "Hipertensão, diabetes tipo 2",
    "allergies": "Penicilina",
    "medications": "Losartana 50mg, Metformina 850mg",
    "medical_notes": "Consulta mensal com cardiologista",
    "emergency_contact_name": "Maria Silva",
    "emergency_contact_phone": "11987654321",
    "emergency_contact_relationship": "Filha",
    "is_active": true
  }
}
```

---

### `PUT /api/v1/elders/me/`

> Atualiza o perfil do idoso (todos os campos).

**Request Body:**
```json
{
  "preferred_name": "João",
  "birth_date": "1950-05-15",
  "gender": "MALE",
  "mobility_level": "NEEDS_ASSISTANCE",
  "cognitive_status": "LUCID",
  "has_fall_risk": true,
  "needs_medication_support": true,
  "requires_24h_care": false,
  "medical_conditions": "Hipertensão, diabetes tipo 2",
  "allergies": "Penicilina",
  "medications": "Losartana 50mg",
  "medical_notes": "Consulta mensal",
  "emergency_contact_name": "Maria Silva",
  "emergency_contact_phone": "11987654321",
  "emergency_contact_relationship": "Filha"
}
```

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `preferred_name` | string | ❌ |
| `birth_date` | date (YYYY-MM-DD) | ❌ |
| `gender` | enum | ❌ |
| `mobility_level` | enum | ✅ |
| `cognitive_status` | enum | ✅ |
| `has_fall_risk` | boolean | ❌ |
| `needs_medication_support` | boolean | ❌ |
| `requires_24h_care` | boolean | ❌ |
| `medical_conditions` | string | ❌ |
| `allergies` | string | ❌ |
| `medications` | string | ❌ |
| `medical_notes` | string | ❌ |
| `emergency_contact_name` | string | ❌ |
| `emergency_contact_phone` | string | ❌ |
| `emergency_contact_relationship` | string | ❌ |

**Response 200:** Dados atualizados (mesmo formato do GET).

---

### `PATCH /api/v1/elders/me/`

> Atualiza parcialmente o perfil do idoso.

**Request Body** (apenas os campos desejados):
```json
{
  "mobility_level": "WHEELCHAIR",
  "has_fall_risk": true
}
```

**Response 200:** Dados atualizados.

---

## Perfil do Cuidador

**Prefixo:** `/api/v1/caregivers/`  
**Requer role:** `CAREGIVER`

---

### `GET /api/v1/caregivers/me/`

> Retorna o perfil do cuidador autenticado.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "bio": "Cuidador com 5 anos de experiência em cuidados domiciliares",
    "experience_years": 5,
    "is_available": true,
    "city": "São Paulo",
    "state": "SP",
    "care_types": ["HOME", "COMPANION"],
    "background_check_status": "verified",
    "documents_verified": true
  }
}
```

---

### `PUT /api/v1/caregivers/me/`

> Atualiza o perfil do cuidador (todos os campos).

**Request Body:**
```json
{
  "bio": "Texto biográfico",
  "experience_years": 5,
  "is_available": true,
  "city": "São Paulo",
  "state": "SP",
  "care_types_input": ["HOME", "NIGHT_SHIFT", "COMPANION"]
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `bio` | string | ❌ | Biografia |
| `experience_years` | integer | ❌ | Anos de experiência |
| `is_available` | boolean | ❌ | Disponível para contratação |
| `city` | string | ❌ | Cidade |
| `state` | string | ❌ | UF (2 caracteres) |
| `care_types_input` | array de enum | ❌ | Tipos de cuidado (substitui todos os anteriores) |

**Response 200:** Dados atualizados.

---

### `PATCH /api/v1/caregivers/me/`

> Atualiza parcialmente o perfil do cuidador.

**Request Body:**
```json
{
  "is_available": false,
  "care_types_input": ["HOME"]
}
```

**Response 200:** Dados atualizados.

---

## Perfil do Responsável

**Prefixo:** `/api/v1/guardians/`  
**Requer role:** `GUARDIAN`

---

### `GET /api/v1/guardians/me/`

> Retorna o perfil do responsável autenticado.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "relationship": "CHILD",
    "is_legal_guardian": true,
    "preferred_contact": "whatsapp"
  }
}
```

---

### `PUT /api/v1/guardians/me/`

> Atualiza o perfil do responsável.

**Request Body:**
```json
{
  "relationship": "CHILD",
  "is_legal_guardian": true,
  "preferred_contact": "email"
}
```

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `relationship` | enum | ✅ |
| `is_legal_guardian` | boolean | ❌ |
| `preferred_contact` | string | ❌ |

**Response 200:** Dados atualizados.

---

### `PATCH /api/v1/guardians/me/`

> Atualiza parcialmente o perfil do responsável.

---

## Perfil do Profissional de Saúde

**Prefixo:** `/api/v1/professionals/`  
**Requer role:** `PROFESSIONAL`

---

### `GET /api/v1/professionals/me/`

> Retorna o perfil do profissional autenticado.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "profession": "PHYSIOTHERAPIST",
    "council": "CREFITO",
    "license_number": "123456-F",
    "bio": "Fisioterapeuta especializado em reabilitação geriátrica",
    "service_mode": "HOME",
    "hourly_rate": "150.00",
    "is_available": true,
    "registration_verified": false,
    "city": "São Paulo",
    "state": "SP"
  }
}
```

---

### `PUT /api/v1/professionals/me/`

> Atualiza o perfil do profissional.

**Request Body:**
```json
{
  "profession": "PHYSIOTHERAPIST",
  "council": "CREFITO",
  "license_number": "123456-F",
  "bio": "Fisioterapeuta especializado em reabilitação geriátrica",
  "service_mode": "HOME",
  "hourly_rate": "150.00",
  "is_available": true,
  "city": "São Paulo",
  "state": "SP"
}
```

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `profession` | enum | ✅ |
| `council` | string | ❌ |
| `license_number` | string | ❌ |
| `bio` | string | ❌ |
| `service_mode` | enum | ✅ |
| `hourly_rate` | decimal | ❌ |
| `is_available` | boolean | ❌ |
| `city` | string | ❌ |
| `state` | string | ❌ |

**Response 200:** Dados atualizados.

---

### `PATCH /api/v1/professionals/me/`

> Atualiza parcialmente o perfil do profissional.

---

## Perfil da Instituição

**Prefixo:** `/api/v1/institutions/`  
**Requer role:** `INSTITUTION`

---

### `GET /api/v1/institutions/me/`

> Retorna o perfil da instituição autenticada.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "legal_name": "ILPI São João Ltda",
    "trade_name": "Lar São João",
    "cnpj": "12345678000190",
    "institution_type": "ILPI",
    "capacity": 80,
    "website": "https://www.saojoao.com.br",
    "license_number": "ALV/2024/123",
    "is_verified": false
  }
}
```

---

### `PUT /api/v1/institutions/me/`

> Atualiza o perfil da instituição.

**Request Body:**
```json
{
  "legal_name": "ILPI São João Ltda",
  "trade_name": "Lar São João",
  "cnpj": "12345678000190",
  "institution_type": "ILPI",
  "capacity": 80,
  "website": "https://www.saojoao.com.br",
  "license_number": "ALV/2024/123"
}
```

| Campo | Tipo | Obrigatório |
|-------|------|-------------|
| `legal_name` | string | ✅ |
| `trade_name` | string | ❌ |
| `cnpj` | string (14 dígitos) | ❌ |
| `institution_type` | enum | ✅ |
| `capacity` | integer | ❌ |
| `website` | URL | ❌ |
| `license_number` | string | ❌ |

**Response 200:** Dados atualizados.

---

### `PATCH /api/v1/institutions/me/`

> Atualiza parcialmente o perfil da instituição.

---

## Posts

**Prefixo:** `/api/v1/posts/my-posts/`

---

### `GET /api/v1/posts/my-posts/`

> Lista os posts do usuário autenticado (paginado).

**Query Params:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `page` | integer | Número da página |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "text": "Conteúdo do post",
      "image": "https://s3.amazonaws.com/bucket/post-images/foto.jpg",
      "image_alt_text": "Descrição da imagem",
      "status": "PUBLISHED",
      "visibility_scope": "PUBLIC",
      "likes_count": 5,
      "comments_count": 2,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "published_at": "2024-01-15T10:30:00Z",
      "edited_at": null
    }
  ]
}
```

---

### `POST /api/v1/posts/my-posts/`

> Cria um novo post. Suporta envio de imagem via `multipart/form-data`.

**Request Body** (`multipart/form-data` ou `application/json`):
```json
{
  "text": "Texto do meu post",
  "image": "<arquivo de imagem (opcional)>",
  "image_alt_text": "Texto alternativo da imagem",
  "status": "PUBLISHED",
  "visibility_scope": "PUBLIC",
  "parent_post": null
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `text` | string | ✅ | Conteúdo do post |
| `image` | arquivo | ❌ | Imagem (upload) |
| `image_alt_text` | string | ❌ | Texto alternativo da imagem |
| `status` | enum | ❌ | Padrão: `PUBLISHED` |
| `visibility_scope` | enum | ❌ | Padrão: `PUBLIC` |
| `parent_post` | integer | ❌ | ID do post original (para repost) |

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "text": "Texto do meu post",
    "image": "https://s3.amazonaws.com/bucket/post-images/foto.jpg",
    "image_alt_text": "Texto alternativo da imagem",
    "status": "PUBLISHED",
    "visibility_scope": "PUBLIC",
    "likes_count": 0,
    "comments_count": 0,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z",
    "published_at": "2024-01-15T11:00:00Z",
    "edited_at": null
  }
}
```

---

### `GET /api/v1/posts/my-posts/{id}/`

> Retorna um post específico do usuário autenticado.

**Response 200:** Dados do post (mesmo formato da listagem).

---

### `PUT /api/v1/posts/my-posts/{id}/`

> Atualiza um post completo.

**Request Body:** Mesmo que o `POST`.

**Response 200:** Dados atualizados do post.

---

### `PATCH /api/v1/posts/my-posts/{id}/`

> Atualiza parcialmente um post.

**Request Body:**
```json
{
  "text": "Texto atualizado",
  "visibility_scope": "CAREGIVERS"
}
```

**Response 200:** Dados atualizados do post.

---

### `DELETE /api/v1/posts/my-posts/{id}/`

> Deleta um post (soft delete — o post recebe status `DELETED`).

**Response 200:**
```json
{
  "success": true,
  "data": null
}
```

---

## Likes

**Prefixo:** `/api/v1/posts/`

---

### `POST /api/v1/posts/like/{post_id}`

> Dá like em um post.

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "post_id": 1,
    "user_id": 3,
    "likes_count": 6,
    "created_at": "2024-01-15T11:15:00Z"
  }
}
```

---

### `DELETE /api/v1/posts/unlike/{post_id}`

> Remove o like de um post.

**Response 204:** Sem conteúdo.

---

## Comentários

**Prefixo:** `/api/v1/posts/`

---

### `GET /api/v1/posts/comment/{post_id}`

> Lista os comentários de um post (cursor pagination).

**Query Params:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `cursor` | string | Cursor para próxima página |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "next": "cD0yMDI0LTAxLTE1",
    "previous": null,
    "results": [
      {
        "id": 1,
        "post_id": 1,
        "user_id": 2,
        "content": "Que post incrível!",
        "created_at": "2024-01-15T11:20:00Z",
        "updated_at": "2024-01-15T11:20:00Z"
      }
    ]
  }
}
```

---

### `POST /api/v1/posts/comment/{post_id}`

> Cria um comentário em um post.

**Request Body:**
```json
{
  "content": "Comentário de até 500 caracteres"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "post_id": 1,
    "user_id": 2,
    "content": "Comentário de até 500 caracteres",
    "comments_count": 3,
    "created_at": "2024-01-15T11:20:00Z",
    "updated_at": "2024-01-15T11:20:00Z"
  }
}
```

---

### `PATCH /api/v1/posts/comment/{post_id}/{comment_id}`

> Atualiza um comentário. Apenas o autor pode editar.

**Request Body:**
```json
{
  "content": "Comentário editado"
}
```

**Response 200:** Dados atualizados do comentário.

---

### `DELETE /api/v1/posts/comment/{post_id}/{comment_id}`

> Deleta um comentário. Apenas o autor pode deletar.

**Response 204:** Sem conteúdo.

---

## Feed

**Prefixo:** `/api/v1/posts/`

---

### `GET /api/v1/posts/feed/`

> Retorna o feed de posts para o usuário autenticado, ordenado por data de publicação (cursor pagination, com cache de 60s).

**Query Params:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `cursor` | string | Cursor para próxima página |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "next": "cD0yMDI0LTAxLTE1",
    "previous": null,
    "results": [
      {
        "id": 1,
        "author_name": "João Silva",
        "text": "Conteúdo do post",
        "image": "https://s3.amazonaws.com/...",
        "image_alt_text": "Descrição da imagem",
        "likes_count": 10,
        "comments_count": 3,
        "created_at": "2024-01-15T10:00:00Z",
        "published_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

## Vínculos (Links)

**Prefixo:** `/api/v1/links/`

Os vínculos representam as relações entre idosos e os outros perfis (cuidadores, responsáveis, profissionais e instituições). Todo novo vínculo é criado com status `PENDING` e deve ser aceito pelo outro lado.

---

### `GET /api/v1/links/`

> Lista todos os vínculos do usuário autenticado (ativos, pendentes e finalizados).

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "link_type": "caregiver",
      "status": "ACTIVE",
      "elder_id": 5,
      "other_party_id": 3,
      "other_party_name": "Maria Cuidadora",
      "other_party_role": "CAREGIVER",
      "created_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

---

### `GET /api/v1/links/{user_id}`

> Lista os vínculos de um usuário específico (somente ativos e finalizados — não inclui pendentes ou cancelados).

**Response 200:** Lista de vínculos (mesmo formato acima).

---

### `POST /api/v1/links/`

> Cria uma solicitação de vínculo. O campo `link_type` define o tipo e os campos adicionais esperados.

**Campos comuns a todos os tipos:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `link_type` | string | ✅ | `"caregiver"`, `"guardian"`, `"professional"`, `"institution"` |
| `elder` | integer | ✅ | ID do `ElderProfile` do idoso |

---

#### Tipo `caregiver`

```json
{
  "link_type": "caregiver",
  "elder": 5,
  "agreed_hourly_rate": "50.00",
  "started_at": "2024-02-01",
  "notes": "Cuidado diurno de segunda a sexta"
}
```

| Campo extra | Tipo | Obrigatório |
|-------------|------|-------------|
| `agreed_hourly_rate` | decimal | ❌ |
| `started_at` | date | ❌ |
| `notes` | string | ❌ |

---

#### Tipo `guardian`

```json
{
  "link_type": "guardian",
  "elder": 5,
  "relationship": "CHILD",
  "is_legal_guardian": true,
  "can_view_medical": true,
  "can_hire": true
}
```

| Campo extra | Tipo | Obrigatório |
|-------------|------|-------------|
| `relationship` | enum | ✅ |
| `is_legal_guardian` | boolean | ❌ |
| `can_view_medical` | boolean | ❌ (padrão: `true`) |
| `can_hire` | boolean | ❌ (padrão: `true`) |

---

#### Tipo `professional`

```json
{
  "link_type": "professional",
  "elder": 5,
  "service_mode": "HOME",
  "goals": "Fisioterapia respiratória 3x por semana",
  "agreed_hourly_rate": "120.00",
  "started_at": "2024-02-01",
  "notes": "Paciente com limitação motora leve"
}
```

| Campo extra | Tipo | Obrigatório |
|-------------|------|-------------|
| `service_mode` | enum | ❌ |
| `goals` | string | ❌ |
| `agreed_hourly_rate` | decimal | ❌ |
| `started_at` | date | ❌ |
| `notes` | string | ❌ |

---

#### Tipo `institution`

```json
{
  "link_type": "institution",
  "elder": 5,
  "admitted_at": "2024-02-01",
  "room": "104",
  "bed": "B",
  "notes": "Idoso com dieta especial"
}
```

| Campo extra | Tipo | Obrigatório |
|-------------|------|-------------|
| `admitted_at` | date | ❌ |
| `room` | string | ❌ |
| `bed` | string | ❌ |
| `notes` | string | ❌ |

---

**Response 201:**
```json
{
  "success": true,
  "status": "success",
  "message": "Vínculo solicitado com sucesso.",
  "data": {
    "id": 10,
    "status": "PENDING"
  }
}
```

---

### `POST /api/v1/links/respond/`

> Aceita ou rejeita uma solicitação de vínculo pendente.

**Request Body:**
```json
{
  "link_type": "caregiver",
  "link_id": 10,
  "action": "approve"
}
```

| Campo | Tipo | Valores aceitos |
|-------|------|-----------------|
| `link_type` | string | `"caregiver"`, `"guardian"`, `"professional"`, `"institution"` |
| `link_id` | integer | ID do vínculo |
| `action` | string | `"approve"` ou `"reject"` |

**Response 200:**
```json
{
  "success": true,
  "status": "success",
  "message": "Vínculo aprovado com sucesso.",
  "data": {
    "id": 10,
    "status": "ACTIVE"
  }
}
```

---

## Busca

**Prefixo:** `/api/v1/search/`

> **Público** — Permite buscar usuários por tipo, nome, cidade, estado e filtros específicos.

---

### `GET /api/v1/search/`

**Query Params Gerais:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `role` | enum | Filtra por tipo de usuário |
| `q` | string | Busca por nome |
| `city` | string | Filtra por cidade |
| `state` | string | Filtra por UF |
| `cursor` | string | Cursor para próxima página |

**Query Params para `role=CAREGIVER`:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `is_available` | boolean | Disponibilidade |
| `experience_years` | integer | Experiência mínima em anos |

**Query Params para `role=PROFESSIONAL`:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `is_available` | boolean | Disponibilidade |
| `profession` | enum | Profissão |
| `service_mode` | enum | Modalidade de atendimento |
| `min_price` | decimal | Valor mínimo por hora |
| `max_price` | decimal | Valor máximo por hora |

**Exemplo de requisição:**
```
GET /api/v1/search/?role=PROFESSIONAL&profession=PHYSIOTHERAPIST&service_mode=HOME&city=São Paulo
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "next": "cD0yMDI0LTAxLTE1",
    "previous": null,
    "role": "PROFESSIONAL",
    "results": [
      {
        "id": 3,
        "role": "PROFESSIONAL",
        "full_name": "Ana Terapeuta",
        "profession": "PHYSIOTHERAPIST",
        "service_mode": "HOME",
        "hourly_rate": "150.00",
        "city": "São Paulo",
        "state": "SP",
        "is_available": true
      }
    ]
  }
}
```

**Exemplo de resultado para `role=ELDER`:**
```json
{
  "id": 5,
  "role": "ELDER",
  "full_name": "João Silva",
  "preferred_name": "João",
  "gender": "MALE",
  "mobility_level": "INDEPENDENT"
}
```

---

## Health Check

### `GET /api/v1/health/`

> **Público** — Verifica se a API está operacional.

**Response 200:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "message": "API de rede de cuidados ativa"
  }
}
```

---

## Códigos de Erro Comuns

| HTTP | Code | Descrição |
|------|------|-----------|
| 400 | `VALIDATION_ERROR` | Dados inválidos no body da requisição |
| 401 | `UNAUTHORIZED` | Token ausente, inválido ou expirado |
| 403 | `FORBIDDEN` | Sem permissão para essa ação |
| 404 | `NOT_FOUND` | Recurso não encontrado |
| 409 | `CONFLICT` | Conflito (ex: vínculo já existente) |
| 500 | `INTERNAL_ERROR` | Erro interno do servidor |
