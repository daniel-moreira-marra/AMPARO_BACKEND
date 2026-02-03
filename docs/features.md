# Funcionalidades do Projeto AMPARO

O projeto **AMPARO** é uma plataforma focada no cuidado e monitoramento de idosos, conectando cuidadores, familiares (responsáveis), profissionais de saúde e instituições. Abaixo estão listadas as funcionalidades principais organizadas por módulo.

---

## 1. Infraestrutura e Core
Funcionalidades transversais que garantem a estabilidade e performance do sistema.

- **Health Check**: Endpoint para monitoramento do status da API (`/api/v1/health/`).
- **Middleware de Observabilidade**: Implementação de `RequestIDMiddleware` para rastreamento de requisições.
- **Logging Estruturado**: Logs padronizados com ID de requisição para facilitar o debug.
- **Caching**: Estratégia de cache para o feed de posts visando performance.
- **Paginação Cursorizada**: Implementada para lidar com grandes volumes de dados no feed de forma eficiente.

---

## 2. Autenticação e Segurança
Gerenciamento de acesso e proteção de dados.

- **Tokens JWT**: Autenticação baseada em JSON Web Tokens com fluxo de atualização (`refresh`).
- **Login por E-mail**: Autenticação simplificada utilizando e-mail e senha.
- **Gestão de Perfil (Me)**: Recuperação de dados do usuário logado.
- **Signup**: Registro de novos usuários no sistema.
- **Alteração de Senha**: Fluxo seguro para mudança de credenciais.

---

## 3. Gestão de Perfis de Usuários
O sistema suporta múltiplos papéis, cada um com necessidades específicas.

- **Idoso (Elder)**: Perfil central com histórico e dados de saúde.
- **Cuidador (Caregiver)**: Gestão de atividades diárias e cuidados.
- **Responsável (Guardian)**: Familiares ou responsáveis legais que acompanham o idoso.
- **Profissional (Professional)**: Especialistas (médicos, fisioterapeutas, etc.) vinculados ao cuidado.
- **Instituição (Institution)**: Casas de repouso ou centros de cuidado que gerenciam múltiplos idosos.

---

## 4. Conectividade e Vínculos
Mecânicas para associar usuários aos idosos, permitindo o compartilhamento de informações.

- **Gestão de Vínculos**: Endpoints para criar, listar e remover associações entre cuidadores/profissionais/instituições e os idosos.
- **Permissões Expressivas**: Controle de acesso granular baseado no tipo de vínculo (ex: apenas o dono ou o cuidador ativo pode editar certas informações).

---

## 5. Social e Conteúdo (Posts)
Funcionalidades para comunicação e registro de eventos.

- **Gestão de Posts**: Criação, edição e exclusão de publicações (CRUD de posts).
- **Feed Dinâmico**: Visualização cronológica de atualizações relevantes para o contexto do usuário.
- **Meus Posts**: Filtro para visualização rápida das publicações autorais.

---

*Documento gerado automaticamente em 03/02/2026.*
