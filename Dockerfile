FROM python:3.13-slim as builder

WORKDIR /app

# Установка system dependencies и poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir poetry

# Копируем только файлы, необходимые для установки зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости poetry в системный python
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main --no-root

# Финальный образ
FROM python:3.13-slim

WORKDIR /app

# Копируем установленные зависимости из builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем остальные файлы проекта
COPY . .

# Настройки окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=university_backend.settings

CMD ["bash", "-c", "\
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --no-input && \
    python manage.py createcachetable && \
    (echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='root').exists() or User.objects.create_superuser('root', '', '1234')\" | python manage.py shell) && \
    gunicorn university_backend.wsgi:application --bind 0.0.0.0:8000"]