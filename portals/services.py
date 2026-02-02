"""Сервисы для работы с порталами"""
import requests
from urllib.parse import urlparse
from django.core.files.base import ContentFile
from io import BytesIO


def get_domain_from_url(url):
    """Извлекает домен из URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_favicon(url):
    """
    Загружает favicon для указанного URL
    Возвращает ContentFile или None
    """
    domain = get_domain_from_url(url)
    
    # PNG and ICO magic bytes for validation
    PNG_MAGIC = b'\x89PNG'
    ICO_MAGIC = b'\x00\x00\x01\x00'
    GIF_MAGIC = b'GIF'
    JPEG_MAGIC = b'\xff\xd8\xff'
    
    def is_valid_image(content):
        """Check if content starts with valid image magic bytes"""
        if len(content) < 4:
            return False
        return (
            content[:4] == PNG_MAGIC or
            content[:4] == ICO_MAGIC or
            content[:3] == GIF_MAGIC or
            content[:3] == JPEG_MAGIC
        )
    
    # Пробуем несколько вариантов получения favicon
    # Google's favicon service is most reliable, so try it first
    favicon_urls = [
        f"https://www.google.com/s2/favicons?domain={urlparse(url).netloc}&sz=128",  # Google favicon service
        f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={url}&size=128",  # Alternative Google service
        f"{domain}/favicon.ico",
        f"{domain}/favicon.png",
        f"{domain}/apple-touch-icon.png",
    ]
    
    for favicon_url in favicon_urls:
        try:
            response = requests.get(
                favicon_url, 
                timeout=10, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                allow_redirects=True
            )
            
            if response.status_code == 200 and len(response.content) > 100:
                # Validate that this is actually an image
                content_type = response.headers.get('content-type', '').lower()
                
                # Check content-type OR magic bytes
                is_image_type = 'image' in content_type
                has_valid_magic = is_valid_image(response.content)
                
                if is_image_type or has_valid_magic:
                    return ContentFile(response.content, name='favicon.png')
                    
        except Exception as e:
            continue
    
    return None


def check_portal_availability(portal):
    """
    Проверяет доступность портала
    Возвращает словарь с результатами проверки
    """
    from .models import PortalAvailability
    
    try:
        response = requests.get(
            portal.url,
            timeout=10,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        is_available = response.status_code < 500
        response_time = response.elapsed.total_seconds() * 1000  # в миллисекундах
        
        availability = PortalAvailability.objects.create(
            portal=portal,
            is_available=is_available,
            response_time=round(response_time, 2),
            status_code=response.status_code
        )
        
        return {
            'success': True,
            'is_available': is_available,
            'response_time': response_time,
            'status_code': response.status_code
        }
    except Exception as e:
        # Портал недоступен
        availability = PortalAvailability.objects.create(
            portal=portal,
            is_available=False,
            response_time=None,
            status_code=None
        )
        
        return {
            'success': True,
            'is_available': False,
            'response_time': None,
            'status_code': None,
            'error': str(e)
        }


def get_availability_stats(portal, days=7):
    """
    Получает статистику доступности портала за указанное количество дней
    """
    from django.utils import timezone
    from datetime import timedelta
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    checks = portal.availability_checks.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).order_by('timestamp')
    
    if not checks.exists():
        return {
            'uptime_percentage': None,
            'avg_response_time': None,
            'checks_count': 0,
            'available_count': 0,
            'unavailable_count': 0,
            'chart_data': []
        }
    
    available_count = checks.filter(is_available=True).count()
    unavailable_count = checks.filter(is_available=False).count()
    total_count = checks.count()
    
    # Вычисляем среднее время ответа
    response_times = [c.response_time for c in checks if c.response_time is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else None
    
    # Данные для графика (группируем по дням)
    chart_data = []
    for check in checks:
        chart_data.append({
            'timestamp': check.timestamp.isoformat(),
            'is_available': check.is_available,
            'response_time': check.response_time
        })
    
    return {
        'uptime_percentage': round((available_count / total_count) * 100, 1) if total_count > 0 else 0,
        'avg_response_time': round(avg_response_time, 2) if avg_response_time else None,
        'checks_count': total_count,
        'available_count': available_count,
        'unavailable_count': unavailable_count,
        'chart_data': chart_data
    }
