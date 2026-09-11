from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from .models import Event
from .utils.export_utils import export_events_to_excel, export_events_to_csv


class ExportEventsExcelView(LoginRequiredMixin, View):
    """Экспорт заявок в Excel"""
    
    def get(self, request, *args, **kwargs):
        # Получаем queryset с теми же фильтрами, что и на странице списка
        queryset = self.get_queryset()
        
        if not queryset.exists():
            messages.warning(request, 'Нет данных для экспорта')
            return redirect('events:event_list')
        
        return export_events_to_excel(queryset)
    
    def get_queryset(self):
        """Получение queryset с применением фильтров из GET-параметров"""
        queryset = Event.objects.all()
        
        # Применяем фильтры аналогично EventListView
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        filter_type = self.request.GET.get('filter')
        today = timezone.now().date()
        
        if filter_type == 'today':
            queryset = queryset.filter(planned_start__date=today)
        elif filter_type == 'upcoming':
            queryset = queryset.filter(planned_start__date__gte=today)
        elif filter_type == 'past':
            queryset = queryset.filter(planned_end__date__lt=today)
        
        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(work_name__icontains=search_query) |
                Q(work_description__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        return queryset


class ExportEventsCSVView(ExportEventsExcelView):
    """Экспорт заявок в CSV"""
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        if not queryset.exists():
            messages.warning(request, 'Нет данных для экспорта')
            return redirect('events:event_list')
        
        return export_events_to_csv(queryset)
    