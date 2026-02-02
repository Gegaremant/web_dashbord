from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator


class Portal(models.Model):
    """Модель для хранения порталов пользователя"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portals', verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Название')
    url = models.URLField(max_length=500, verbose_name='URL', validators=[URLValidator()])
    description = models.TextField(blank=True, verbose_name='Описание')
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True, verbose_name='Иконка')
    position = models.IntegerField(default=0, verbose_name='Позиция')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    
    class Meta:
        ordering = ['position', '-created_at']
        verbose_name = 'Портал'
        verbose_name_plural = 'Порталы'
    
    def __str__(self):
        return self.title
    
    @property
    def uptime_percentage(self):
        """Вычисляет процент доступности за последние 7 дней"""
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
    """Модель для хранения истории проверок доступности порталов"""
    portal = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name='availability_checks', verbose_name='Портал')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время проверки')
    is_available = models.BooleanField(verbose_name='Доступен')
    response_time = models.FloatField(null=True, blank=True, verbose_name='Время ответа (мс)')
    status_code = models.IntegerField(null=True, blank=True, verbose_name='HTTP код')
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Проверка доступности'
        verbose_name_plural = 'Проверки доступности'
        indexes = [
            models.Index(fields=['portal', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.portal.title} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
