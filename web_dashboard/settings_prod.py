"""
Продакшен-настройки Django для Web Dashboard.

Этот файл импортирует базовые настройки и переопределяет их
для безопасного развертывания в продакшен.
"""

# Импортируем все настройки из основного файла
from .settings import *
import os

# ============================================================================
# БЕЗОПАСНОСТЬ
# ============================================================================

# Выключаем режим отладки
DEBUG = False

# Секретный ключ из переменной окружения (или значение по умолчанию для тестов)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-production-secret-key-here-change-me!')

# Разрешенные хосты
ALLOWED_HOSTS = [
    'dashbord.gegaremant.ru',
    'localhost',
    '127.0.0.1',
    '155.212.166.17',
]

# CSRF доверенные источники
CSRF_TRUSTED_ORIGINS = [
    'https://dashbord.gegaremant.ru',
    'http://dashbord.gegaremant.ru',
    'http://localhost:4213',
    'http://127.0.0.1:4213',
    'http://155.212.166.17:4213',
]


# ============================================================================
# СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ
# ============================================================================

# Директория для собранной статики
STATIC_ROOT = '/app/staticfiles'

# Директория для медиа файлов
MEDIA_ROOT = '/app/media'


# ============================================================================
# БАЗА ДАННЫХ
# ============================================================================

# Путь к базе данных внутри контейнера (монтируется как volume)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/app/data/db.sqlite3',
    }
}


# ============================================================================
# БЕЗОПАСНОСТЬ (дополнительные настройки)
# ============================================================================

# Защита куков
SESSION_COOKIE_SECURE = False  # True если используете HTTPS
CSRF_COOKIE_SECURE = False     # True если используете HTTPS

# X-Frame-Options
X_FRAME_OPTIONS = 'DENY'

# Content-Type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS фильтр браузера
SECURE_BROWSER_XSS_FILTER = True


# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
