"""
Модуль моделей для приложения порталов.
Содержит модели Portal (порталы) и PortalAvailability (проверки доступности).
"""

# Базовый модуль моделей Django
from django.db import models

# Модель пользователя Django для связи с порталами
from django.contrib.auth.models import User

# Валидатор для проверки корректности URL
from django.core.validators import URLValidator


class Portal(models.Model):
    """
    Модель для хранения порталов пользователя.
    
    Каждый портал содержит URL веб-сайта, его название,
    описание, favicon и позицию для сортировки.
    """
    
    # Связь с пользователем-владельцем портала
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='portals', 
        verbose_name='Пользователь'
    )
    
    # Название портала для отображения
    title = models.CharField(max_length=200, verbose_name='Название')
    
    # URL адрес портала с валидацией
    url = models.URLField(max_length=500, verbose_name='URL', validators=[URLValidator()])
    
    # Опциональное описание портала
    description = models.TextField(blank=True, verbose_name='Описание')
    
    # Favicon портала, загружается автоматически
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True, verbose_name='Иконка')
    
    # Позиция для сортировки (drag-and-drop)
    position = models.IntegerField(default=0, verbose_name='Позиция')
    
    # Дата создания записи
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    
    # Дата последнего обновления
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        ordering = ['position', '-created_at']
        verbose_name = 'Портал'
        verbose_name_plural = 'Порталы'
    
    def __str__(self):
        """Возвращает название портала для отображения в админке."""
        return self.title
    
    @property
    def uptime_percentage(self):
        """
        Вычисляет процент доступности портала за последние 7 дней.
        
        Возвращает None если проверок не было,
        иначе возвращает число от 0 до 100.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        checks = self.availability_checks.filter(timestamp__gte=week_ago)
        
        if not checks.exists():
            return None
        
        available_count = checks.filter(is_available=True).count()
        total_count = checks.count()
        
        return round((available_count / total_count) * 100, 1) if total_count > 0 else 0


class PortalAvailability(models.Model):
    """
    Модель для хранения истории проверок доступности порталов.
    
    Каждая запись содержит результат одной проверки:
    был ли портал доступен, время ответа и HTTP-код.
    """
    
    # Связь с проверяемым порталом
    portal = models.ForeignKey(
        Portal, 
        on_delete=models.CASCADE, 
        related_name='availability_checks', 
        verbose_name='Портал'
    )
    
    # Время выполнения проверки
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время проверки')
    
    # Был ли портал доступен при проверке
    is_available = models.BooleanField(verbose_name='Доступен')
    
    # Время ответа сервера в миллисекундах
    response_time = models.FloatField(null=True, blank=True, verbose_name='Время ответа (мс)')
    
    # HTTP статус-код ответа
    status_code = models.IntegerField(null=True, blank=True, verbose_name='HTTP код')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Проверка доступности'
        verbose_name_plural = 'Проверки доступности'
        indexes = [
            # Индекс для быстрого поиска проверок конкретного портала
            models.Index(fields=['portal', '-timestamp']),
        ]
    
    def __str__(self):
        """Возвращает строковое представление для админки."""
        return f"{self.portal.title} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
