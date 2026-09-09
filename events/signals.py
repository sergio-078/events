from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event
from .utils.email_utils import send_submit_notification, send_approve_notification, send_reject_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Event)
def event_status_changed(sender, instance, created, **kwargs):
    """
    Отправка уведомлений при изменении статуса заявки
    """
    if created:
        return
    
    try:
        # Получаем предыдущее состояние
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # Статус изменился
            if instance.status == 'under_review':
                send_submit_notification(instance)
            elif instance.status == 'approved':
                send_approve_notification(instance)
            elif instance.status == 'rejected':
                send_reject_notification(instance)
    except sender.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Ошибка в сигнале status_changed для заявки #{instance.id}: {e}")
        