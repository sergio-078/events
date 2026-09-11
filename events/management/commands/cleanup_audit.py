from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from events.models import AuditLog


class Command(BaseCommand):
    help = 'Очистка старых записей аудита'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Количество дней хранения записей (по умолчанию 90)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_logs = AuditLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()
        
        if count > 0:
            old_logs.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Удалено {count} записей аудита старше {days} дней')
            )
        else:
            self.stdout.write('Нет записей для удаления')
            