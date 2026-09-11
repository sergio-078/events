from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from events.models import Event, Service, Device, Location, Employee

User = get_user_model()


class Command(BaseCommand):
    help = 'Настройка групп и прав доступа'
    
    def handle(self, *args, **options):
        self.stdout.write('Настройка групп и прав доступа...')
        
        # Определяем разрешения для моделей
        # Базовые права для всех моделей
        models_for_permissions = [
            Event, Service, Device, Location, Employee,
            # Добавьте другие модели по необходимости
        ]
        
        # Создаем группы
        groups_data = {
            'admin': {
                'name': 'Администратор',
                'permissions': ['add', 'change', 'delete', 'view'],
                'description': 'Полный доступ ко всем функциям системы'
            },
            'gdu': {
                'name': 'Группа ГДУ',
                'permissions': ['add', 'change', 'view'],
                'custom_permissions': ['can_approve_event'],
                'description': 'Права на согласование заявок и редактирование справочников'
            },
            'employee': {
                'name': 'Сотрудник',
                'permissions': ['add', 'change', 'view'],
                'description': 'Права на создание и редактирование заявок'
            },
            'guest': {
                'name': 'Гость',
                'permissions': ['view'],
                'description': 'Только просмотр'
            }
        }
        
        for group_key, group_info in groups_data.items():
            group, created = Group.objects.get_or_create(name=group_info['name'])
            
            if created:
                self.stdout.write(f'Создана группа: {group_info["name"]}')
            
            # Очищаем текущие разрешения
            group.permissions.clear()
            
            # Добавляем базовые разрешения
            for model in models_for_permissions:
                content_type = ContentType.objects.get_for_model(model)
                
                for perm_name in group_info['permissions']:
                    try:
                        perm = Permission.objects.get(
                            content_type=content_type,
                            codename=f'{perm_name}_{model._meta.model_name}'
                        )
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        pass
            
            # Добавляем кастомные разрешения
            if 'custom_permissions' in group_info:
                for custom_perm in group_info['custom_permissions']:
                    try:
                        # Ищем кастомное разрешение
                        perm = Permission.objects.get(
                            codename=custom_perm
                        )
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Кастомное разрешение {custom_perm} не найдено'
                            )
                        )
            
            # Добавляем специальные права для группы ГДУ
            if group_key == 'gdu':
                # Право на редактирование справочников
                for model in [Service, Device, Location, Employee]:
                    content_type = ContentType.objects.get_for_model(model)
                    try:
                        perm = Permission.objects.get(
                            content_type=content_type,
                            codename='change_%s' % model._meta.model_name
                        )
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        pass
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Группа {group_info["name"]} настроена: '
                    f'{group.permissions.count()} разрешений'
                )
            )
        
        # Создание тестового пользователя
        self.create_test_users()
        
        self.stdout.write(self.style.SUCCESS('Настройка групп завершена!'))
    
    def create_test_users(self):
        """Создание тестовых пользователей для каждой группы"""
        users_data = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@company.ru',
                'group': 'Администратор',
                'is_superuser': True,
                'is_staff': True
            },
            {
                'username': 'gdu_user',
                'password': 'gdu123',
                'email': 'gdu@company.ru',
                'group': 'Группа ГДУ',
                'is_superuser': False,
                'is_staff': True
            },
            {
                'username': 'employee',
                'password': 'employee123',
                'email': 'employee@company.ru',
                'group': 'Сотрудник',
                'is_superuser': False,
                'is_staff': False
            },
            {
                'username': 'guest',
                'password': 'guest123',
                'email': 'guest@company.ru',
                'group': 'Гость',
                'is_superuser': False,
                'is_staff': False
            }
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_superuser': user_data['is_superuser'],
                    'is_staff': user_data['is_staff']
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    f'Создан пользователь: {user_data["username"]} '
                    f'(пароль: {user_data["password"]})'
                )
            
            # Добавляем в группу
            try:
                group = Group.objects.get(name=user_data['group'])
                user.groups.add(group)
                user.save()
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'Группа {user_data["group"]} не найдена'
                    )
                )
                