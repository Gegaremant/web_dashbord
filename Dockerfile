# ============================================================================
# Dockerfile для Web Dashboard
# Сборка продакшен-контейнера с Django + Gunicorn + Nginx
# ============================================================================

# Используем Python 3.12 на Alpine Linux для минимального размера
FROM python:3.12-alpine

# Устанавливаем метаданные
LABEL maintainer="gegaremant"
LABEL description="Web Dashboard - Django application"

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=web_dashboard.settings_prod

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apk add --no-cache \
    nginx \
    supervisor \
    jpeg-dev \
    zlib-dev \
    libjpeg \
    openssl \
    && rm -rf /var/cache/apk/*

# Создаем пользователя для запуска приложения
RUN adduser -D -u 1000 appuser

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Копируем код приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p /app/staticfiles /app/media /var/log/supervisor /run/nginx

# Копируем конфигурацию Nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Копируем конфигурацию Supervisor
COPY docker/supervisord.conf /etc/supervisord.conf

# Собираем статические файлы
RUN python manage.py collectstatic --noinput --settings=web_dashboard.settings_prod

# Устанавливаем права доступа
RUN chown -R appuser:appuser /app /var/log/supervisor /run/nginx /var/lib/nginx

# Открываем порт
EXPOSE 4213

# Запускаем через Supervisor (Nginx + Gunicorn)
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
