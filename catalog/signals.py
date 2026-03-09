from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    """Очищает кеш при изменении или удалении продукта"""
    # Очищаем кеш главной страницы (все страницы)
    cache.delete_pattern('index_products_*')

    # Очищаем кеш категории
    if instance.category_id:
        cache.delete_pattern(f'category_{instance.category_id}_*')
        cache.delete_pattern(f'category_stats_{instance.category_id}*')

    # Очищаем кеш конкретного продукта
    cache.delete_pattern(f'product_{instance.id}_*')
    cache.delete_pattern(f'related_products_{instance.id}*')

    print(f"✅ Кеш очищен после изменения продукта {instance.id}")


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    """Очищает кеш при изменении категории"""
    # Очищаем кеш всех категорий
    cache.delete_pattern('all_categories')

    # Очищаем кеш конкретной категории
    cache.delete_pattern(f'category_{instance.id}_*')
    cache.delete_pattern(f'category_stats_{instance.id}*')

    # Очищаем кеш главной страницы
    cache.delete_pattern('index_products_*')

    print(f"✅ Кеш очищен после изменения категории {instance.id}")