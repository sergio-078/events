from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from crispy_forms.bootstrap import TabHolder, Tab
from .models import (
    Event, TechCardStep, EventDocument, Service, DeviceType, Device,
    Location, OutsideLocation, Material, Organization, Department,
    Unit, Employee
)


class EventForm(forms.ModelForm):
    """Основная форма создания/редактирования заявки"""
    
    # Переопределяем поля ManyToMany для использования виджета SelectMultiple
    affected_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Затронутые сервисы"
    )
    device_types = forms.ModelMultipleChoiceField(
        queryset=DeviceType.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Тип объекта"
    )
    devices = forms.ModelMultipleChoiceField(
        queryset=Device.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Объект"
    )
    materials = forms.ModelMultipleChoiceField(
        queryset=Material.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Используемые материалы/инструменты"
    )
    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Организации"
    )
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Подразделения"
    )
    units = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Отделы/лаборатории/цехи/участки"
    )
    executors = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="ФИО исполнителей"
    )
    joint_workers = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="С кем совместно будут проводиться работы"
    )
    agreed_with = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="С кем были согласованы работы"
    )
    notified_persons = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
        required=False,
        label="Кто был оповещён о работах"
    )
    
    class Meta:
        model = Event
        fields = [
            # Блок 1: Дата и время
            'planned_start', 'planned_end',
            # Блок 2: Причина
            'work_reason',
            # Блок 3: Нарушение сервиса
            'is_service_disruption',
            'service_disruption_duration_days',
            'service_disruption_duration_hours',
            'service_disruption_duration_minutes',
            'is_duration_match',
            # Блок 4: Сервисы
            'affected_services', 'services_comment',
            # Блок 5: Детали работ
            'device_types', 'devices',
            'object_location', 'is_object_outside', 'object_outside_location',
            'work_location', 'is_work_outside', 'work_outside_location',
            'work_name', 'work_description',
            'is_tech_card_required',
            'materials', 'materials_comment',
            # Блок 6: Исполнители
            'organizations', 'departments', 'units',
            'responsible_person', 'executors', 'joint_workers',
            # Блок 7: Согласование и оповещение
            'agreed_with', 'notified_persons',
            # Блок 8: Доработка
            'revision_reason', 'revision_comment',
        ]
        widgets = {
            'planned_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'planned_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'work_reason': forms.Select(attrs={'class': 'form-select'}),
            'object_location': forms.Select(attrs={'class': 'form-select'}),
            'object_outside_location': forms.Select(attrs={'class': 'form-select'}),
            'work_location': forms.Select(attrs={'class': 'form-select'}),
            'work_outside_location': forms.Select(attrs={'class': 'form-select'}),
            'responsible_person': forms.Select(attrs={'class': 'form-select'}),
            'work_name': forms.TextInput(attrs={'class': 'form-control'}),
            'work_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'services_comment': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'materials_comment': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'revision_reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'revision_comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'planned_start': 'Планируемые дата и время начала работ',
            'planned_end': 'Планируемые дата и время окончания работ',
            'work_reason': 'Причина работ',
            'is_service_disruption': 'Нарушение сервиса',
            'service_disruption_duration_days': 'Длительность перерыва (дни)',
            'service_disruption_duration_hours': 'Длительность перерыва (часы)',
            'service_disruption_duration_minutes': 'Длительность перерыва (минуты)',
            'is_duration_match': 'Длительность работ совпадает с перерывом сервиса',
            'services_comment': 'Комментарии к затронутым сервисам',
            'object_location': 'Место нахождения объекта',
            'is_object_outside': 'Объект находится за территорией Общества',
            'object_outside_location': 'Место нахождения объекта за территорией Общества',
            'work_location': 'Место выполнения работ',
            'is_work_outside': 'Работы выполняются за территорией Общества',
            'work_outside_location': 'Место выполнения работ за территорией Общества',
            'work_name': 'Наименование работ',
            'work_description': 'Подробное описание работ (план мероприятий)',
            'is_tech_card_required': 'Требуется технологическая карта',
            'materials_comment': 'Комментарий к материалам/инструментам',
            'responsible_person': 'ФИО ответственного',
            'revision_reason': 'Причина отправки на доработку',
            'revision_comment': 'Комментарий после доработки',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'
        
        # Настройка для полей с длительностью
        self.fields['service_disruption_duration_days'].widget.attrs['class'] = 'form-control'
        self.fields['service_disruption_duration_hours'].widget.attrs['class'] = 'form-control'
        self.fields['service_disruption_duration_minutes'].widget.attrs['class'] = 'form-control'
        self.fields['service_disruption_duration_days'].widget.attrs['style'] = 'width: 80px; display: inline;'
        self.fields['service_disruption_duration_hours'].widget.attrs['style'] = 'width: 80px; display: inline;'
        self.fields['service_disruption_duration_minutes'].widget.attrs['style'] = 'width: 80px; display: inline;'
    
    def clean(self):
        cleaned_data = super().clean()
        planned_start = cleaned_data.get('planned_start')
        planned_end = cleaned_data.get('planned_end')
        
        if planned_start and planned_end and planned_end <= planned_start:
            raise forms.ValidationError(
                'Дата окончания работ не может быть раньше даты начала работ'
            )
        
        # Валидация длительности перерыва
        is_service_disruption = cleaned_data.get('is_service_disruption')
        if is_service_disruption:
            days = cleaned_data.get('service_disruption_duration_days', 0)
            hours = cleaned_data.get('service_disruption_duration_hours', 0)
            minutes = cleaned_data.get('service_disruption_duration_minutes', 0)
            if days == 0 and hours == 0 and minutes == 0:
                raise forms.ValidationError(
                    'При наличии нарушения сервиса необходимо указать длительность перерыва'
                )
        
        return cleaned_data


# === Форма для технологической карты ===

class TechCardStepForm(forms.ModelForm):
    class Meta:
        model = TechCardStep
        fields = ['step_number', 'planned_start', 'planned_end']
        widgets = {
            'step_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 50}),
            'planned_start': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'planned_end': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        planned_start = cleaned_data.get('planned_start')
        planned_end = cleaned_data.get('planned_end')
        
        if planned_start and planned_end and planned_end <= planned_start:
            raise forms.ValidationError(
                'Дата окончания шага не может быть раньше даты начала шага'
            )
        
        return cleaned_data


TechCardStepFormSet = inlineformset_factory(
    Event,
    TechCardStep,
    form=TechCardStepForm,
    extra=1,
    can_delete=True,
    max_num=50,
    validate_max=True,
)


# === Форма для документов ===

class EventDocumentForm(forms.ModelForm):
    class Meta:
        model = EventDocument
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Описание документа'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Проверка размера (10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Размер файла не должен превышать 10 МБ')
            
            # Проверка расширения
            allowed_extensions = ['txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'doc', 'docx', 'xls', 'xlsx']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f'Недопустимый формат файла. Разрешены: {", ".join(allowed_extensions)}')
        
        return file
    