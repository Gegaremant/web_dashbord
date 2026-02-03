"""
Модуль представлений (views) для приложения аккаунтов.
Содержит логику аутентификации и регистрации пользователей.
"""

# Функция для авторизации пользователя в системе
from django.contrib.auth import login

# Базовый класс представления для страницы входа
from django.contrib.auth.views import LoginView

# Готовая форма для создания нового пользователя
from django.contrib.auth.forms import UserCreationForm

# Функции для рендеринга шаблонов и редиректа
from django.shortcuts import render, redirect

# Базовый класс для представлений на основе классов
from django.views import View


class CustomLoginView(LoginView):
    """
    Кастомная страница входа в систему.
    
    Наследует стандартную LoginView Django и настраивает:
    - Кастомный шаблон login.html
    - Автоматический редирект авторизованных пользователей на дашборд
    """
    
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class RegisterView(View):
    """
    Страница регистрации нового пользователя.
    
    Обрабатывает GET-запрос для отображения формы и
    POST-запрос для создания нового аккаунта.
    """
    
    template_name = 'accounts/register.html'
    
    def get(self, request):
        """
        Отображает форму регистрации.
        
        Если пользователь уже авторизован - редиректит на дашборд.
        """
        if request.user.is_authenticated:
            return redirect('portals:dashboard')
        
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """
        Обрабатывает отправку формы регистрации.
        
        При успешной валидации создает пользователя,
        авторизует его и редиректит на дашборд.
        """
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('portals:dashboard')
        
        return render(request, self.template_name, {'form': form})
