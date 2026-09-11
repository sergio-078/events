from django.utils import timezone
from .models import AuditLog
import json


class AuditMiddleware:
    """
    Middleware для автоматического логирования действий пользователей
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Логируем вход пользователя
        if request.user.is_authenticated and request.method == 'POST':
            if '/login/' in request.path:
                self._log_login(request)
        
        response = self.get_response(request)
        
        # Логируем выход пользователя
        if '/logout/' in request.path:
            self._log_logout(request)
        
        return response
    
    def _log_login(self, request):
        """Логирование входа"""
        AuditLog.objects.create(
            user=request.user,
            username=request.user.username,
            user_ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            action_type='login',
            model_name='User',
            object_id=str(request.user.id),
            object_repr=request.user.username,
            request_path=request.path,
            message=f"Пользователь {request.user.username} вошел в систему"
        )
    
    def _log_logout(self, request):
        """Логирование выхода"""
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                username=request.user.username,
                user_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                action_type='logout',
                model_name='User',
                object_id=str(request.user.id),
                object_repr=request.user.username,
                request_path=request.path,
                message=f"Пользователь {request.user.username} вышел из системы"
            )