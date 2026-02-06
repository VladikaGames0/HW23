#!/usr/bin/env python
"""
Скрипт для выполнения команд Django Shell
"""

import os
import sys
import django
from django.db import models

# Настройка Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from catalog.models import Category, Product
from django.utils import timezone


def run_commands():
    print("=" * 50)
    print("ЗАПУСК DJANGO SHELL КОМАНД")
    print("=" * 50)

    # 1. Создаем категории
    print("\n1. СОЗДАНИЕ КАТЕГОРИЙ:")
    print("-" * 30)

    categories_data = [
        ("Смартфоны", "Мобильные телефоны и аксессуары"),
        ("Ноутбуки", "Портативные компьютеры"),
        ("Бытовая техника", "Техника для дома"),
        ("Одежда", "Мужская и женская одежда"),
        ("Книги", "Художественная и учебная литература"),
    ]

    created_categories = []
    for name, description in categories_data:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        status = "СОЗДАНА" if created else "УЖЕ СУЩЕСТВОВАЛА"
        print(f"  {name}: {status}")
        created_categories.append(category)

    # 2. Создаем продукты
    print("\n2. СОЗДАНИЕ ПРОДУКТОВ:")
    print("-" * 30)

    products_data = [
        ("iPhone 15 Pro", "Флагманский смартфон Apple", 99999.99, "Смартфоны"),
        ("Samsung Galaxy S24", "Смартфон с AI-функциями", 89999.99, "Смартфоны"),
        ("Xiaomi Redmi Note 13", "Бюджетный смартфон", 24999.99, "Смартфоны"),
        ("MacBook Pro 16", "Ноутбук для профессионалов", 199999.99, "Ноутбуки"),
        ("Asus ROG Zephyrus", "Игровой ноутбук", 149999.99, "Ноутбуки"),
        ("Холодильник LG", "Двухкамерный холодильник", 79999.99, "Бытовая техника"),
        ("Футболка Nike", "Спортивная футболка", 2999.99, "Одежда"),
        ("Джинсы Levi's", "Классические джинсы", 5999.99, "Одежда"),
        ("Война и мир", "Роман Льва Толстого", 1499.99, "Книги"),
        ("Python для начинающих", "Учебник по программированию", 2999.99, "Книги"),
    ]

    for name, description, price, category_name in products_data:
        category = Category.objects.get(name=category_name)
        product, created = Product.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'category': category,
                'price': price
            }
        )
        status = "СОЗДАН" if created else "УЖЕ СУЩЕСТВОВАЛ"
        print(f"  {name}: {status}, цена: {price} руб.")

    # 3. Запросы к базе данных
    print("\n3. ЗАПРОСЫ К БАЗЕ ДАННЫХ:")
    print("-" * 30)

    # 3.1 Все категории
    print("\n3.1 ВСЕ КАТЕГОРИИ:")
    for category in Category.objects.all():
        product_count = Product.objects.filter(category=category).count()
        print(f"  {category.id}: {category.name} ({product_count} товаров)")

    # 3.2 Все продукты
    print("\n3.2 ВСЕ ПРОДУКТЫ:")
    for product in Product.objects.all():
        print(f"  {product.id}: {product.name} - {product.price} руб. [{product.category.name}]")

    # 3.3 Продукты в определенной категории
    print("\n3.3 ПРОДУКТЫ В КАТЕГОРИИ 'СМАРТФОНЫ':")
    smartphones = Product.objects.filter(category__name="Смартфоны")
    for product in smartphones:
        print(f"  {product.name}: {product.price} руб.")

    # 3.4 Обновление цены
    print("\n3.4 ОБНОВЛЕНИЕ ЦЕНЫ:")
    iphone = Product.objects.get(name__icontains="iPhone")
    print(f"  Старая цена iPhone: {iphone.price} руб.")
    iphone.price = 94999.99
    iphone.save()
    print(f"  Новая цена iPhone: {iphone.price} руб.")

    # 3.5 Удаление продукта
    print("\n3.5 УДАЛЕНИЕ ПРОДУКТА:")
    deleted_count, _ = Product.objects.filter(name__icontains="Xiaomi").delete()
    print(f"  Удалено продуктов: {deleted_count}")

    # 4. Произвольные фильтры
    print("\n4. ПРОИЗВОЛЬНЫЕ ФИЛЬТРЫ:")
    print("-" * 30)

    # 4.1 Продукты дороже 50000
    print("\n4.1 ПРОДУКТЫ ДОРОЖЕ 50000 РУБ:")
    expensive = Product.objects.filter(price__gt=50000)
    for product in expensive:
        print(f"  {product.name}: {product.price} руб.")

    # 4.2 Продукты дешевле 10000
    print("\n4.2 ПРОДУКТЫ ДЕШЕВЛЕ 10000 РУБ:")
    cheap = Product.objects.filter(price__lt=10000)
    for product in cheap:
        print(f"  {product.name}: {product.price} руб.")

    # 4.3 Поиск по описанию
    print("\n4.3 ПОИСК ПО ОПИСАНИЮ (содержит 'игр'):")
    gaming = Product.objects.filter(description__icontains='игр')
    for product in gaming:
        print(f"  {product.name}: {product.description[:50]}...")

    # 4.4 Сортировка по цене
    print("\n4.4 ПРОДУКТЫ ОТСОРТИРОВАННЫЕ ПО ЦЕНЕ (по убыванию):")
    sorted_products = Product.objects.all().order_by('-price')[:3]
    for product in sorted_products:
        print(f"  {product.name}: {product.price} руб.")

    # 5. Статистика
    print("\n5. СТАТИСТИКА:")
    print("-" * 30)

    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    avg_price = Product.objects.aggregate(models.Avg('price'))['price__avg']
    max_price = Product.objects.aggregate(models.Max('price'))['price__max']
    min_price = Product.objects.aggregate(models.Min('price'))['price__min']

    print(f"  Всего категорий: {total_categories}")
    print(f"  Всего продуктов: {total_products}")
    print(f"  Средняя цена: {avg_price:.2f} руб.")
    print(f"  Максимальная цена: {max_price:.2f} руб.")
    print(f"  Минимальная цена: {min_price:.2f} руб.")

    print("\n" + "=" * 50)
    print("ВЫПОЛНЕНИЕ ЗАВЕРШЕНО!")
    print("=" * 50)


if __name__ == "__main__":
    run_commands()