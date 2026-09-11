from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from crispy_forms.bootstrap import TabHolder, Tab
from .models import (
    Event, TechCard, TechCardStep, EventDocument, Service, DeviceType, Device,
    Location, OutsideLocation, Material, Organization, Department,
    Unit, Employee
)
from django.utils import timezone

class DateTimeLocalInput(forms.DateTimeInput):
    """
    Виджет для <input type="datetime-local">.
    Форматирует значение как YYYY-MM-DDTHH:MM — только так браузер
    понимает value в datetime-local.
    """
    input_type = 'datetime-local'

    def __init__(self, attrs=None, format=None):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format=format or '%Y-%m-%dT%H:%M')

    def format_value(self, value):
        """
        Django по умолчанию рендерит datetime с таймзоной.
        Приводим к локальному времени (в вашем случае — Europe/Moscow)
        и форматируем в YYYY-MM-DDTHH:MM.
        """
        if value is None:
            return ''
        if hasattr(value, 'strftime'):
            # Если USE_TZ=True и значение aware — переводим в текущую таймзону
            if timezone.is_aware(value):
                value = timezone.localtime(value)
            return value.strftime('%Y-%m-%dT%H:%M')
        return super().format_value(value)


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
            # Фактические данные
            'actual_start', 'actual_end',
            'actual_disruption_start', 'actual_disruption_end',
            'work_done', 'comments',
            'is_completed',
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
            'planned_start': DateTimeLocalInput(),
            'planned_end': DateTimeLocalInput(),
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
            # Фактические даты
            'actual_start': DateTimeLocalInput(),
            'actual_end': DateTimeLocalInput(),
            'actual_disruption_start': DateTimeLocalInput(),
            'actual_disruption_end': DateTimeLocalInput(),
            'work_done': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
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
            'actual_start': 'Фактическая дата и время начала работ',
            'actual_end': 'Фактическая дата и время окончания работ',
            'actual_disruption_start': 'Фактическая дата и время начала перерыва',
            'actual_disruption_end': 'Фактическая дата и время окончания перерыва',
            'work_done': 'Что было сделано',
            'comments': 'Комментарии',
            'is_completed': 'Работы завершены',
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
        # Эти поля необязательные — валидация длительности перерыва
        # делается отдельно в clean(), только когда стоит галочка is_service_disruption
        self.fields['service_disruption_duration_days'].required = False
        self.fields['service_disruption_duration_hours'].required = False
        self.fields['service_disruption_duration_minutes'].required = False
        self.fields['is_duration_match'].required = False

    def clean(self):
        print("DEBUG POST is_service_disruption:", repr(self.data.get('is_service_disruption')))
        cleaned_data = super().clean()
        print("DEBUG cleaned is_service_disruption:", repr(cleaned_data.get('is_service_disruption')))
        print("DEBUG cleaned duration_days:", repr(cleaned_data.get('service_disruption_duration_days')))
        planned_start = cleaned_data.get('planned_start')
        planned_end = cleaned_data.get('planned_end')
        actual_start = cleaned_data.get('actual_start')
        actual_end = cleaned_data.get('actual_end')
        actual_disruption_start = cleaned_data.get('actual_disruption_start')
        actual_disruption_end = cleaned_data.get('actual_disruption_end')

        # Валидация плановых дат
        if planned_start and planned_end and planned_end <= planned_start:
            raise forms.ValidationError(
                'Дата окончания работ не может быть раньше даты начала работ'
            )

        # Валидация фактических дат
        if actual_start and actual_end and actual_end <= actual_start:
            raise forms.ValidationError(
                'Фактическая дата окончания не может быть раньше даты начала'
            )

        if actual_disruption_start and actual_disruption_end and actual_disruption_end <= actual_disruption_start:
            raise forms.ValidationError(
                'Фактическая дата окончания перерыва не может быть раньше даты начала перерыва'
            )

        # Проверка, что фактические даты не раньше плановых
        if planned_start and actual_start and actual_start < planned_start:
            raise forms.ValidationError(
                'Фактическая дата начала не может быть раньше плановой'
            )

        # Валидация длительности перерыва
        # Читаем значение галочки НАПРЯМУЮ из POST, чтобы не зависеть от того,
    # как Django/Crispy отрендерили чекбокс.
        posted_is_service_disruption = self.data.get('is_service_disruption')
        is_service_disruption = posted_is_service_disruption in ('on', 'true', 'True', '1')

        if is_service_disruption:
            days = cleaned_data.get('service_disruption_duration_days') or 0
            hours = cleaned_data.get('service_disruption_duration_hours') or 0
            minutes = cleaned_data.get('service_disruption_duration_minutes') or 0
            if days == 0 and hours == 0 and minutes == 0:
                self.add_error(
                    'service_disruption_duration_days',
                    'При наличии нарушения сервиса необходимо указать длительность перерыва'
                )
        else:
            # Галочка не стоит — принудительно обнуляем, чтобы не тянулись старые значения
            cleaned_data['service_disruption_duration_days'] = 0
            cleaned_data['service_disruption_duration_hours'] = 0
            cleaned_data['service_disruption_duration_minutes'] = 0
            cleaned_data['is_duration_match'] = False

        return cleaned_data


# ====================================================
# Форма для шагов технологической карты
# ====================================================

class TechCardStepForm(forms.ModelForm):
    class Meta:
        model = TechCardStep
        fields = ['name', 'planned_start', 'planned_end']  # step_number убрали
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Проверить порт на АТС'}),
            'planned_start': DateTimeLocalInput(),
            'planned_end': DateTimeLocalInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        ps = cleaned_data.get('planned_start')
        pe = cleaned_data.get('planned_end')
        if ps and pe and pe <= ps:
            raise forms.ValidationError('Дата окончания шага не может быть раньше даты начала шага')
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


# ====================================================
# Форма для технологических карт (основные записи)
# ====================================================

class TechCardForm(forms.ModelForm):
    class Meta:
        model = TechCard
        fields = ['name', 'quantity', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
        }


TechCardFormSet = inlineformset_factory(
    Event,
    TechCard,
    form=TechCardForm,
    extra=1,
    can_delete=True,
)


# ====================================================
# Форма для документов
# ====================================================

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
            allowed_extensions = ['txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg',
                                  'doc', 'docx', 'xls', 'xlsx']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Недопустимый формат файла. Разрешены: {", ".join(allowed_extensions)}'
                )

        return file
    