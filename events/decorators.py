
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import AuditLog
import json


def group_required(*group_names):
    """Декоратор для проверки принадлежности к группам"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(group in user_groups for group in group_names):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'У вас нет прав для доступа к этой странице')
            return redirect('events:event_list')
        return wrapper
    return decorator


def permission_required(perm):
    """Декоратор для проверки наличия конкретного разрешения"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, f'У вас нет права "{perm}" для выполнения этого действия')
            return redirect('events:event_list')
        return wrapper
    return decorator


def event_owner_or_permission(perm):
    """Проверка: пользователь владелец заявки или имеет специальное право"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Получаем объект события
            from .models import Event
            event_id = kwargs.get('pk')
            if event_id:
                try:
                    event = Event.objects.get(pk=event_id)
                    # Проверяем, является ли пользователь владельцем
                    if event.created_by == request.user:
                        return view_func(request, *args, **kwargs)
                except Event.DoesNotExist:
                    pass
            
            # Проверяем наличие разрешения
            if request.user.has_perm(perm):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'У вас нет прав для редактирования этой заявки')
            return redirect('events:event_list')
        return wrapper
    return decorator


def audit_log(action_type):
    """
    Декоратор для логирования действий пользователей
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Получаем информацию о пользователе
            user = request.user if request.user.is_authenticated else None
            username = user.username if user else 'Anonymous'
            user_ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            request_path = request.path
            
            # Получаем информацию об объекте (если есть)
            object_id = kwargs.get('pk', '')
            model_name = ''
            object_repr = ''
            
            # Если в функции есть объект, пытаемся получить его представление
            if hasattr(view_func, 'model'):
                model_name = view_func.model.__name__
            
            # Сохраняем изменения для POST запросов
            changes = {}
            if request.method in ['POST', 'PUT', 'PATCH']:
                # Копируем данные формы (кроме паролей и файлов)
                for key, value in request.POST.items():
                    if 'password' not in key.lower():
                        changes[key] = str(value)[:100]  # Ограничиваем длину
            
            # Выполняем функцию
            response = view_func(request, *args, **kwargs)
            
            # Если объект был создан или обновлен, получаем его ID
            if hasattr(response, 'context_data') and 'object' in response.context_data:
                obj = response.context_data['object']
                object_id = str(obj.pk)
                object_repr = str(obj)[:200]
                model_name = obj.__class__.__name__
            
            # Создаем запись аудита
            AuditLog.objects.create(
                user=user,
                username=username,
                user_ip=user_ip,
                user_agent=user_agent,
                action_type=action_type,
                model_name=model_name,
                object_id=object_id,
                object_repr=object_repr,
                changes=changes,
                request_path=request_path,
                message=f"{username} выполнил действие: {action_type}"
            )
            
            return response
        return wrapper
    return decorator


class AuditMixin:
    """Mixin для логирования действий в классах View"""
    
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Логируем создание/обновление
        response = super().form_valid(form)
        self._log_action()
        return response
    
    def _log_action(self):
        """Логирование действия"""
        if hasattr(self, 'object'):
            action_type = 'update' if self.object else 'create'
        else:
            action_type = 'create'
        
        user = self.request.user
        AuditLog.objects.create(
            user=user,
            username=user.username,
            user_ip=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            action_type=action_type,
            model_name=self.model.__name__,
            object_id=str(self.object.pk) if hasattr(self, 'object') else '',
            object_repr=str(self.object)[:200] if hasattr(self, 'object') else '',
            request_path=self.request.path,
            message=f"{user.username} создал/обновил запись"
        )
