from datetime import date

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from ..models import Event, Employee
import logging

logger = logging.getLogger(__name__)


def send_event_notification(event, template_name, subject, recipient_emails, context_extra=None):
    """
    Отправка уведомления о событии
    
    Args:
        event: Объект Event
        template_name: Имя шаблона email
        subject: Тема письма
        recipient_emails: Список email получателей
        context_extra: Дополнительный контекст
    """
    if not recipient_emails:
        logger.warning(f"Нет получателей для уведомления о заявке #{event.id}")
        return
    
    # Базовый контекст
    context = {
        'event': event,
        'event_url': f"{settings.BASE_URL}/events/{event.id}/",
        'status_display': event.get_status_display(),
        'work_name': event.work_name,
        'planned_start': event.planned_start,
        'planned_end': event.planned_end,
        **(context_extra if context_extra else {})
    }
    
    # Рендеринг HTML и текстовой версии
    html_content = render_to_string(f'events/emails/{template_name}.html', context)
    text_content = strip_tags(html_content)
    
    # Отправка письма
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Уведомление отправлено для заявки #{event.id} получателям: {recipient_emails}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления для заявки #{event.id}: {str(e)}")


def get_emails_from_employees(employee_queryset):
    """Получение списка email из queryset сотрудников"""
    emails = []
    for emp in employee_queryset:
        if emp.email:
            emails.append(emp.email)
    return emails


def get_emails_from_users(user_list):
    """Получение списка email из списка пользователей"""
    emails = []
    for user in user_list:
        if user.email:
            emails.append(user.email)
    return emails


def get_managers_emails():
    """Получение email руководителей (пользователей с правами can_approve_event)"""
    from django.contrib.auth.models import User
    users = User.objects.filter(groups__permissions__codename='can_approve_event')
    return [user.email for user in users if user.email]


def send_submit_notification(event):
    """Уведомление при отправке заявки на согласование"""
    subject = f"Новая заявка на согласование #{event.id}"
    
    # Получаем email руководителей
    recipient_emails = get_managers_emails()
    
    # Также можно получить email из поля agreed_with
    if event.agreed_with.exists():
        agreed_emails = get_emails_from_employees(event.agreed_with.all())
        recipient_emails.extend(agreed_emails)
    
    # Убираем дубликаты
    recipient_emails = list(set(recipient_emails))
    
    if recipient_emails:
        send_event_notification(
            event=event,
            template_name='event_submitted',
            subject=subject,
            recipient_emails=recipient_emails,
            context_extra={
                'action_url': f"{settings.BASE_URL}/events/{event.id}/",
                'action_text': 'Перейти к заявке'
            }
        )
    else:
        logger.warning(f"Нет email для уведомления о заявке #{event.id}")


def send_approve_notification(event):
    """Уведомление при согласовании заявки"""
    subject = f"Заявка #{event.id} согласована"
    
    # Уведомляем автора заявки
    recipient_emails = []
    if event.created_by and event.created_by.email:
        recipient_emails.append(event.created_by.email)
    
    # Уведомляем ответственного
    if event.responsible_person and event.responsible_person.email:
        recipient_emails.append(event.responsible_person.email)
    
    # Уведомляем исполнителей
    if event.executors.exists():
        executor_emails = get_emails_from_employees(event.executors.all())
        recipient_emails.extend(executor_emails)
    
    # Убираем дубликаты
    recipient_emails = list(set(recipient_emails))
    
    if recipient_emails:
        send_event_notification(
            event=event,
            template_name='event_approved',
            subject=subject,
            recipient_emails=recipient_emails,
            context_extra={
                'approved_by': event.approved_by.get_full_name() if event.approved_by else 'Неизвестно',
                'approved_at': event.approved_at
            }
        )


def send_reject_notification(event):
    """Уведомление при отправке заявки на доработку"""
    subject = f"Заявка #{event.id} отправлена на доработку"
    
    # Уведомляем автора заявки
    recipient_emails = []
    if event.created_by and event.created_by.email:
        recipient_emails.append(event.created_by.email)
    
    if recipient_emails:
        send_event_notification(
            event=event,
            template_name='event_rejected',
            subject=subject,
            recipient_emails=recipient_emails,
            context_extra={
                'revision_reason': event.revision_reason or 'Причина не указана'
            }
        )


def send_reminder_notification(event):
    """Напоминание о предстоящей заявке (за день)"""
    subject = f"Напоминание: заявка #{event.id} на {event.planned_start|date:'d.m.Y'}"
    
    recipient_emails = []
    
    # Уведомляем автора
    if event.created_by and event.created_by.email:
        recipient_emails.append(event.created_by.email)
    
    # Уведомляем ответственного
    if event.responsible_person and event.responsible_person.email:
        recipient_emails.append(event.responsible_person.email)
    
    # Уведомляем исполнителей
    if event.executors.exists():
        executor_emails = get_emails_from_employees(event.executors.all())
        recipient_emails.extend(executor_emails)
    
    # Убираем дубликаты
    recipient_emails = list(set(recipient_emails))
    
    if recipient_emails:
        send_event_notification(
            event=event,
            template_name='event_reminder',
            subject=subject,
            recipient_emails=recipient_emails,
            context_extra={
                'days_until': (event.planned_start.date() - timezone.now().date()).days
            }
        )
