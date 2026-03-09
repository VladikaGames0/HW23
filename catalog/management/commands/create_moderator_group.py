from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создает группу "Модератор продуктов" с необходимыми разрешениями'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Создание группы "Модератор продуктов"...'))

        # Получаем content type для модели Product
        content_type = ContentType.objects.get_for_model(Product)

        # Получаем необходимые разрешения
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=['can_unpublish_product', 'delete_product']
        )

        # Создаем или получаем группу
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        # Добавляем разрешения к группе
        moderator_group.permissions.set(permissions)

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модератор продуктов" успешно создана!'))
        else:
            self.stdout.write(self.style.SUCCESS('Группа "Модератор продуктов" уже существует, разрешения обновлены'))

        # Выводим информацию о разрешениях
        self.stdout.write('\nРазрешения группы:')
        for perm in moderator_group.permissions.all():
            self.stdout.write(f'  - {perm.name}')