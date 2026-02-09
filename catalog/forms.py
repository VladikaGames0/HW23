from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Форма для создания и редактирования продуктов"""

    # Запрещенные слова (в любом регистре)
    FORBIDDEN_WORDS = [
        'казино', 'криптовалюта', 'крипта', 'биржа',
        'дешево', 'бесплатно', 'обман', 'полиция', 'радар'
    ]

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price',
            'image', 'sku', 'stock', 'is_available',
            'manufacturer', 'weight', 'dimensions',
            'warranty', 'rating'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """Инициализация формы с настройкой стилей"""
        super().__init__(*args, **kwargs)

        # Настройка CSS-классов для всех полей
        for field_name, field in self.fields.items():
            if field_name not in ['is_available']:  # Для checkbox особый случай
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': f'Введите {field.label.lower()}'
                })
            else:
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })

            # Особые настройки для определенных полей
            if field_name == 'price':
                field.widget.attrs.update({
                    'step': '0.01',
                    'min': '0'
                })
            elif field_name == 'stock':
                field.widget.attrs.update({
                    'min': '0'
                })
            elif field_name == 'rating':
                field.widget.attrs.update({
                    'min': '0',
                    'max': '5',
                    'step': '0.1'
                })
            elif field_name == 'warranty':
                field.widget.attrs.update({
                    'min': '0'
                })

    def clean_name(self):
        """Валидация названия продукта"""
        name = self.cleaned_data.get('name', '').lower()

        for forbidden_word in self.FORBIDDEN_WORDS:
            if forbidden_word in name:
                raise ValidationError(
                    f'Название содержит запрещенное слово: "{forbidden_word}"'
                )

        return self.cleaned_data['name']

    def clean_description(self):
        """Валидация описания продукта"""
        description = self.cleaned_data.get('description', '').lower()

        for forbidden_word in self.FORBIDDEN_WORDS:
            if forbidden_word in description:
                raise ValidationError(
                    f'Описание содержит запрещенное слово: "{forbidden_word}"'
                )

        return self.cleaned_data['description']

    def clean_price(self):
        """Валидация цены продукта"""
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise ValidationError('Цена не может быть отрицательной')

        return price

    def clean(self):
        """Дополнительная валидация всей формы"""
        cleaned_data = super().clean()

        # Проверка наличия названия и описания
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')

        if name and len(name) < 3:
            self.add_error('name', 'Название должно содержать минимум 3 символа')

        if description and len(description) < 10:
            self.add_error('description', 'Описание должно содержать минимум 10 символов')

        # Проверка на уникальность SKU (если не текущий объект)
        sku = cleaned_data.get('sku')
        if sku:  # SKU не обязательное поле
            product_id = self.instance.id if self.instance else None
            existing_products = Product.objects.filter(sku=sku)

            if product_id:
                existing_products = existing_products.exclude(id=product_id)

            if existing_products.exists():
                self.add_error('sku', 'Продукт с таким артикулом уже существует')

        return cleaned_data