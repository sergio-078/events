from django.urls import path
from . import views

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
]
