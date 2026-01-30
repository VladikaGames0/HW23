import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Добавляет тестовые продукты и категории в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Количество продуктов для создания'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить все существующие данные перед добавлением'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            self.stdout.write("Удаление существующих данных...")
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS("Все данные удалены!")
            )

        # Создаем категории
        categories_data = [
            {"name": "Электроника", "description": "Техника и гаджеты"},
            {"name": "Книги", "description": "Литература разных жанров"},
            {"name": "Одежда", "description": "Мужская и женская одежда"},
            {"name": "Мебель", "description": "Домашняя и офисная мебель"},
            {"name": "Спорт", "description": "Спортивные товары"},
            {"name": "Красота", "description": "Косметика и уход"},
            {"name": "Автотовары", "description": "Автомобильные аксессуары"},
            {"name": "Игрушки", "description": "Детские игрушки"},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]}
            )
            categories.append(category)
            self.stdout.write(
                f"Категория '{category.name}' {'создана' if created else 'уже существует'}"
            )

        # Генератор продуктов
        products_templates = [
            {"name": "Смартфон", "base_price": 29999.99},
            {"name": "Ноутбук", "base_price": 89999.99},
            {"name": "Наушники", "base_price": 4999.99},
            {"name": "Телевизор", "base_price": 59999.99},
            {"name": "Роман", "base_price": 1499.99},
            {"name": "Учебник", "base_price": 999.99},
            {"name": "Футболка", "base_price": 1999.99},
            {"name": "Джинсы", "base_price": 3999.99},
            {"name": "Стул", "base_price": 4999.99},
            {"name": "Стол", "base_price": 12999.99},
            {"name": "Мяч", "base_price": 1999.99},
            {"name": "Гантели", "base_price": 2999.99},
            {"name": "Крем для лица", "base_price": 999.99},
            {"name": "Автоковрик", "base_price": 2999.99},
            {"name": "Конструктор", "base_price": 3999.99},
        ]

        created_count = 0
        for i in range(count):
            # Выбираем случайный шаблон
            template = random.choice(products_templates)

            # Генерируем уникальное название
            brand_names = ["Samsung", "Apple", "Xiaomi", "Sony", "LG", "Philips",
                           "Bosch", "Nike", "Adidas", "Puma", "Reebok", "Levi's"]
            brand = random.choice(brand_names)
            product_name = f"{brand} {template['name']} {i + 1}"

            # Генерируем случайную цену (±20%)
            price_variation = random.uniform(0.8, 1.2)
            price = round(template['base_price'] * price_variation, 2)

            # Создаем продукт
            product = Product.objects.create(
                name=product_name,
                description=f"Высококачественный {template['name'].lower()} от {brand}. "
                            f"Идеальное сочетание цены и качества.",
                category=random.choice(categories),
                price=price
            )

            created_count += 1
            self.stdout.write(
                f"Создан продукт: {product.name} - {product.price} руб. "
                f"(категория: {product.category.name})"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nУспешно создано {created_count} продуктов!"
            )
        )

        # Выводим статистику
        self.stdout.write("\n=== Статистика ===")
        self.stdout.write(f"Всего категорий: {Category.objects.count()}")
        self.stdout.write(f"Всего продуктов: {Product.objects.count()}")

        # Статистика по категориям
        self.stdout.write("\nПродуктов по категориям:")
        for category in Category.objects.all():
            product_count = Product.objects.filter(category=category).count()
            self.stdout.write(f"  {category.name}: {product_count} продуктов")