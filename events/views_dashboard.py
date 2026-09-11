from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from .utils.dashboard_utils import DashboardData
import json


class DashboardView(LoginRequiredMixin, TemplateView):
    """Дашборд с визуализацией данных"""
    template_name = 'events/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем данные для дашборда
        dashboard = DashboardData()
        stats = dashboard.get_all_stats()
        
        # Конвертируем в JSON для JavaScript
        context['stats_json'] = json.dumps(stats)
        context['stats'] = stats
        
        return context
    