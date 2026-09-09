from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from ...models import Event
from ...utils.email_utils import send_reminder_notification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Отправка напоминаний о предстоящих событиях'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Количество дней до события для отправки напоминания'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        tomorrow = timezone.now().date() + timedelta(days=days)
        
        # Находим события, которые начинаются через указанное количество дней
        events = Event.objects.filter(
            status__in=['approved', 'in_progress'],
            planned_start__date=tomorrow
        )
        
        count = 0
        for event in events:
            try:
                send_reminder_notification(event)
                count += 1
                self.stdout.write(f"Напоминание отправлено для заявки #{event.id}")
            except Exception as e:
                self.stderr.write(f"Ошибка для заявки #{event.id}: {e}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Напоминания отправлены для {count} событий')
        )
        