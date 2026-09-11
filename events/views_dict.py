from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Service, DeviceType, Device, Location, Employee, Organization, Department


class DictionaryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Базовый класс для списка справочников"""
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_list.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model._meta.verbose_name_plural
        context['model_name'] = model_name
        # Автоматически формируем имя для URL создания
        context['create_url'] = f'{self.model._meta.model_name}_create'
        return context


class DictionaryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Базовый класс для создания записи справочника"""
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно создана')
        return response


class DictionaryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Базовый класс для редактирования записи справочника"""
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно обновлена')
        return response


class DictionaryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Базовый класс для удаления записи справочника"""
    permission_required = 'events.can_edit_dictionaries'
    success_url = reverse_lazy('events:dictionary_list')
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Запись успешно удалена')
        return response


# Конкретные классы для каждой модели
class ServiceListView(DictionaryListView):
    model = Service
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'service_create'
        context['model_name'] = 'Сервисы'
        return context


class ServiceCreateView(DictionaryCreateView):
    model = Service
    fields = ['name', 'is_active']


class ServiceUpdateView(DictionaryUpdateView):
    model = Service
    fields = ['name', 'is_active']


class ServiceDeleteView(DictionaryDeleteView):
    model = Service


# Аналогично для других моделей...
class DeviceTypeListView(DictionaryListView):
    model = DeviceType
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'device_type_create'  # 👈 именно так, как в urls.py
        context['model_name'] = 'Типы объектов'
        return context


class DeviceTypeCreateView(DictionaryCreateView):
    model = DeviceType
    fields = ['name', 'is_active']  # или какие поля у вас в модели


class DeviceTypeUpdateView(DictionaryUpdateView):
    model = DeviceType
    fields = ['name', 'is_active']


class DeviceTypeDeleteView(DictionaryDeleteView):
    model = DeviceType


class DeviceListView(DictionaryListView):
    model = Device
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'device_create'
        context['model_name'] = 'Объекты'
        return context


class DeviceCreateView(DictionaryCreateView):
    model = Device
    fields = ['name', 'is_active']  # или какие поля у вас в модели


class DeviceUpdateView(DictionaryUpdateView):
    model = Device
    fields = ['name', 'is_active']


class DeviceDeleteView(DictionaryDeleteView):
    model = Device


# ===================================================================
# Location
# ===================================================================
class LocationListView(DictionaryListView):
    model = Location
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'location_create'
        context['model_name'] = 'Местоположения'
        return context


class LocationCreateView(DictionaryCreateView):
    model = Location
    fields = ['name', 'is_active']


class LocationUpdateView(DictionaryUpdateView):
    model = Location
    fields = ['name', 'is_active']


class LocationDeleteView(DictionaryDeleteView):
    model = Location


# ===================================================================
# Employee
# ===================================================================
class EmployeeListView(DictionaryListView):
    model = Employee
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'employee_create'
        context['model_name'] = 'Сотрудники'
        return context


class EmployeeCreateView(DictionaryCreateView):
    model = Employee
    fields = ['name', 'position', 'is_active']  # или какие поля у вас в модели


class EmployeeUpdateView(DictionaryUpdateView):
    model = Employee
    fields = ['name', 'position', 'is_active']


class EmployeeDeleteView(DictionaryDeleteView):
    model = Employee


# ===================================================================
# Organization
# ===================================================================
class OrganizationListView(DictionaryListView):
    model = Organization
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'organization_create'
        context['model_name'] = 'Организации'
        return context


class OrganizationCreateView(DictionaryCreateView):
    model = Organization
    fields = ['name', 'is_active']


class OrganizationUpdateView(DictionaryUpdateView):
    model = Organization
    fields = ['name', 'is_active']


class OrganizationDeleteView(DictionaryDeleteView):
    model = Organization


# ===================================================================
# Department (если есть ссылки в urls.py)
# ===================================================================
class DepartmentListView(DictionaryListView):
    model = Department
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'department_create'
        context['model_name'] = 'Подразделения'
        return context


class DepartmentCreateView(DictionaryCreateView):
    model = Department
    fields = ['name', 'is_active']


class DepartmentUpdateView(DictionaryUpdateView):
    model = Department
    fields = ['name', 'is_active']


class DepartmentDeleteView(DictionaryDeleteView):
    model = Department    
