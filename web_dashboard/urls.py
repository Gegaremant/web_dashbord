"""
Главный конфигурационный файл URL-маршрутов проекта web_dashboard.
Определяет корневые пути и подключает приложения.
"""

# Модуль администрирования Django
from django.contrib import admin

# Функции для создания URL-маршрутов и подключения приложений
from django.urls import path, include

# Модуль настроек Django
from django.conf import settings

# Функция для раздачи медиа-файлов в режиме разработки
from django.conf.urls.static import static

# Функция для редиректа
from django.shortcuts import redirect


urlpatterns = [
    # Админ-панель Django
    path('admin/', admin.site.urls),
    
    # Редирект с главной страницы на дашборд
    path('', lambda request: redirect('portals:dashboard')),
    
    # Маршруты приложения порталов
    path('dashboard/', include('portals.urls')),
    
    # Маршруты приложения аккаунтов (авторизация)
    path('accounts/', include('accounts.urls')),
]

# Раздача медиа-файлов в режиме разработки (favicon и т.д.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
