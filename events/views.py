# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.utils import timezone
from django.db.models import Q

from .models import Event, EventDocument, TechCardStep
from .forms import (
    EventForm,
    EventDocumentForm,
    TechCardStepFormSet,
)
from .decorators import group_required, permission_required as perm_required, event_owner_or_permission
from .utils.email_utils import (
    send_submit_notification,
    send_approve_notification,
    send_reject_notification
)
import logging

logger = logging.getLogger(__name__)


class EventListView(LoginRequiredMixin, ListView):
    """Реестр заявок с фильтрацией"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Базовые оптимизации
        queryset = queryset.select_related(
            'created_by', 'approved_by', 'responsible_person'
        ).prefetch_related(
            'affected_services', 'device_types', 'devices',
            'organizations', 'departments', 'units'
        )

        # Если пользователь не администратор и не в ГДУ, показываем только свои заявки
        if not (self.request.user.is_superuser or
                self.request.user.groups.filter(name='Группа ГДУ').exists()):
            queryset = queryset.filter(created_by=self.request.user)

        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Фильтр по дате
        filter_type = self.request.GET.get('filter')
        today = timezone.now().date()

        if filter_type == 'today':
            queryset = queryset.filter(planned_start__date=today)
        elif filter_type == 'upcoming':
            queryset = queryset.filter(
                planned_start__date__gte=today,
                status__in=['draft', 'under_review', 'approved', 'in_progress']
            )
        elif filter_type == 'past':
            queryset = queryset.filter(planned_end__date__lt=today)
        elif filter_type == 'period':
            date_from = self.request.GET.get('date_from')
            date_to = self.request.GET.get('date_to')
            if date_from and date_to:
                queryset = queryset.filter(
                    planned_start__date__gte=date_from,
                    planned_start__date__lte=date_to
                )

        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(work_name__icontains=search_query) |
                Q(work_description__icontains=search_query) |
                Q(id__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Event.EventStatus.choices
        context['current_filter'] = self.request.GET.get('filter', 'upcoming')
        context['search_query'] = self.request.GET.get('q', '')

        # Проверка прав для кнопок действий
        context['can_approve'] = (
            self.request.user.is_superuser or
            self.request.user.has_perm('events.can_approve_event')
        )

        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр заявки"""
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'created_by', 'approved_by', 'responsible_person',
            'object_location', 'object_outside_location',
            'work_location', 'work_outside_location'
        ).prefetch_related(
            'affected_services', 'device_types', 'devices',
            'materials', 'organizations', 'departments', 'units',
            'executors', 'joint_workers', 'agreed_with', 'notified_persons',
            'tech_card_steps', 'tech_cards', 'documents'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Проверка прав
        event = self.object
        context['can_edit'] = (
            event.status in [Event.EventStatus.DRAFT, Event.EventStatus.REJECTED] and
            (event.created_by == self.request.user or
             self.request.user.is_superuser or
             self.request.user.has_perm('events.can_approve_event'))
        )
        context['can_approve'] = (
            self.request.user.is_superuser or
            self.request.user.has_perm('events.can_approve_event')
        )
        context['can_delete'] = (
            event.status == Event.EventStatus.DRAFT and
            (event.created_by == self.request.user or self.request.user.is_superuser)
        )

        return context


class EventCreateView(LoginRequiredMixin, CreateView):
    """Создание заявки"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tech_card_formset'] = TechCardStepFormSet(
                self.request.POST, instance=self.object, prefix='tech_card'
            )
        else:
            context['tech_card_formset'] = TechCardStepFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        context = self.get_context_data()
        tech_card_formset = context['tech_card_formset']

        if tech_card_formset.is_valid():
            self.object = form.save()
            tech_card_formset.instance = self.object
            tech_card_formset.save()
            messages.success(self.request, 'Заявка успешно создана')
            return redirect('events:event_detail', pk=self.object.pk)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование заявки (только для владельца или администратора)"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            status__in=[Event.EventStatus.DRAFT, Event.EventStatus.REJECTED]
        )
        # Только владелец или администратор
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tech_card_formset'] = TechCardStepFormSet(
                self.request.POST, instance=self.object, prefix='tech_card'
            )
        else:
            context['tech_card_formset'] = TechCardStepFormSet(instance=self.object, prefix='tech_card')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        tech_card_formset = context['tech_card_formset']

        if tech_card_formset.is_valid():
            self.object = form.save()
            tech_card_formset.instance = self.object
            tech_card_formset.save()
            if not self.object.is_tech_card_required:
                self.object.tech_card_steps.all().delete()
            else:
                for i, step in enumerate(self.object.tech_card_steps.order_by('created_at', 'id'), start=1):
                    if step.step_number != i:
                        # обход unique_together: временно в минус
                        TechCardStep.objects.filter(pk=step.pk).update(step_number=-i)
                for i, step in enumerate(self.object.tech_card_steps.order_by('created_at', 'id'), start=1):
                    TechCardStep.objects.filter(pk=step.pk).update(step_number=i)
            messages.success(self.request, 'Заявка успешно обновлена!')
            return redirect('events:event_detail', pk=self.object.pk)

        return self.form_invalid(form)


@login_required
def event_submit(request, pk):
    """Отправка заявки на согласование (автор или администратор)"""
    event = get_object_or_404(Event, pk=pk)

    if event.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для отправки этой заявки на согласование')
        return redirect('events:event_detail', pk=pk)

    if event.status != Event.EventStatus.DRAFT:
        messages.error(request, 'Нельзя отправить на согласование заявку не в статусе "Черновик"')
        return redirect('events:event_detail', pk=pk)

    event.status = Event.EventStatus.UNDER_REVIEW
    event.submitted_at = timezone.now()
    event.save()

    try:
        send_submit_notification(event)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

    messages.success(request, 'Заявка отправлена на согласование')
    return redirect('events:event_detail', pk=pk)


@permission_required('events.can_approve_event', raise_exception=True)
def event_approve(request, pk):
    """Согласование заявки (только для ГДУ)"""
    event = get_object_or_404(Event, pk=pk)

    if event.status != Event.EventStatus.UNDER_REVIEW:
        messages.error(request, 'Нельзя согласовать заявку не в статусе "На согласовании"')
        return redirect('events:event_detail', pk=pk)

    event.status = Event.EventStatus.APPROVED
    event.approved_by = request.user
    event.approved_at = timezone.now()
    event.save()

    try:
        send_approve_notification(event)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

    messages.success(request, 'Заявка согласована')
    return redirect('events:event_detail', pk=pk)


@permission_required('events.can_approve_event', raise_exception=True)
def event_reject(request, pk):
    """Отправка заявки на доработку (только для ГДУ)"""
    event = get_object_or_404(Event, pk=pk)

    if event.status != Event.EventStatus.UNDER_REVIEW:
        messages.error(request, 'Нельзя отправить на доработку заявку не в статусе "На согласовании"')
        return redirect('events:event_detail', pk=pk)

    revision_reason = request.POST.get('revision_reason', '')
    if not revision_reason:
        messages.error(request, 'Необходимо указать причину отправки на доработку')
        return redirect('events:event_detail', pk=pk)

    event.status = Event.EventStatus.REJECTED
    event.revision_reason = revision_reason
    event.save()

    try:
        send_reject_notification(event)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

    messages.success(request, 'Заявка отправлена на доработку')
    return redirect('events:event_detail', pk=pk)


@event_owner_or_permission('events.can_approve_event')
def event_cancel(request, pk):
    """Отмена заявки"""
    event = get_object_or_404(Event, pk=pk)

    if event.status in [Event.EventStatus.COMPLETED, Event.EventStatus.CANCELLED]:
        messages.error(request, 'Нельзя отменить завершенную или уже отмененную заявку')
        return redirect('events:event_detail', pk=pk)

    event.status = Event.EventStatus.CANCELLED
    event.save()

    messages.success(request, 'Заявка отменена')
    return redirect('events:event_detail', pk=pk)


@login_required
def add_document(request, pk):
    """Добавление документа к заявке"""
    event = get_object_or_404(Event, pk=pk)

    # Проверяем права
    if event.created_by != request.user and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав для добавления документов к этой заявке')
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        form = EventDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.event = event
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Документ успешно загружен')
        else:
            messages.error(request, 'Ошибка при загрузке документа')

    return redirect('events:event_detail', pk=pk)


@login_required
def delete_document(request, pk):
    """Удаление документа"""
    document = get_object_or_404(EventDocument, pk=pk)
    event_pk = document.event.pk

    # Проверяем права
    if document.uploaded_by != request.user and not request.user.is_superuser:
        messages.error(request, 'У вас нет прав на удаление этого документа')
        return redirect('events:event_detail', pk=event_pk)

    document.delete()
    messages.success(request, 'Документ удален')
    return redirect('events:event_detail', pk=event_pk)


@login_required
def complete_event(request, pk):
    """Завершение работ по заявке"""
    event = get_object_or_404(Event, pk=pk)

    # Проверка прав
    if (event.created_by != request.user
            and not request.user.is_superuser
            and not request.user.has_perm('events.can_approve_event')):
        messages.error(request, 'У вас нет прав для завершения этой заявки')
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        # Получаем фактические данные из формы
        actual_start = request.POST.get('actual_start')
        actual_end = request.POST.get('actual_end')
        actual_disruption_start = request.POST.get('actual_disruption_start')
        actual_disruption_end = request.POST.get('actual_disruption_end')
        work_done = request.POST.get('work_done')
        comments = request.POST.get('comments')

        # Обновляем заявку
        if actual_start:
            event.actual_start = actual_start
        if actual_end:
            event.actual_end = actual_end
        if actual_disruption_start:
            event.actual_disruption_start = actual_disruption_start
        if actual_disruption_end:
            event.actual_disruption_end = actual_disruption_end
        event.work_done = work_done
        event.comments = comments
        event.is_completed = True
        event.completed_at = timezone.now()
        event.status = Event.EventStatus.COMPLETED

        event.save()

        messages.success(request, 'Работы успешно завершены!')
        return redirect('events:event_detail', pk=pk)

    return render(request, 'events/complete_event.html', {'event': event})
