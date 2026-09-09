from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Event
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Автоматическое обновление статусов событий'
    
    def handle(self, *args, **options):
        now = timezone.now()
        updated_count = 0
        
        # Перевод в статус "Выполняется"
        in_progress_events = Event.objects.filter(
            status='approved',
            planned_start__lte=now,
            planned_end__gte=now
        )
        for event in in_progress_events:
            event.status = 'in_progress'
            event.save()
            updated_count += 1
            self.stdout.write(f"Заявка #{event.id} переведена в статус 'Выполняется'")
        
        # Перевод в статус "Завершена"
        completed_events = Event.objects.filter(
            status='in_progress',
            planned_end__lt=now
        )
        for event in completed_events:
            event.status = 'completed'
            event.save()
            updated_count += 1
            self.stdout.write(f"Заявка #{event.id} переведена в статус 'Завершена'")
        
        self.stdout.write(
            self.style.SUCCESS(f'Обновлено статусов: {updated_count}')
        )
        