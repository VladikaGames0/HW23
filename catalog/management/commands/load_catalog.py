import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Загружает тестовые данные из фикстур с предварительной очисткой базы данных'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Начинаю очистку базы данных...'))

        # Удаляем все существующие данные
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('База данных очищена'))

        # Загружаем фикстуры
        fixtures = [
            'category_data.json',
            'product_data.json'
        ]

        for fixture in fixtures:
            self.stdout.write(f'Загружаю фикстуру: {fixture}')
            try:
                # Используем стандартный путь для фикстур
                call_command('loaddata', fixture)
                self.stdout.write(self.style.SUCCESS(f'✓ Фикстура {fixture} успешно загружена'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Ошибка при загрузке {fixture}: {e}'))

        # Показываем статистику
        category_count = Category.objects.count()
        product_count = Product.objects.count()

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Загрузка завершена успешно!'))
        self.stdout.write(self.style.SUCCESS(f'Загружено категорий: {category_count}'))
        self.stdout.write(self.style.SUCCESS(f'Загружено продуктов: {product_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))