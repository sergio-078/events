# Create your views here.
from venv import logger

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponseRedirect

from .models import Event, EventDocument, TechCardStep
from .forms import EventForm, EventDocumentForm, TechCardStepFormSet
from .utils.email_utils import (
    send_submit_notification, 
    send_approve_notification, 
    send_reject_notification
)


class EventListView(LoginRequiredMixin, ListView):
    """Реестр заявок с фильтрацией"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'created_by', 'approved_by', 'responsible_person'
        ).prefetch_related(
            'affected_services', 'device_types', 'devices',
            'organizations', 'departments', 'units'
        )
        
        # Фильтр по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Фильтр по дате
        filter_type = self.request.GET.get('filter')
        today = timezone.now().date()
        
        if filter_type == 'today':
            queryset = queryset.filter(
                planned_start__date=today
            )
        elif filter_type == 'upcoming':
            queryset = queryset.filter(
                planned_start__date__gte=today,
                status__in=['draft', 'under_review', 'approved']
            )
        elif filter_type == 'past':
            queryset = queryset.filter(
                planned_end__date__lt=today
            )
        elif filter_type == 'period':
            date_from = self.request.GET.get('date_from')
            date_to = self.request.GET.get('date_to')
            if date_from and date_to:
                queryset = queryset.filter(
                    planned_start__date__gte=date_from,
                    planned_start__date__lte=date_to
                )
        
        # Поиск по тексту
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
        # ИСПРАВЛЕНО: Используем правильный синтаксис для доступа к choices
        context['status_choices'] = Event.EventStatus.choices
        context['current_filter'] = self.request.GET.get('filter', 'upcoming')
        context['search_query'] = self.request.GET.get('q', '')
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
            'tech_card_steps', 'documents'
        )


class EventCreateView(LoginRequiredMixin, CreateView):
    """Создание новой заявки"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tech_card_formset'] = TechCardStepFormSet(
                self.request.POST,
                prefix='tech_card'
            )
        else:
            context['tech_card_formset'] = TechCardStepFormSet(
                prefix='tech_card'
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        tech_card_formset = context['tech_card_formset']
        
        if tech_card_formset.is_valid():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            # ИСПРАВЛЕНО: Используем правильный синтаксис
            self.object.status = Event.EventStatus.DRAFT
            self.object.save()
            
            # Сохраняем связи ManyToMany
            form.save_m2m()
            
            # Сохраняем шаги технологической карты
            tech_card_formset.instance = self.object
            tech_card_formset.save()
            
            messages.success(self.request, 'Заявка успешно создана!')
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)


class EventUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование заявки (только если в статусе Черновик или Отправлена на доработку)"""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('events:event_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['tech_card_formset'] = TechCardStepFormSet(
                self.request.POST,
                instance=self.object,
                prefix='tech_card'
            )
        else:
            context['tech_card_formset'] = TechCardStepFormSet(
                instance=self.object,
                prefix='tech_card'
            )
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        tech_card_formset = context['tech_card_formset']
        
        if tech_card_formset.is_valid():
            self.object = form.save()
            tech_card_formset.instance = self.object
            tech_card_formset.save()
            messages.success(self.request, 'Заявка успешно обновлена!')
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)
    
    def get_queryset(self):
        # ИСПРАВЛЕНО: Используем правильный синтаксис
        return super().get_queryset().filter(
            status__in=[Event.EventStatus.DRAFT, Event.EventStatus.REJECTED]
        )


# === Функции для работы со статусами ===

def event_submit(request, pk):
    """Отправка заявки на согласование"""
    event = get_object_or_404(Event, pk=pk)
    
    if event.status != Event.EventStatus.DRAFT:
        messages.error(request, 'Нельзя отправить на согласование заявку не в статусе "Черновик"')
        return redirect('events:event_detail', pk=pk)
    
    event.status = Event.EventStatus.UNDER_REVIEW
    event.submitted_at = timezone.now()
    event.save()
    
    # Отправка уведомления
    try:
        send_submit_notification(event)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
    
    messages.success(request, 'Заявка отправлена на согласование')
    return redirect('events:event_detail', pk=pk)


def event_approve(request, pk):
    """Согласование заявки"""
    event = get_object_or_404(Event, pk=pk)
    
    if event.status != Event.EventStatus.UNDER_REVIEW:
        messages.error(request, 'Нельзя согласовать заявку не в статусе "На согласовании"')
        return redirect('events:event_detail', pk=pk)
    
    event.status = Event.EventStatus.APPROVED
    event.approved_by = request.user
    event.approved_at = timezone.now()
    event.save()
    
    # Отправка уведомления
    try:
        send_approve_notification(event)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
    
    messages.success(request, 'Заявка согласована')
    return redirect('events:event_detail', pk=pk)


def event_reject(request, pk):
    """Отправка заявки на доработку"""
    event = get_object_or_404(Event, pk=pk)
    
    if event.status != Event.EventStatus.UNDER_REVIEW:
        messages.error(request, 'Нельзя отправить на доработку заявку не в статусе "На согласовании"')
        return redirect('events:event_detail', pk=pk)
    
    # Получаем причину доработки из POST-запроса
    revision_reason = request.POST.get('revision_reason', '')
    
    event.status = Event.EventStatus.REJECTED
    event.revision_reason = revision_reason
    event.save()
    
    # Отправка уведомления
    try:
        send_reject_notification(event)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
    
    messages.success(request, 'Заявка отправлена на доработку')
    return redirect('events:event_detail', pk=pk)


def event_cancel(request, pk):
    """Отмена заявки"""
    event = get_object_or_404(Event, pk=pk)
    
    # ИСПРАВЛЕНО: Используем правильный синтаксис
    if event.status in [Event.EventStatus.COMPLETED, Event.EventStatus.CANCELLED]:
        messages.error(request, 'Нельзя отменить завершенную или уже отмененную заявку')
        return redirect('events:event_detail', pk=pk)
    
    event.status = Event.EventStatus.CANCELLED
    event.save()
    
    messages.success(request, 'Заявка отменена')
    return redirect('events:event_detail', pk=pk)


def add_document(request, pk):
    """Добавление документа к заявке"""
    event = get_object_or_404(Event, pk=pk)
    
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


def delete_document(request, pk):
    """Удаление документа"""
    document = get_object_or_404(EventDocument, pk=pk)
    event_pk = document.event.pk
    
    if request.user == document.uploaded_by or request.user.is_superuser:
        document.delete()
        messages.success(request, 'Документ удален')
    else:
        messages.error(request, 'У вас нет прав на удаление этого документа')
    
    return redirect('events:event_detail', pk=event_pk)
