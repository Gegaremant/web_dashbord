from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    """Кастомная страница входа"""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class RegisterView(View):
    """Страница регистрации"""
    template_name = 'accounts/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('portals:dashboard')
        
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('portals:dashboard')
        
        return render(request, self.template_name, {'form': form})
