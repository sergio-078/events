# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from .models import (
    Service, DeviceType, Device, Location, OutsideLocation, Material,
    Organization, Department, Unit, Employee,
    Event, TechCardStep, EventDocument
)


class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_permissions_count']
    filter_horizontal = ['permissions']
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()
    get_permissions_count.short_description = 'Количество прав'


# Переопределяем стандартную регистрацию групп
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'is_active', 'created_at']
    search_fields = ['name']
    list_filter = ['device_type', 'is_active']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['region', 'site', 'building', 'room', 'rack', 'is_active']
    search_fields = ['region', 'site', 'building', 'room', 'rack']
    list_filter = ['region', 'site', 'is_active']


@admin.register(OutsideLocation)
class OutsideLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    list_filter = ['is_active']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'email', 'phone', 'is_active']
    search_fields = ['full_name', 'position', 'email']
    list_filter = ['position', 'is_active']


class TechCardStepInline(admin.TabularInline):
    model = TechCardStep
    extra = 0
    fields = ['step_number', 'name', 'planned_start', 'planned_end']
    ordering = ['step_number']


class EventDocumentInline(admin.TabularInline):
    model = EventDocument
    extra = 0
    fields = ['file', 'description', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'work_name', 'status', 'planned_start', 'planned_end',
        'created_by', 'created_at', 'status_badge'
    ]
    list_filter = ['status', 'work_reason', 'is_service_disruption', 'created_at']
    search_fields = ['work_name', 'work_description', 'id']
    readonly_fields = [
        'planned_duration_days', 'planned_duration_hours', 'planned_duration_minutes',
        'created_at', 'updated_at', 'submitted_at', 'approved_at'
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'created_by', 'approved_by', 'status',
                'work_reason', 'work_name', 'work_description'
            )
        }),
        ('Дата и время', {
            'fields': (
                'planned_start', 'planned_end',
                'planned_duration_days', 'planned_duration_hours', 'planned_duration_minutes'
            )
        }),
        ('Нарушение сервиса', {
            'fields': (
                'is_service_disruption',
                'service_disruption_duration_days',
                'service_disruption_duration_hours',
                'service_disruption_duration_minutes',
                'is_duration_match'
            )
        }),
        ('Местоположение', {
            'fields': (
                'object_location', 'is_object_outside', 'object_outside_location',
                'work_location', 'is_work_outside', 'work_outside_location'
            )
        }),
        ('Связи (многие ко многим)', {
            'fields': (
                'affected_services', 'device_types', 'devices',
                'materials', 'organizations', 'departments', 'units',
                'executors', 'joint_workers', 'agreed_with', 'notified_persons'
            )
        }),
        ('Ответственные', {
            'fields': ('responsible_person',)
        }),
        ('Доработка', {
            'fields': ('revision_reason', 'revision_comment'),
            'classes': ('collapse',)
        }),
        ('Системные поля', {
            'fields': (
                'created_at', 'updated_at', 'submitted_at', 'approved_at',
                'services_comment', 'materials_comment'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [TechCardStepInline, EventDocumentInline]
    
    def status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'under_review': 'warning',
            'rejected': 'danger',
            'approved': 'success',
            'in_progress': 'info',
            'completed': 'primary',
            'cancelled': 'dark'
        }
        status_names = dict(Event.EventStatus.choices)
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            status_names.get(obj.status, obj.status)
        )
    status_badge.short_description = 'Статус'

    def save_model(self, request, obj, form, change):
        if not change:  # Создание новой записи
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
