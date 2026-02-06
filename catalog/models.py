from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name='Наименование')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Категория'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за покупку')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата последнего изменения')

    # Добавим новые поля
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='Артикул')
    stock = models.IntegerField(default=0, verbose_name='Количество на складе')
    is_available = models.BooleanField(default=True, verbose_name='В наличии')
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name='Производитель')
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name='Вес (кг)')
    dimensions = models.CharField(max_length=50, blank=True, null=True, verbose_name='Габариты')
    warranty = models.IntegerField(default=12, verbose_name='Гарантия (мес)')
    rating = models.FloatField(default=0.0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']

    def __str__(self):
        return self.name

    # Метод для проверки наличия
    def in_stock(self):
        return self.stock > 0 and self.is_available

    # Метод для расчета скидки (пример)
    def get_discounted_price(self, discount_percent=10):
        return round(self.price * (1 - discount_percent / 100), 2)