"""
Модуль представлений (views) для приложения порталов.
Содержит AJAX-эндпоинты для CRUD-операций с порталами
и проверки их доступности.
"""

# Функции для рендеринга шаблонов и получения объектов
from django.shortcuts import render, get_object_or_404

# Декоратор для проверки авторизации пользователя
from django.contrib.auth.decorators import login_required

# Класс для возврата JSON-ответов
from django.http import JsonResponse

# Декоратор для ограничения HTTP-методов
from django.views.decorators.http import require_http_methods

# Модуль для работы с JSON-данными
import json

# Модели порталов и проверок доступности
from .models import Portal, PortalAvailability

# Сервисные функции для работы с порталами
from .services import fetch_favicon, check_portal_availability, get_availability_stats


@login_required
def dashboard(request):
    """
    Главная страница дашборда.
    
    Отображает все порталы текущего пользователя,
    отсортированные по позиции и дате создания.
    """
    portals = Portal.objects.filter(user=request.user).order_by('position', '-created_at')
    return render(request, 'portals/dashboard.html', {
        'portals': portals
    })


@login_required
@require_http_methods(["POST"])
def portal_create(request):
    """
    Создание нового портала (AJAX-эндпоинт).
    
    Принимает JSON с данными портала, создает запись в БД,
    загружает favicon и выполняет первую проверку доступности.
    
    Возвращает JSON с данными созданного портала.
    """
    try:
        data = json.loads(request.body)
        
        portal = Portal.objects.create(
            user=request.user,
            title=data.get('title'),
            url=data.get('url'),
            description=data.get('description', ''),
            position=Portal.objects.filter(user=request.user).count()
        )
        
        # Попытка загрузить favicon с сайта
        favicon_file = fetch_favicon(portal.url)
        if favicon_file:
            portal.favicon.save(f'favicon_{portal.id}.png', favicon_file, save=True)
        
        # Первая проверка доступности портала
        check_portal_availability(portal)
        
        return JsonResponse({
            'success': True,
            'portal': {
                'id': portal.id,
                'title': portal.title,
                'url': portal.url,
                'description': portal.description,
                'favicon_url': portal.favicon.url if portal.favicon else None,
                'position': portal.position
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def portal_update(request, portal_id):
    """
    Обновление существующего портала (AJAX-эндпоинт).
    
    Принимает JSON с новыми данными портала.
    Если URL изменился - загружает новый favicon.
    
    Возвращает JSON с обновленными данными портала.
    """
    portal = get_object_or_404(Portal, id=portal_id, user=request.user)
    
    try:
        data = json.loads(request.body)
        
        portal.title = data.get('title', portal.title)
        portal.url = data.get('url', portal.url)
        portal.description = data.get('description', portal.description)
        
        # Если URL изменился, обновляем favicon
        if 'url' in data and data['url'] != portal.url:
            portal.url = data['url']
            favicon_file = fetch_favicon(portal.url)
            if favicon_file:
                portal.favicon.save(f'favicon_{portal.id}.png', favicon_file, save=True)
        
        portal.save()
        
        return JsonResponse({
            'success': True,
            'portal': {
                'id': portal.id,
                'title': portal.title,
                'url': portal.url,
                'description': portal.description,
                'favicon_url': portal.favicon.url if portal.favicon else None
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def portal_delete(request, portal_id):
    """
    Удаление портала (AJAX-эндпоинт).
    
    Удаляет файл favicon и запись портала из БД.
    Вместе с порталом удаляются все связанные проверки доступности.
    """
    portal = get_object_or_404(Portal, id=portal_id, user=request.user)
    
    try:
        # Удаляем файл favicon если он существует
        if portal.favicon:
            try:
                portal.favicon.delete(save=False)
            except Exception:
                pass  # Игнорируем ошибки удаления файла
        
        portal.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def portal_reorder(request):
    """
    Обновление порядка порталов после drag-and-drop (AJAX-эндпоинт).
    
    Принимает JSON со списком ID порталов в новом порядке
    и обновляет поле position для каждого.
    """
    try:
        data = json.loads(request.body)
        portal_ids = data.get('portal_ids', [])
        
        for index, portal_id in enumerate(portal_ids):
            Portal.objects.filter(id=portal_id, user=request.user).update(position=index)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def portal_availability(request, portal_id):
    """
    Получение статистики доступности портала (JSON API).
    
    Возвращает процент доступности, среднее время ответа
    и данные для построения графика за указанный период.
    """
    portal = get_object_or_404(Portal, id=portal_id, user=request.user)
    
    days = int(request.GET.get('days', 7))
    stats = get_availability_stats(portal, days=days)
    
    return JsonResponse({
        'success': True,
        'portal_id': portal.id,
        'portal_title': portal.title,
        'stats': stats
    })


@login_required
@require_http_methods(["POST"])
def portal_check_now(request, portal_id):
    """
    Немедленная проверка доступности портала (AJAX-эндпоинт).
    
    Выполняет HTTP-запрос к порталу и сохраняет результат.
    Используется для ручной проверки по запросу пользователя.
    """
    portal = get_object_or_404(Portal, id=portal_id, user=request.user)
    
    result = check_portal_availability(portal)
    
    return JsonResponse({
        'success': True,
        'portal_id': portal.id,
        'is_available': result['is_available'],
        'response_time': result.get('response_time'),
        'status_code': result.get('status_code')
    })
