"""
Django management command для мониторинга доступности порталов
Запускать через cron каждые 5-15 минут:
*/5 * * * * cd /path/to/project && ./venv/bin/python manage.py monitor_portals
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from portals.models import Portal
from portals.services import check_portal_availability


class Command(BaseCommand):
    help = 'Проверяет доступность всех порталов и сохраняет результаты'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID пользователя для проверки только его порталов',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        
        # Получаем порталы для проверки
        portals = Portal.objects.all()
        if user_id:
            portals = portals.filter(user_id=user_id)
        
        total = portals.count()
        self.stdout.write(f'Начинаю проверку {total} порталов...')
        
        success_count = 0
        fail_count = 0
        
        for portal in portals:
            try:
                result = check_portal_availability(portal)
                
                if result['is_available']:
                    status = f"✓ {portal.title}: ДОСТУПЕН ({result.get('response_time', 'N/A')}ms)"
                    self.stdout.write(self.style.SUCCESS(status))
                    success_count += 1
                else:
                    status = f"✗ {portal.title}: НЕДОСТУПЕН"
                    self.stdout.write(self.style.WARNING(status))
                    fail_count += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при проверке {portal.title}: {str(e)}')
                )
                fail_count += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Проверка завершена:'))
        self.stdout.write(f'  Доступно: {success_count}')
        self.stdout.write(f'  Недоступно: {fail_count}')
        self.stdout.write(f'  Всего: {total}')
