from django.urls import path
from . import views
from . import views_dict
from . import views_export
from . import views_dashboard
from . import views_audit

app_name = 'events'

urlpatterns = [
    # Главная страница (реестр заявок)
    path('', views.EventListView.as_view(), name='event_list'),
    
    # Создание заявки
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    
    # Детальный просмотр заявки
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    
    # Редактирование заявки
    path('<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    
    # Отправка на согласование
    path('<int:pk>/submit/', views.event_submit, name='event_submit'),
    
    # Согласование заявки
    path('<int:pk>/approve/', views.event_approve, name='event_approve'),
    
    # Отправка на доработку
    path('<int:pk>/reject/', views.event_reject, name='event_reject'),
    
    # Отмена заявки
    path('<int:pk>/cancel/', views.event_cancel, name='event_cancel'),
    
    # Загрузка файлов
    path('<int:pk>/add_document/', views.add_document, name='add_document'),
    path('document/<int:pk>/delete/', views.delete_document, name='delete_document'),

    # URL для управления справочниками (только для ГДУ)
    path('dictionaries/services/', views_dict.ServiceListView.as_view(), name='service_list'),
    path('dictionaries/services/create/', views_dict.ServiceCreateView.as_view(), name='service_create'),
    path('dictionaries/services/<int:pk>/edit/', views_dict.ServiceUpdateView.as_view(), name='service_update'),
    path('dictionaries/services/<int:pk>/delete/', views_dict.ServiceDeleteView.as_view(), name='service_delete'),
    
    # Добавьте аналогично для других моделей
    # 👇 ДОБАВЬТЕ ЭТИ СТРОКИ ДЛЯ DeviceType
    path('dictionaries/device-types/', views_dict.DeviceTypeListView.as_view(), name='device_type_list'),
    path('dictionaries/device-types/create/', views_dict.DeviceTypeCreateView.as_view(), name='device_type_create'),
    path('dictionaries/device-types/<int:pk>/edit/', views_dict.DeviceTypeUpdateView.as_view(), name='device_type_update'),
    path('dictionaries/device-types/<int:pk>/delete/', views_dict.DeviceTypeDeleteView.as_view(), name='device_type_delete'),
    
    # 👇 ДОБАВЬТЕ ЭТИ СТРОКИ ДЛЯ Device
    path('dictionaries/devices/', views_dict.DeviceListView.as_view(), name='device_list'),
    path('dictionaries/devices/create/', views_dict.DeviceCreateView.as_view(), name='device_create'),
    path('dictionaries/devices/<int:pk>/edit/', views_dict.DeviceUpdateView.as_view(), name='device_update'),
    path('dictionaries/devices/<int:pk>/delete/', views_dict.DeviceDeleteView.as_view(), name='device_delete'),
    
    # ... и так далее для остальных моделей (Location, Employee, Organization)
    path('dictionaries/locations/', views_dict.LocationListView.as_view(), name='location_list'),
    path('dictionaries/locations/create/', views_dict.LocationCreateView.as_view(), name='location_create'),
    path('dictionaries/locations/<int:pk>/edit/', views_dict.LocationUpdateView.as_view(), name='location_update'),
    path('dictionaries/locations/<int:pk>/delete/', views_dict.LocationDeleteView.as_view(), name='location_delete'),
    
    path('dictionaries/employees/', views_dict.EmployeeListView.as_view(), name='employee_list'),
    path('dictionaries/employees/create/', views_dict.EmployeeCreateView.as_view(), name='employee_create'),
    path('dictionaries/employees/<int:pk>/edit/', views_dict.EmployeeUpdateView.as_view(), name='employee_update'),
    path('dictionaries/employees/<int:pk>/delete/', views_dict.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    path('dictionaries/organizations/', views_dict.OrganizationListView.as_view(), name='organization_list'),
    path('dictionaries/organizations/create/', views_dict.OrganizationCreateView.as_view(), name='organization_create'),
    path('dictionaries/organizations/<int:pk>/edit/', views_dict.OrganizationUpdateView.as_view(), name='organization_update'),
    path('dictionaries/organizations/<int:pk>/delete/', views_dict.OrganizationDeleteView.as_view(), name='organization_delete'),

    path('dictionaries/departments/', views_dict.OrganizationListView.as_view(), name='department_list'),
    path('dictionaries/departments/create/', views_dict.OrganizationCreateView.as_view(), name='department_create'),
    path('dictionaries/departments/<int:pk>/edit/', views_dict.OrganizationUpdateView.as_view(), name='department_update'),
    path('dictionaries/departments/<int:pk>/delete/', views_dict.OrganizationDeleteView.as_view(), name='department_delete'),

     # Экспорт
    path('export/excel/', views_export.ExportEventsExcelView.as_view(), name='export_excel'),
    path('export/csv/', views_export.ExportEventsCSVView.as_view(), name='export_csv'),

    # Дашборд
    path('dashboard/', views_dashboard.DashboardView.as_view(), name='dashboard'),

    # Завершение работ
    path('<int:pk>/complete/', views.complete_event, name='complete_event'),

    # Аудит
    path('audit/', views_audit.AuditLogListView.as_view(), name='audit_list'),
]
