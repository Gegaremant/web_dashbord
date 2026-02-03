"""
Модуль сервисов для работы с порталами.
Содержит функции для загрузки favicon, проверки доступности
и получения статистики.
"""

# Библиотека для выполнения HTTP-запросов
import requests

# Функция для разбора URL на компоненты
from urllib.parse import urlparse

# Класс для создания файлового объекта из байтов
from django.core.files.base import ContentFile


def get_domain_from_url(url):
    """
    Извлекает базовый домен из полного URL.
    
    Пример: https://example.com/page -> https://example.com
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_favicon(url):
    """
    Загружает favicon для указанного URL сайта.
    
    Пробует несколько источников:
    1. Google Favicon API (самый надежный)
    2. Прямые пути к favicon на сайте
    
    Возвращает ContentFile с изображением или None если не удалось загрузить.
    """
    domain = get_domain_from_url(url)
    
    # Магические байты для определения типа изображения
    PNG_MAGIC = b'\x89PNG'      # PNG файлы начинаются с этих байт
    ICO_MAGIC = b'\x00\x00\x01\x00'  # ICO файлы
    GIF_MAGIC = b'GIF'          # GIF файлы
    JPEG_MAGIC = b'\xff\xd8\xff'    # JPEG файлы
    
    def is_valid_image(content):
        """
        Проверяет, является ли содержимое валидным изображением
        по магическим байтам в начале файла.
        """
        if len(content) < 4:
            return False
        return (
            content[:4] == PNG_MAGIC or
            content[:4] == ICO_MAGIC or
            content[:3] == GIF_MAGIC or
            content[:3] == JPEG_MAGIC
        )
    
    # Список URL для попытки загрузки favicon
    favicon_urls = [
        # Google Favicon API - самый надежный источник
        f"https://www.google.com/s2/favicons?domain={urlparse(url).netloc}&sz=128",
        # Альтернативный Google сервис
        f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={url}&size=128",
        # Прямые пути на сайте
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
            
            # Проверяем успешность запроса и минимальный размер
            if response.status_code == 200 and len(response.content) > 100:
                content_type = response.headers.get('content-type', '').lower()
                
                # Проверяем тип контента или магические байты
                is_image_type = 'image' in content_type
                has_valid_magic = is_valid_image(response.content)
                
                if is_image_type or has_valid_magic:
                    return ContentFile(response.content, name='favicon.png')
                    
        except Exception:
            continue
    
    return None


def check_portal_availability(portal):
    """
    Проверяет доступность портала выполнением HTTP-запроса.
    
    Сохраняет результат проверки в БД и возвращает словарь:
    - is_available: доступен ли портал
    - response_time: время ответа в мс
    - status_code: HTTP код ответа
    """
    # Импортируем модель здесь для избежания циклических импортов
    from .models import PortalAvailability
    
    try:
        response = requests.get(
            portal.url,
            timeout=10,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        # Считаем доступным если статус меньше 500 (серверных ошибок)
        is_available = response.status_code < 500
        response_time = response.elapsed.total_seconds() * 1000  # в миллисекундах
        
        # Сохраняем результат проверки в БД
        PortalAvailability.objects.create(
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
        # Портал недоступен (таймаут, ошибка DNS и т.д.)
        PortalAvailability.objects.create(
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
    Получает статистику доступности портала за указанный период.
    
    Возвращает словарь с:
    - uptime_percentage: процент времени доступности
    - avg_response_time: среднее время ответа
    - checks_count: общее количество проверок
    - chart_data: данные для построения графика
    """
    # Импорты для работы с датами
    from django.utils import timezone
    from datetime import timedelta
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Получаем все проверки за период
    checks = portal.availability_checks.filter(
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).order_by('timestamp')
    
    # Если проверок нет - возвращаем пустую статистику
    if not checks.exists():
        return {
            'uptime_percentage': None,
            'avg_response_time': None,
            'checks_count': 0,
            'available_count': 0,
            'unavailable_count': 0,
            'chart_data': []
        }
    
    # Подсчет успешных и неуспешных проверок
    available_count = checks.filter(is_available=True).count()
    unavailable_count = checks.filter(is_available=False).count()
    total_count = checks.count()
    
    # Вычисляем среднее время ответа (только для успешных проверок)
    response_times = [c.response_time for c in checks if c.response_time is not None]
    avg_response_time = sum(response_times) / len(response_times) if response_times else None
    
    # Данные для графика
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
