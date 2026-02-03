"""
Модуль URL-маршрутов для приложения порталов.
Определяет все эндпоинты для работы с порталами через AJAX.
"""

# Функция для создания URL-маршрутов
from django.urls import path

# Представления из текущего приложения
from . import views

# Пространство имен для URL-маршрутов (используется как portals:dashboard)
app_name = 'portals'

urlpatterns = [
    # Главная страница дашборда с порталами
    path('', views.dashboard, name='dashboard'),
    
    # Создание нового портала (AJAX POST)
    path('portal/create/', views.portal_create, name='portal_create'),
    
    # Обновление существующего портала (AJAX POST)
    path('portal/<int:portal_id>/update/', views.portal_update, name='portal_update'),
    
    # Удаление портала (AJAX POST)
    path('portal/<int:portal_id>/delete/', views.portal_delete, name='portal_delete'),
    
    # Немедленная проверка доступности (AJAX POST)
    path('portal/<int:portal_id>/check/', views.portal_check_now, name='portal_check'),
    
    # Получение статистики доступности (JSON API)
    path('portal/<int:portal_id>/availability/', views.portal_availability, name='portal_availability'),
    
    # Обновление порядка порталов после drag-and-drop (AJAX POST)
    path('portal/reorder/', views.portal_reorder, name='portal_reorder'),
]
