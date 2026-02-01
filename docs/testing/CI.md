# Testes Backend: CI & Performance

Este guia descreve como integrar a suíte de testes ao pipeline de CI e como manter a execução rápida.

## Integração com CI (GitHub Actions)

Exemplo de workflow para o GitHub Actions (`.github/workflows/tests.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: amparo_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: password
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-django pytest-cov pytest-xdist
      
      - name: Run Tests
        env:
          DATABASE_URL: postgres://postgres:password@localhost:5432/amparo_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          pytest --cov=. --cov-report=xml
```

## Dicas de Velocidade

1. **Reuso de Banco de Dados**:
   O flag `--reuse-db` (já configurado no `pytest.ini`) evita recriar o banco em cada execução se o schema não mudou.
   
2. **Execução Paralela**:
   Instale `pytest-xdist` e rode com `pytest -n auto`. Isso distribuirá os testes entre os núcleos da CPU.

3. **Ignorar Migrações**:
   O flag `--nomigrations` faz o Django criar as tabelas diretamente a partir dos modelos, o que é muito mais rápido do que rodar todas as migrações.

4. **Markers**:
   Use markers para rodar apenas o que importa no momento:
   - `pytest -m unit`: Apenas testes rápidos de lógica.
   - `pytest -m "not integration"`: Pula testes que dependem de rede/banco complexo.

## Cobertura (Coverage)
Sempre verifique a cobertura para garantir que caminhos críticos de erro (exception handlers) estão sendo testados:
`pytest --cov=posts --cov=accounts`
