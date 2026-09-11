from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import (
    Service, DeviceType, Device, Location, Employee,
    Organization, Department,
)


# ===================================================================
# Базовые классы
# ===================================================================
class DictionaryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_list.html'
    paginate_by = 20
    url_prefix = None  # обязательно задать в наследнике

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prefix = self.url_prefix
        if not prefix:
            raise ValueError(f'{self.__class__.__name__}: не задан url_prefix')
        context['model_name'] = self.model._meta.verbose_name_plural
        context['create_url'] = f'events:{prefix}_create'
        context['update_url'] = f'events:{prefix}_update'
        context['delete_url'] = f'events:{prefix}_delete'
        return context


class DictionaryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_form.html'

    def get_success_url(self):
        return reverse_lazy(f'events:{self.url_prefix}_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно создана')
        return response


class DictionaryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_form.html'

    def get_success_url(self):
        return reverse_lazy(f'events:{self.url_prefix}_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно обновлена')
        return response


class DictionaryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'events.can_edit_dictionaries'
    template_name = 'events/dictionary_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy(f'events:{self.url_prefix}_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Запись успешно удалена')
        return response


# ===================================================================
# Service
# ===================================================================
class ServiceListView(DictionaryListView):
    model = Service
    context_object_name = 'items'
    url_prefix = 'service'


class ServiceCreateView(DictionaryCreateView):
    model = Service
    fields = ['name', 'is_active']
    url_prefix = 'service'


class ServiceUpdateView(DictionaryUpdateView):
    model = Service
    fields = ['name', 'is_active']
    url_prefix = 'service'


class ServiceDeleteView(DictionaryDeleteView):
    model = Service
    url_prefix = 'service'


# ===================================================================
# DeviceType
# ===================================================================
class DeviceTypeListView(DictionaryListView):
    model = DeviceType
    context_object_name = 'items'
    url_prefix = 'device_type'


class DeviceTypeCreateView(DictionaryCreateView):
    model = DeviceType
    fields = ['name', 'is_active']
    url_prefix = 'device_type'


class DeviceTypeUpdateView(DictionaryUpdateView):
    model = DeviceType
    fields = ['name', 'is_active']
    url_prefix = 'device_type'


class DeviceTypeDeleteView(DictionaryDeleteView):
    model = DeviceType
    url_prefix = 'device_type'


# ===================================================================
# Device
# ===================================================================
class DeviceListView(DictionaryListView):
    model = Device
    context_object_name = 'items'
    url_prefix = 'device'


class DeviceCreateView(DictionaryCreateView):
    model = Device
    fields = ['name', 'device_type', 'is_active']
    url_prefix = 'device'


class DeviceUpdateView(DictionaryUpdateView):
    model = Device
    fields = ['name', 'device_type', 'is_active']
    url_prefix = 'device'


class DeviceDeleteView(DictionaryDeleteView):
    model = Device
    url_prefix = 'device'


# ===================================================================
# Location
# ===================================================================
class LocationListView(DictionaryListView):
    model = Location
    context_object_name = 'items'
    url_prefix = 'location'


class LocationCreateView(DictionaryCreateView):
    model = Location
    fields = ['region', 'site', 'building', 'room', 'rack', 'is_active']
    url_prefix = 'location'


class LocationUpdateView(DictionaryUpdateView):
    model = Location
    fields = ['region', 'site', 'building', 'room', 'rack', 'is_active']
    url_prefix = 'location'


class LocationDeleteView(DictionaryDeleteView):
    model = Location
    url_prefix = 'location'


# ===================================================================
# Employee
# ===================================================================
class EmployeeListView(DictionaryListView):
    model = Employee
    context_object_name = 'items'
    url_prefix = 'employee'


class EmployeeCreateView(DictionaryCreateView):
    model = Employee
    fields = ['full_name', 'position', 'email', 'phone', 'is_active']
    url_prefix = 'employee'


class EmployeeUpdateView(DictionaryUpdateView):
    model = Employee
    fields = ['full_name', 'position', 'email', 'phone', 'is_active']
    url_prefix = 'employee'


class EmployeeDeleteView(DictionaryDeleteView):
    model = Employee
    url_prefix = 'employee'


# ===================================================================
# Organization
# ===================================================================
class OrganizationListView(DictionaryListView):
    model = Organization
    context_object_name = 'items'
    url_prefix = 'organization'


class OrganizationCreateView(DictionaryCreateView):
    model = Organization
    fields = ['name', 'is_active']
    url_prefix = 'organization'


class OrganizationUpdateView(DictionaryUpdateView):
    model = Organization
    fields = ['name', 'is_active']
    url_prefix = 'organization'


class OrganizationDeleteView(DictionaryDeleteView):
    model = Organization
    url_prefix = 'organization'


# ===================================================================
# Department
# ===================================================================
class DepartmentListView(DictionaryListView):
    model = Department
    context_object_name = 'items'
    url_prefix = 'department'


class DepartmentCreateView(DictionaryCreateView):
    model = Department
    fields = ['name', 'is_active']
    url_prefix = 'department'


class DepartmentUpdateView(DictionaryUpdateView):
    model = Department
    fields = ['name', 'is_active']
    url_prefix = 'department'


class DepartmentDeleteView(DictionaryDeleteView):
    model = Department
    url_prefix = 'department' 
