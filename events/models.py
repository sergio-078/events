# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
import os

# ====================================================
# ЧАСТЬ 1: СПРАВОЧНИКИ (по Варианту Б)
# ====================================================

class Service(models.Model):
    """Блок 4: Затронутые сервисы"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Наименование сервиса")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Сервис"
        verbose_name_plural = "Сервисы"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DeviceType(models.Model):
    """Блок 5: Тип объекта (АТС, Маршрутизатор, и т.д.)"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Тип оборудования")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Device(models.Model):
    """Блок 5: Объект (SI-3000, Cisco 7206, и т.д.)"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Наименование оборудования")
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE, related_name='devices', verbose_name="Тип оборудования")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Location(models.Model):
    """Блок 5: Место нахождения объекта / Место выполнения работ"""
    region = models.CharField(max_length=100, verbose_name="Регион")
    site = models.CharField(max_length=100, verbose_name="Площадка")
    building = models.CharField(max_length=100, verbose_name="Здание")
    room = models.CharField(max_length=100, verbose_name="Помещение")
    rack = models.CharField(max_length=100, verbose_name="Технологический шкаф")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Местоположение"
        verbose_name_plural = "Местоположения"
        ordering = ['region', 'site', 'building']
        unique_together = ['region', 'site', 'building', 'room', 'rack']
    
    def __str__(self):
        return f"{self.region}, {self.site}, {self.building}, {self.room}, {self.rack}"
    
    @property
    def full_address(self):
        return str(self)


class OutsideLocation(models.Model):
    """Блок 5: Место нахождения объекта за территорией Общества / Место выполнения работ за территорией"""
    name = models.CharField(max_length=500, unique=True, verbose_name="Наименование (адрес)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Внешнее местоположение"
        verbose_name_plural = "Внешние местоположения"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Material(models.Model):
    """Блок 5: Используемые материалы/инструменты"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Наименование")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Материал/инструмент"
        verbose_name_plural = "Материалы/инструменты"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Organization(models.Model):
    """Блок 6: Организация"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Наименование организации")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    """Блок 6: Подразделение"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Наименование подразделения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Подразделение"
        verbose_name_plural = "Подразделения"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Unit(models.Model):
    """Блок 6: Отдел/лаборатория/цех/участок"""
    name = models.CharField(max_length=200, unique=True, verbose_name="Наименование")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Отдел/лаборатория/цех/участок"
        verbose_name_plural = "Отделы/лаборатории/цехи/участки"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    """Блок 6: ФИО ответственного, исполнители, согласовавшие, оповещенные"""
    full_name = models.CharField(max_length=200, unique=True, verbose_name="ФИО")
    position = models.CharField(max_length=200, blank=True, verbose_name="Должность")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name


# ====================================================
# ЧАСТЬ 2: ОСНОВНАЯ МОДЕЛЬ - ЗАЯВКА НА РАБОТЫ
# ====================================================
    
class Event(models.Model):
    """Главная модель - Заявка на плановые работы"""

        # Определяем статусы как вложенный класс
    class EventStatus(models.TextChoices):
        DRAFT = 'draft', 'Черновик'
        UNDER_REVIEW = 'under_review', 'На согласовании'
        REJECTED = 'rejected', 'Отправлена на доработку'
        APPROVED = 'approved', 'Согласована'
        IN_PROGRESS = 'in_progress', 'Выполняется'
        COMPLETED = 'completed', 'Завершена'
        CANCELLED = 'cancelled', 'Отменена'
    
    # Блок 0: Связи с пользователями (позже доработаем)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_events',
        verbose_name="Создал заявку"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_events',
        verbose_name="Согласовал"
    )
    
    # Блок 1: Дата и время
    planned_start = models.DateTimeField(verbose_name="Планируемая дата и время начала работ")
    planned_end = models.DateTimeField(verbose_name="Планируемая дата и время окончания работ")
    planned_duration_days = models.IntegerField(default=0, verbose_name="Длительность (дни)")
    planned_duration_hours = models.IntegerField(default=0, verbose_name="Длительность (часы)")
    planned_duration_minutes = models.IntegerField(default=0, verbose_name="Длительность (минуты)")
    
    # Блок 2: Причина работ
    class WorkReason(models.TextChoices):
        AVR = 'avr', 'АВР'
        PLANNED = 'planned', 'Плановые работы'
        PPR = 'ppr', 'ППР'
    
    work_reason = models.CharField(
        max_length=20,
        choices=WorkReason.choices,
        verbose_name="Причина работ"
    )
    
    # Блок 3: Нарушение сервиса
    is_service_disruption = models.BooleanField(
        default=False,
        verbose_name="Нарушение сервиса"
    )
    service_disruption_duration_days = models.IntegerField(
        default=0,
        verbose_name="Длительность перерыва (дни)"
    )
    service_disruption_duration_hours = models.IntegerField(
        default=0,
        verbose_name="Длительность перерыва (часы)"
    )
    service_disruption_duration_minutes = models.IntegerField(
        default=0,
        verbose_name="Длительность перерыва (минуты)"
    )
    is_duration_match = models.BooleanField(
        default=False,
        verbose_name="Длительность работ совпадает с перерывом сервиса"
    )
    
    # Блок 4: Затронутые сервисы
    affected_services = models.ManyToManyField(
        Service,
        blank=True,
        related_name='events',
        verbose_name="Затронутые сервисы"
    )
    services_comment = models.TextField(
        blank=True,
        verbose_name="Комментарии к затронутым сервисам"
    )
    
    # Блок 5: Подробное описание работ
    # Тип объекта (многие ко многим)
    device_types = models.ManyToManyField(
        DeviceType,
        blank=True,
        related_name='events',
        verbose_name="Тип объекта"
    )
    # Объект (многие ко многим)
    devices = models.ManyToManyField(
        Device,
        blank=True,
        related_name='events',
        verbose_name="Объект"
    )
    
    # Место нахождения объекта (или внешнее)
    object_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='object_events',
        verbose_name="Место нахождения объекта"
    )
    is_object_outside = models.BooleanField(
        default=False,
        verbose_name="Объект находится за территорией Общества"
    )
    object_outside_location = models.ForeignKey(
        OutsideLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='object_outside_events',
        verbose_name="Место нахождения объекта за территорией Общества"
    )
    
    # Место выполнения работ (или внешнее)
    work_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_events',
        verbose_name="Место выполнения работ"
    )
    is_work_outside = models.BooleanField(
        default=False,
        verbose_name="Работы выполняются за территорией Общества"
    )
    work_outside_location = models.ForeignKey(
        OutsideLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_outside_events',
        verbose_name="Место выполнения работ за территорией Общества"
    )
    
    # Текстовые поля
    work_name = models.CharField(
        max_length=500,
        verbose_name="Наименование работ"
    )
    work_description = models.TextField(
        verbose_name="Подробное описание работ"
    )
    
    # Технологическая карта (связь будет через отдельную модель)
    is_tech_card_required = models.BooleanField(
        default=False,
        verbose_name="Требуется технологическая карта"
    )
    
    # Используемые материалы (многие ко многим)
    materials = models.ManyToManyField(
        Material,
        blank=True,
        related_name='events',
        verbose_name="Используемые материалы/инструменты"
    )
    materials_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий к материалам"
    )
    
    # Блок 6: Исполнители работ (многие ко многим)
    organizations = models.ManyToManyField(
        Organization,
        blank=True,
        related_name='events',
        verbose_name="Организации"
    )
    departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='events',
        verbose_name="Подразделения"
    )
    units = models.ManyToManyField(
        Unit,
        blank=True,
        related_name='events',
        verbose_name="Отделы/лаборатории/цехи/участки"
    )
    
    # Ответственный (связь ForeignKey, т.к. ответственный один)
    responsible_person = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_events',
        verbose_name="ФИО ответственного"
    )
    # Исполнители (многие ко многим)
    executors = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='executor_events',
        verbose_name="ФИО исполнителей"
    )
    # Совместные работы (многие ко многим)
    joint_workers = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='joint_events',
        verbose_name="С кем совместно будут проводиться работы"
    )
    
    # Блок 7: Согласование и оповещение
    agreed_with = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='agreed_events',
        verbose_name="С кем были согласованы работы"
    )
    notified_persons = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='notified_events',
        verbose_name="Кто был оповещён о работах"
    )
    
    # Блок 8: Доработка заявки
    revision_reason = models.TextField(
        blank=True,
        verbose_name="Причина отправки на доработку"
    )
    revision_comment = models.TextField(
        blank=True,
        verbose_name="Комментарий после доработки"
    )
    
    # Блок 0: Статус и системные поля
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT,
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата отправки на согласование")
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата согласования")
    
    class Meta:
        verbose_name = "Заявка на работы"
        verbose_name_plural = "Заявки на работы"
        ordering = ['-created_at']
        permissions = [
            ("can_approve_event", "Может согласовывать заявки"),
            ("can_edit_dictionaries", "Может редактировать справочники"),
        ]
    
    def __str__(self):
        return f"Заявка #{self.id} - {self.work_name[:50]}"
    
    def save(self, *args, **kwargs):
        """При сохранении вычисляем длительность"""
        if self.planned_start and self.planned_end:
            delta = self.planned_end - self.planned_start
            total_seconds = int(delta.total_seconds())
            self.planned_duration_days = total_seconds // (24 * 3600)
            self.planned_duration_hours = (total_seconds % (24 * 3600)) // 3600
            self.planned_duration_minutes = (total_seconds % 3600) // 60
        
        # Если нарушение сервиса = Нет, обнуляем длительность перерыва
        if not self.is_service_disruption:
            self.service_disruption_duration_days = 0
            self.service_disruption_duration_hours = 0
            self.service_disruption_duration_minutes = 0
            self.is_duration_match = False
        
        super().save(*args, **kwargs)


class TechCardStep(models.Model):
    """Технологическая карта (шаги) - Блок 5"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='tech_card_steps',
        verbose_name="Заявка"
    )
    step_number = models.PositiveIntegerField(
        verbose_name="Номер шага",
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    planned_start = models.DateTimeField(verbose_name="Планируемая дата и время начала шага")
    planned_end = models.DateTimeField(verbose_name="Планируемая дата и время окончания шага")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Шаг технологической карты"
        verbose_name_plural = "Шаги технологической карты"
        ordering = ['event', 'step_number']
        unique_together = ['event', 'step_number']
    
    def __str__(self):
        return f"Шаг {self.step_number} (Заявка #{self.event.id})"
    
    def save(self, *args, **kwargs):
        # Проверяем, что шагов не больше 50
        if self.pk is None:  # Новый шаг
            count = TechCardStep.objects.filter(event=self.event).count()
            if count >= 50:
                raise ValueError("Нельзя добавить более 50 шагов в технологическую карту")
        super().save(*args, **kwargs)


class EventDocument(models.Model):
    """Прилагаемые документы - Блок 5"""
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name="Заявка"
    )
    file = models.FileField(
        upload_to='event_documents/%Y/%m/%d/',
        verbose_name="Файл",
        validators=[
            FileExtensionValidator(
                allowed_extensions=['txt', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'doc', 'docx', 'xls', 'xlsx']
            )
        ]
    )
    description = models.CharField(max_length=200, blank=True, verbose_name="Описание")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Загрузил"
    )
    
    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Документ #{self.id} - {self.file.name}"
    
    def save(self, *args, **kwargs):
        # Проверяем размер файла (максимум 10MB)
        if self.file and self.file.size > 10 * 1024 * 1024:
            raise ValueError("Размер файла не должен превышать 10 МБ")
        super().save(*args, **kwargs)
