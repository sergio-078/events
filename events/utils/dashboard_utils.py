from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import timedelta
from ..models import Event
import json
from collections import defaultdict


class DashboardData:
    """Класс для подготовки данных для дашборда"""
    
    def __init__(self):
        self.now = timezone.now()
        self.today = self.now.date()
        self.start_of_month = self.today.replace(day=1)
        self.start_of_week = self.today - timedelta(days=self.today.weekday())
    
    def get_status_stats(self):
        """Статистика по статусам"""
        stats = Event.objects.values('status').annotate(count=Count('id'))
        
        status_labels = dict(Event.EventStatus.choices)
        result = {
            'labels': [],
            'values': [],
            'colors': []
        }
        
        color_map = {
            'draft': '#6c757d',
            'under_review': '#ffc107',
            'rejected': '#dc3545',
            'approved': '#198754',
            'in_progress': '#0dcaf0',
            'completed': '#0d6efd',
            'cancelled': '#212529'
        }
        
        for stat in stats:
            status = stat['status']
            result['labels'].append(status_labels.get(status, status))
            result['values'].append(stat['count'])
            result['colors'].append(color_map.get(status, '#6c757d'))
        
        return result
    
    def get_monthly_stats(self):
        """Статистика по месяцам"""
        # За последние 6 месяцев
        months = []
        for i in range(5, -1, -1):
            month_date = self.now - timedelta(days=30*i)
            months.append(month_date.strftime('%b %Y'))
        
        # Получаем данные по месяцам
        month_data = {}
        for month in months:
            month_data[month] = {
                'created': 0,
                'completed': 0,
                'approved': 0
            }
        
        # Группируем по месяцам
        events = Event.objects.filter(
            created_at__gte=self.now - timedelta(days=180)
        )
        
        for event in events:
            month_key = event.created_at.strftime('%b %Y')
            if month_key in month_data:
                month_data[month_key]['created'] += 1
                
                if event.status == 'completed':
                    month_data[month_key]['completed'] += 1
                elif event.status == 'approved':
                    month_data[month_key]['approved'] += 1
        
        return {
            'months': list(month_data.keys()),
            'created': [data['created'] for data in month_data.values()],
            'completed': [data['completed'] for data in month_data.values()],
            'approved': [data['approved'] for data in month_data.values()]
        }
    
    def get_today_stats(self):
        """Статистика за сегодня"""
        events_today = Event.objects.filter(planned_start__date=self.today)
        
        return {
            'total': events_today.count(),
            'with_disruption': events_today.filter(is_service_disruption=True).count(),
            'without_disruption': events_today.filter(is_service_disruption=False).count(),
            'in_progress': events_today.filter(status='in_progress').count(),
            'completed': events_today.filter(status='completed').count()
        }
    
    def get_week_stats(self):
        """Статистика за неделю"""
        events_week = Event.objects.filter(
            planned_start__date__gte=self.start_of_week,
            planned_start__date__lte=self.today
        )
        
        return {
            'total': events_week.count(),
            'by_day': self._get_daily_stats(events_week)
        }
    
    def _get_daily_stats(self, queryset):
        """Статистика по дням недели"""
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        result = {day: 0 for day in days}
        
        for event in queryset:
            day_index = event.planned_start.weekday()
            result[days[day_index]] += 1
        
        return result
    
    def get_work_reason_stats(self):
        """Статистика по причинам работ"""
        stats = Event.objects.values('work_reason').annotate(count=Count('id'))
        
        reason_labels = dict(Event.WorkReason.choices)
        result = {
            'labels': [],
            'values': []
        }
        
        for stat in stats:
            reason = stat['work_reason']
            result['labels'].append(reason_labels.get(reason, reason))
            result['values'].append(stat['count'])
        
        return result
    
    def get_services_stats(self):
        """Статистика по затронутым сервисам (Топ-10)"""
        from ..models import Service
        
        services = Service.objects.annotate(
            event_count=Count('events')
        ).filter(event_count__gt=0).order_by('-event_count')[:10]
        
        return {
            'labels': [s.name for s in services],
            'values': [s.event_count for s in services]
        }
    
    def get_work_duration_stats(self):
        """Статистика по длительности работ"""
        events = Event.objects.filter(
            status__in=['completed', 'approved', 'in_progress']
        )
        
        durations = []
        for event in events:
            duration_minutes = (
                event.planned_duration_days * 24 * 60 +
                event.planned_duration_hours * 60 +
                event.planned_duration_minutes
            )
            
            # Группируем по диапазонам
            if duration_minutes <= 30:
                category = 'до 30 мин'
            elif duration_minutes <= 60:
                category = '30-60 мин'
            elif duration_minutes <= 180:
                category = '1-3 часа'
            elif duration_minutes <= 480:
                category = '3-8 часов'
            else:
                category = 'более 8 часов'
            
            durations.append(category)
        
        # Подсчет
        from collections import Counter
        counter = Counter(durations)
        
        return {
            'labels': list(counter.keys()),
            'values': list(counter.values())
        }
    
    def get_performance_stats(self):
        """Статистика производительности"""
        # Среднее время выполнения
        completed_events = Event.objects.filter(
            status='completed',
            approved_at__isnull=False,
            completed_at__isnull=False
        )
        
        avg_completion_time = 0
        if completed_events.exists():
            total_seconds = 0
            for event in completed_events:
                if event.approved_at and event.completed_at:
                    delta = event.completed_at - event.approved_at
                    total_seconds += delta.total_seconds()
            
            avg_seconds = total_seconds / completed_events.count()
            avg_completion_time = {
                'days': int(avg_seconds // (24*3600)),
                'hours': int((avg_seconds % (24*3600)) // 3600),
                'minutes': int((avg_seconds % 3600) // 60)
            }
        
        # Коэффициент успешности
        total = Event.objects.count()
        completed = Event.objects.filter(status='completed').count()
        cancelled = Event.objects.filter(status='cancelled').count()
        
        success_rate = 0
        if total > 0:
            success_rate = round((completed / total) * 100, 1)
        
        return {
            'avg_completion_time': avg_completion_time,
            'success_rate': success_rate,
            'total_events': total,
            'completed_events': completed,
            'cancelled_events': cancelled
        }
    
    def get_all_stats(self):
        """Получение всей статистики для дашборда"""
        return {
            'status': self.get_status_stats(),
            'monthly': self.get_monthly_stats(),
            'today': self.get_today_stats(),
            'week': self.get_week_stats(),
            'work_reason': self.get_work_reason_stats(),
            'services': self.get_services_stats(),
            'work_duration': self.get_work_duration_stats(),
            'performance': self.get_performance_stats()
        }
    