"""
Настройки Django для проекта web_dashboard.

Этот файл содержит все конфигурации проекта:
- Подключение приложений
- Настройки базы данных
- Аутентификация
- Статические и медиа файлы
- Локализация

Документация: https://docs.djangoproject.com/en/5.0/ref/settings/
"""

# Модуль для работы с путями файловой системы
from pathlib import Path


# ============================================================================
# БАЗОВЫЕ НАСТРОЙКИ
# ============================================================================

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ для криптографических операций Django
# ВАЖНО: В продакшене необходимо использовать переменную окружения!
SECRET_KEY = 'django-insecure-gb-t8&j$_#%08j18$6uo*p0#=zo^zaoab7*3&o(dv#^vvi3+4k'

# Режим отладки - отключить в продакшене!
DEBUG = True

# Список разрешенных хостов (заполнить для продакшена)
ALLOWED_HOSTS = []


# ============================================================================
# ПРИЛОЖЕНИЯ
# ============================================================================

INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',       # Админ-панель
    'django.contrib.auth',        # Аутентификация пользователей
    'django.contrib.contenttypes',# Система типов контента
    'django.contrib.sessions',    # Сессии пользователей
    'django.contrib.messages',    # Система сообщений
    'django.contrib.staticfiles', # Раздача статических файлов
    
    # Приложения проекта
    'portals',                    # Управление порталами
    'accounts',                   # Аутентификация и регистрация
    
    # Сторонние библиотеки
    'widget_tweaks',              # Кастомизация виджетов форм
]


# ============================================================================
# MIDDLEWARE (Промежуточное ПО)
# ============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',          # Защита
    'django.contrib.sessions.middleware.SessionMiddleware',   # Сессии
    'django.middleware.common.CommonMiddleware',              # Общие операции
    'django.middleware.csrf.CsrfViewMiddleware',              # CSRF защита
    'django.contrib.auth.middleware.AuthenticationMiddleware',# Аутентификация
    'django.contrib.messages.middleware.MessageMiddleware',   # Сообщения
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Защита от clickjacking
]


# ============================================================================
# URL И ШАБЛОНЫ
# ============================================================================

# Главный URL модуль
ROOT_URLCONF = 'web_dashboard.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI приложение для развертывания
WSGI_APPLICATION = 'web_dashboard.wsgi.application'


# ============================================================================
# БАЗА ДАННЫХ
# ============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # SQLite для разработки
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================================================
# ВАЛИДАЦИЯ ПАРОЛЕЙ
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================================
# ЛОКАЛИЗАЦИЯ
# ============================================================================

# Язык интерфейса - русский
LANGUAGE_CODE = 'ru-ru'

# Часовой пояс - Москва
TIME_ZONE = 'Europe/Moscow'

# Включить интернационализацию
USE_I18N = True

# Использовать часовые пояса
USE_TZ = True


# ============================================================================
# СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ
# ============================================================================

# URL для статических файлов (CSS, JS, изображения)
STATIC_URL = '/static/'

# Директория для сбора статики (collectstatic)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Дополнительные директории со статическими файлами
STATICFILES_DIRS = [BASE_DIR / 'static']

# URL для медиа файлов (загруженные пользователями)
MEDIA_URL = '/media/'

# Директория для хранения медиа файлов
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================================
# АУТЕНТИФИКАЦИЯ
# ============================================================================

# URL страницы входа
LOGIN_URL = 'accounts:login'

# URL редиректа после успешного входа
LOGIN_REDIRECT_URL = 'portals:dashboard'

# URL редиректа после выхода
LOGOUT_REDIRECT_URL = 'accounts:login'


# ============================================================================
# ПРОЧИЕ НАСТРОЙКИ
# ============================================================================

# Тип автоматического первичного ключа
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
