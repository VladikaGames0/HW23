import random
from django.core.management.base import BaseCommand
from django.db import models
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Добавляет тестовые продукты и категории в базу данных с полной информацией'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
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
            self.stdout.write(self.style.WARNING("Удаление существующих данных..."))
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
            {"name": "Бытовая техника", "description": "Техника для дома"},
            {"name": "Зоотовары", "description": "Товары для животных"},
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
            {"name": "Смартфон", "base_price": 29999.99, "weight_range": (0.15, 0.25)},
            {"name": "Ноутбук", "base_price": 89999.99, "weight_range": (1.2, 2.5)},
            {"name": "Наушники", "base_price": 4999.99, "weight_range": (0.1, 0.3)},
            {"name": "Телевизор", "base_price": 59999.99, "weight_range": (5.0, 15.0)},
            {"name": "Роман", "base_price": 1499.99, "weight_range": (0.3, 0.8)},
            {"name": "Учебник", "base_price": 999.99, "weight_range": (0.4, 1.2)},
            {"name": "Футболка", "base_price": 1999.99, "weight_range": (0.1, 0.3)},
            {"name": "Джинсы", "base_price": 3999.99, "weight_range": (0.4, 0.8)},
            {"name": "Стул", "base_price": 4999.99, "weight_range": (3.0, 7.0)},
            {"name": "Стол", "base_price": 12999.99, "weight_range": (10.0, 25.0)},
            {"name": "Мяч", "base_price": 1999.99, "weight_range": (0.3, 0.7)},
            {"name": "Гантели", "base_price": 2999.99, "weight_range": (2.0, 20.0)},
            {"name": "Крем для лица", "base_price": 999.99, "weight_range": (0.05, 0.15)},
            {"name": "Автоковрик", "base_price": 2999.99, "weight_range": (1.0, 3.0)},
            {"name": "Конструктор", "base_price": 3999.99, "weight_range": (0.5, 2.0)},
            {"name": "Кофемашина", "base_price": 24999.99, "weight_range": (3.0, 8.0)},
            {"name": "Корм для кошек", "base_price": 1499.99, "weight_range": (1.0, 5.0)},
            {"name": "Игровая консоль", "base_price": 34999.99, "weight_range": (2.0, 4.0)},
            {"name": "Фотоаппарат", "base_price": 45999.99, "weight_range": (0.5, 1.5)},
            {"name": "Умные часы", "base_price": 15999.99, "weight_range": (0.03, 0.08)},
        ]

        # Бренды и производители
        brand_names = ["Samsung", "Apple", "Xiaomi", "Sony", "LG", "Philips",
                       "Bosch", "Nike", "Adidas", "Puma", "Reebok", "Levi's",
                       "Ikea", "Asus", "Lenovo", "HP", "Dell", "Canon",
                       "Nikon", "Microsoft", "Amazon", "Google", "Huawei",
                       "OnePlus", "Vivo", "Oppo", "Realme", "Motorola"]

        # Описания для разных категорий
        descriptions = {
            "Электроника": [
                "Инновационная технология с передовыми характеристиками.",
                "Высокое качество сборки и долговечность.",
                "Энергоэффективное устройство с длительным сроком службы.",
                "Современный дизайн и удобный интерфейс.",
                "Мощная производительность для любых задач."
            ],
            "Книги": [
                "Захватывающий сюжет и глубокий смысл.",
                "Классическое произведение мировой литературы.",
                "Практическое руководство с полезными советами.",
                "Интересное чтение для любого возраста.",
                "Образовательное издание с актуальной информацией."
            ],
            "Одежда": [
                "Комфортная и стильная одежда для повседневной носки.",
                "Высококачественные материалы и прочная строчка.",
                "Модный дизайн и отличная посадка.",
                "Универсальный предмет гардероба.",
                "Дышащая ткань и удобный крой."
            ],
            "Мебель": [
                "Эргономичный дизайн для максимального комфорта.",
                "Прочная конструкция из качественных материалов.",
                "Современный стиль, который впишется в любой интерьер.",
                "Функциональная мебель с системой хранения.",
                "Экологически чистые материалы и безопасная обработка."
            ],
            "Спорт": [
                "Профессиональное оборудование для тренировок.",
                "Безопасный и надежный спортивный инвентарь.",
                "Идеально подходит для домашних тренировок.",
                "Высокое качество для интенсивного использования.",
                "Спортивный товар, проверенный атлетами."
            ]
        }

        created_count = 0
        for i in range(count):
            # Выбираем случайный шаблон
            template = random.choice(products_templates)

            # Выбираем бренд
            brand = random.choice(brand_names)

            # Генерируем уникальное название
            model_numbers = ["Pro", "Plus", "Ultra", "Lite", "Max", "Mini", "Standard", "Deluxe"]
            model = random.choice(model_numbers)
            product_name = f"{brand} {template['name']} {model} {random.randint(100, 999)}"

            # Генерируем случайную цену (±20%)
            price_variation = random.uniform(0.8, 1.3)
            price = round(template['base_price'] * price_variation, 2)

            # Выбираем категорию
            category = random.choice(categories)

            # Генерируем описание
            category_desc = descriptions.get(category.name, ["Качественный товар по доступной цене."])
            description = f"{random.choice(category_desc)} Бренд {brand} гарантирует высокое качество и надежность. "
            description += f"Идеально подходит для {random.choice(['домашнего', 'офисного', 'промышленного', 'личного'])} использования."

            # Генерируем артикул
            sku = f"{brand[:3].upper()}-{template['name'][:3].upper()}-{random.randint(1000, 9999)}"

            # Генерируем вес
            weight_min, weight_max = template['weight_range']
            weight = round(random.uniform(weight_min, weight_max), 2)

            # Генерируем габариты
            dimensions = f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(5, 50)} см"

            # Гарантия
            warranty_options = [6, 12, 18, 24, 36]
            warranty = random.choice(warranty_options)

            # Рейтинг
            rating = round(random.uniform(3.5, 5.0), 1)

            # Создаем продукт
            product = Product.objects.create(
                name=product_name,
                description=description,
                category=category,
                price=price,
                sku=sku,
                stock=random.randint(0, 200),
                is_available=random.choice([True, True, True, False]),  # 75% шанс
                manufacturer=brand,
                weight=weight,
                dimensions=dimensions,
                warranty=warranty,
                rating=rating
            )

            created_count += 1

            # Выводим информацию о созданном продукте
            status_icon = "✅" if product.is_available else "⛔"
            self.stdout.write(
                f"{status_icon} Создан продукт: {product.name[:40]}..."
            )
            self.stdout.write(
                f"   Цена: {product.price} ₽ | На складе: {product.stock} шт. | Рейтинг: {product.rating}/5"
            )
            self.stdout.write(
                f"   Категория: {product.category.name} | Артикул: {product.sku}"
            )
            self.stdout.write("   " + "-" * 50)

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Успешно создано {created_count} продуктов!"
            )
        )

        # Выводим статистику
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("📊 СТАТИСТИКА ПРОЕКТА")
        self.stdout.write("=" * 60)

        total_products = Product.objects.count()
        total_categories = Category.objects.count()

        # Статистика по наличию
        available_products = Product.objects.filter(is_available=True).count()
        out_of_stock = Product.objects.filter(stock=0).count()

        # Средние значения
        avg_price = Product.objects.aggregate(models.Avg('price'))['price__avg']
        avg_rating = Product.objects.aggregate(models.Avg('rating'))['rating__avg']
        avg_stock = Product.objects.aggregate(models.Avg('stock'))['stock__avg']

        self.stdout.write(f"📁 Всего категорий: {total_categories}")
        self.stdout.write(f"📦 Всего продуктов: {total_products}")
        self.stdout.write(f"✅ В наличии: {available_products} ({available_products / total_products * 100:.1f}%)")
        self.stdout.write(f"⛔ Нет на складе: {out_of_stock}")
        self.stdout.write(f"💰 Средняя цена: {avg_price:.2f} ₽")
        self.stdout.write(f"⭐ Средний рейтинг: {avg_rating:.1f}/5")
        self.stdout.write(f"📊 Средний запас: {avg_stock:.0f} шт.")

        # Статистика по категориям
        self.stdout.write("\n📈 ПРОДУКТОВ ПО КАТЕГОРИЯМ:")
        self.stdout.write("-" * 40)

        for category in Category.objects.all().order_by('name'):
            product_count = Product.objects.filter(category=category).count()
            category_price_avg = Product.objects.filter(category=category).aggregate(
                models.Avg('price')
            )['price__avg'] or 0

            bar = "█" * int((product_count / total_products) * 20)
            self.stdout.write(
                f"  {category.name[:15]:15} {bar:20} {product_count:3} шт. | "
                f"Ср. цена: {category_price_avg:.0f} ₽"
            )

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🚀 Проект готов к использованию!")
        self.stdout.write("=" * 60)
        self.stdout.write("\n📝 Команды для управления:")
        self.stdout.write("  python manage.py runserver     - Запустить сервер")
        self.stdout.write("  python manage.py load_catalog  - Загрузить фикстуры")
        self.stdout.write("  python manage.py shell         - Открыть Django shell")