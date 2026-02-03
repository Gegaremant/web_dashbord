"""
Модуль конфигурации админ-панели для приложения порталов.
Регистрирует модели Portal и PortalAvailability в админке Django.
"""

# Модуль администрирования Django
from django.contrib import admin

# Модели приложения порталов
from .models import Portal, PortalAvailability


@admin.register(Portal)
class PortalAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели Portal в админ-панели.
    
    Отображает таблицу порталов с основными полями,
    фильтрацией и поиском.
    """
    
    # Колонки в списке порталов
    list_display = ['title', 'url', 'user', 'position', 'created_at']
    
    # Фильтры в боковой панели
    list_filter = ['user', 'created_at']
    
    # Поля для поиска
    search_fields = ['title', 'url', 'description']
    
    # Сортировка по умолчанию
    ordering = ['position', '-created_at']


@admin.register(PortalAvailability)
class PortalAvailabilityAdmin(admin.ModelAdmin):
    """
    Настройка отображения модели PortalAvailability в админ-панели.
    
    Отображает историю проверок доступности с фильтрацией
    по статусу и порталу.
    """
    
    # Колонки в списке проверок
    list_display = ['portal', 'timestamp', 'is_available', 'response_time', 'status_code']
    
    # Фильтры в боковой панели  
    list_filter = ['is_available', 'timestamp', 'portal']
    
    # Сортировка по времени (новые сверху)
    ordering = ['-timestamp']
