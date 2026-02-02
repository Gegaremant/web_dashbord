from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Portal, PortalAvailability
from .forms import PortalForm
from .services import fetch_favicon, check_portal_availability, get_availability_stats


@login_required
def dashboard(request):
    """Главная страница дашборда"""
    portals = Portal.objects.filter(user=request.user).order_by('position', '-created_at')
    return render(request, 'portals/dashboard.html', {
        'portals': portals
    })


@login_required
@require_http_methods(["POST"])
def portal_create(request):
    """Создание нового портала (AJAX)"""
    try:
        data = json.loads(request.body)
        
        portal = Portal.objects.create(
            user=request.user,
            title=data.get('title'),
            url=data.get('url'),
            description=data.get('description', ''),
            position=Portal.objects.filter(user=request.user).count()
        )
        
        # Попытка загрузить favicon
        favicon_file = fetch_favicon(portal.url)
        if favicon_file:
            portal.favicon.save(f'favicon_{portal.id}.png', favicon_file, save=True)
        
        # Первая проверка доступности
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
    """Обновление портала (AJAX)"""
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
    """Удаление портала (AJAX)"""
    portal = get_object_or_404(Portal, id=portal_id, user=request.user)
    
    try:
        portal.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def portal_reorder(request):
    """Обновление порядка порталов после drag-and-drop (AJAX)"""
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
    """Получение данных о доступности портала (JSON API)"""
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
    """Проверить доступность портала прямо сейчас (AJAX)"""
    portal = get_object_or_404(Portal, id=portal_id, user=request.user)
    
    result = check_portal_availability(portal)
    
    return JsonResponse({
        'success': True,
        'portal_id': portal.id,
        'is_available': result['is_available'],
        'response_time': result.get('response_time'),
        'status_code': result.get('status_code')
    })
