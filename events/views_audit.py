from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import AuditLog


class AuditLogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Просмотр записей аудита"""
    model = AuditLog
    template_name = 'events/audit_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    permission_required = 'events.can_manage_users'
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        
        # Фильтр по пользователю
        user = self.request.GET.get('user')
        if user:
            queryset = queryset.filter(username__icontains=user)
        
        # Фильтр по типу действия
        action_type = self.request.GET.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Фильтр по модели
        model_name = self.request.GET.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        # Фильтр по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Поиск
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(object_repr__icontains=search) |
                Q(message__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_types'] = AuditLog.ActionType.choices
        context['current_filters'] = self.request.GET.dict()
        return context
    