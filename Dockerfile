# Usando a versão exata que você está usando localmente
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dependências de sistema para compilar drivers (como o do Postgres)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando para rodar as migrações e subir o servidor 
# (Em produção, as migrações costumam ser um passo separado no CI/CD)

# prod
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]

# dev
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]