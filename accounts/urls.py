"""
Модуль URL-маршрутов для приложения аккаунтов.
Определяет пути для авторизации, регистрации и выхода из системы.
"""

# Встроенные представления аутентификации Django (для LogoutView)
from django.contrib.auth import views as auth_views

# Функция для создания URL-маршрутов
from django.urls import path

# Представления из текущего приложения
from . import views

# Пространство имен для URL-маршрутов (используется как accounts:login)
app_name = 'accounts'

urlpatterns = [
    # Страница входа в систему
    path('login/', views.CustomLoginView.as_view(), name='login'),
    
    # Страница регистрации нового пользователя
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Выход из системы (используется встроенный LogoutView)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
