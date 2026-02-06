from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'description')
    ordering = ('id',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock', 'is_available', 'category', 'created_at')
    list_filter = ('category', 'is_available', 'manufacturer')
    search_fields = ('name', 'description', 'sku', 'manufacturer')
    list_editable = ('price', 'stock', 'is_available')
    ordering = ('id',)
    list_per_page = 20
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'category', 'sku')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock', 'is_available')
        }),
        ('Дополнительная информация', {
            'fields': ('manufacturer', 'weight', 'dimensions', 'warranty', 'rating'),
            'classes': ('collapse',)
        }),
        ('Изображение', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')