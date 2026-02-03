#!/bin/bash
# ============================================================================
# Скрипт развертывания Web Dashboard
# Запуск: ./deploy.sh
# ============================================================================

set -e

echo "🚀 Развертывание Web Dashboard..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Создание директорий для данных
echo "📁 Создание директорий..."
mkdir -p data media

# Копирование базы данных (если существует)
if [ -f "db.sqlite3" ] && [ ! -f "data/db.sqlite3" ]; then
    echo "📦 Копирование базы данных..."
    cp db.sqlite3 data/db.sqlite3
fi

# Генерация секретного ключа если не задан
if [ -z "$DJANGO_SECRET_KEY" ]; then
    export DJANGO_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || echo "change-this-secret-key-in-production")
    echo "🔑 Сгенерирован SECRET_KEY: $DJANGO_SECRET_KEY"
fi

# Сборка Docker образа
echo "🔨 Сборка Docker образа..."
docker build -t web_dashboard:latest .

# Остановка существующего контейнера (если есть)
echo "🛑 Остановка существующего контейнера..."
docker stop web_dashboard 2>/dev/null || true
docker rm web_dashboard 2>/dev/null || true

# Запуск контейнера
echo "🚀 Запуск контейнера..."
docker run -d \
    --name web_dashboard \
    --restart unless-stopped \
    -p 4213:4213 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/media:/app/media \
    -e DJANGO_SECRET_KEY="$DJANGO_SECRET_KEY" \
    web_dashboard:latest

# Ожидание запуска
echo "⏳ Ожидание запуска приложения..."
sleep 5

# Применение миграций
echo "📊 Применение миграций..."
docker exec web_dashboard python manage.py migrate --settings=web_dashboard.settings_prod

# Проверка статуса
if docker ps | grep -q web_dashboard; then
    echo ""
    echo "✅ Web Dashboard успешно развернут!"
    echo ""
    echo "📍 Доступ:"
    echo "   - http://localhost:4213"
    echo "   - http://127.0.0.1:4213"
    echo "   - http://155.212.166.17:4213"
    echo "   - http://dashbord.gegaremant.ru:4213"
    echo ""
    echo "📋 Полезные команды:"
    echo "   docker logs -f web_dashboard    - просмотр логов"
    echo "   docker stop web_dashboard       - остановка"
    echo "   docker start web_dashboard      - запуск"
    echo "   docker restart web_dashboard    - перезапуск"
else
    echo "❌ Ошибка запуска контейнера. Проверьте логи: docker logs web_dashboard"
    exit 1
fi
