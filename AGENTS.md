# Repository Guidelines

## Project Structure & Module Organization
- `backend/` holds the Django project (settings in `backend/settings/`, URL routing in `backend/urls.py`).
- `core/` and `accounts/` are Django apps; APIs live in `views/`, serializers in `serializers/`, and URL configs under `urls/`.
- Tests live under app-level `tests/` (example: `core/tests/test_healthcheck.py`) or in `tests.py` within an app.
- OpenAPI/Swagger helpers live in `core/docs/` and `accounts/docs/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: create and activate a local virtualenv.
- `pip install -r requirements.txt`: install runtime and dev dependencies.
- `python manage.py runserver`: run the API locally.
- `python manage.py migrate`: apply database migrations.
- `pytest`: run the test suite (configured by `pytest.ini`).

## Coding Style & Naming Conventions
- Python: 4-space indentation, snake_case for functions/variables, PascalCase for classes.
- Django apps follow the standard layout (`views/`, `serializers/`, `models/`, `urls/`).
- Keep API documentation decorators in `*/docs/*.py` and import them into views.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-django`, `pytest-cov`.
- Test file patterns: `tests.py`, `test_*.py`, `*_tests.py` (see `pytest.ini`).
- Prefer API-level tests using DRF’s `APIClient` (see `core/tests/test_healthcheck.py`).

## Commit & Pull Request Guidelines
- Commit messages are short, sentence-style phrases (e.g., "Setup basico com swagger e pytest").
- PRs should include: a concise description, testing notes (`pytest` output or rationale), and any API/DB changes.

## Configuration & Security
- Settings load `.env` via `python-dotenv` (`backend/settings/base.py`).
- Key env vars: `DJANGO_SECRET_KEY`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`.
- Avoid committing real secrets; keep local overrides in `.env`.

### Teste