from django.core.cache import cache
from django.db.models import Q
from .models import Product, Category


def get_cached_product(product_id, user=None):
    """
    Получает продукт с кешированием
    """
    cache_key = f'product_{product_id}'

    if user and user.is_authenticated:
        cache_key += f'_user_{user.id}'

    product = cache.get(cache_key)

    if not product:
        try:
            queryset = Product.objects.select_related('category', 'owner')
            if user and user.is_authenticated:
                product = queryset.get(
                    Q(id=product_id) &
                    (Q(publication_status='published') | Q(owner=user))
                )
            else:
                product = queryset.get(id=product_id, publication_status='published')

            # Добавляем в кеш на 15 минут
            cache.set(cache_key, product, timeout=60 * 15)
            print(f"✅ Продукт {product_id} загружен из БД")
        except Product.DoesNotExist:
            return None
    else:
        print(f"✅ Продукт {product_id} загружен из кеша")

    return product


def get_cached_categories():
    """
    Получает все категории с кешированием
    """
    cache_key = 'all_categories'
    categories = cache.get(cache_key)

    if not categories:
        categories = list(Category.objects.all())
        cache.set(cache_key, categories, timeout=60 * 60)  # 1 час
        print("✅ Категории загружены из БД")
    else:
        print("✅ Категории загружены из кеша")

    return categories


def get_cached_related_products(product, limit=4):
    """
    Получает похожие товары с кешированием
    """
    cache_key = f'related_products_{product.id}'
    related = cache.get(cache_key)

    if not related:
        related = list(Product.objects.filter(
            category=product.category,
            publication_status='published'
        ).exclude(id=product.id)[:limit])
        cache.set(cache_key, related, timeout=60 * 30)  # 30 минут
        print(f"✅ Похожие товары для продукта {product.id} загружены из БД")
    else:
        print(f"✅ Похожие товары для продукта {product.id} загружены из кеша")

    return related


def get_products_by_category(category_id, user=None, published_only=True):
    """
    Сервисная функция для получения продуктов в указанной категории с кешированием

    Args:
        category_id: ID категории
        user: пользователь (для проверки прав)
        published_only: только опубликованные

    Returns:
        tuple: (category, products)
    """
    # Ключ для кеша зависит от параметров
    cache_key = f'category_{category_id}_products'

    if user and user.is_authenticated:
        if user.has_perm('catalog.can_unpublish_product'):
            cache_key += '_moderator'
        else:
            cache_key += f'_user_{user.id}'

    if not published_only:
        cache_key += '_all'

    # Пытаемся получить из кеша
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"✅ Данные категории {category_id} загружены из кеша")
        return cached_data

    # Получаем категорию
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return None, []

    # Базовый запрос
    queryset = Product.objects.filter(category=category)

    # Фильтрация по статусу публикации
    if published_only:
        if user and user.is_authenticated:
            if user.has_perm('catalog.can_unpublish_product'):
                # Модератор видит все
                pass
            else:
                # Обычный пользователь видит опубликованные и свои
                queryset = queryset.filter(
                    Q(publication_status='published') | Q(owner=user)
                )
        else:
            # Аноним видит только опубликованные
            queryset = queryset.filter(publication_status='published')

    products = list(queryset.select_related('owner'))

    result = (category, products)

    # Кешируем результат
    timeout = 60 * 5 if user and user.is_authenticated else 60 * 15
    cache.set(cache_key, result, timeout=timeout)
    print(f"✅ Данные категории {category_id} загружены из БД")

    return result


def get_category_stats(category_id):
    """
    Получает статистику по категории с кешированием
    """
    cache_key = f'category_stats_{category_id}'
    stats = cache.get(cache_key)

    if not stats:
        products = Product.objects.filter(
            category_id=category_id,
            publication_status='published'
        )

        count = products.count()
        if count > 0:
            prices = [p.price for p in products]
            stats = {
                'count': count,
                'avg_price': sum(prices) / len(prices),
                'min_price': min(prices),
                'max_price': max(prices),
            }
        else:
            stats = {
                'count': 0,
                'avg_price': 0,
                'min_price': 0,
                'max_price': 0,
            }

        cache.set(cache_key, stats, timeout=60 * 30)  # 30 минут
        print(f"✅ Статистика категории {category_id} загружена из БД")
    else:
        print(f"✅ Статистика категории {category_id} загружена из кеша")

    return stats


def get_cached_index_products(category_id=None, page=1):
    """
    Получает список продуктов для главной страницы с кешированием
    """
    cache_key = f'index_products_cat_{category_id if category_id else "all"}_page_{page}'

    products = cache.get(cache_key)

    if not products:
        if category_id:
            products = list(Product.objects.filter(
                category_id=category_id,
                publication_status='published'
            ).select_related('category', 'owner').order_by('-created_at'))
        else:
            products = list(Product.objects.filter(
                publication_status='published'
            ).select_related('category', 'owner').order_by('-created_at'))

        cache.set(cache_key, products, timeout=60 * 10)  # 10 минут
        print(f"✅ Список товаров загружен из БД (ключ: {cache_key})")
    else:
        print(f"✅ Список товаров загружен из кеша (ключ: {cache_key})")

    return products


def clear_product_cache(product_id):
    """
    Очищает кеш продукта при изменении
    """
    cache.delete_pattern(f'product_{product_id}_*')
    cache.delete_pattern(f'related_products_{product_id}*')
    print(f"✅ Кеш продукта {product_id} очищен")


def clear_category_cache(category_id):
    """
    Очищает кеш категории при изменении
    """
    cache.delete_pattern(f'category_{category_id}_*')
    cache.delete_pattern(f'category_stats_{category_id}*')
    print(f"✅ Кеш категории {category_id} очищен")


def clear_all_product_caches():
    """
    Очищает все кеши связанные с продуктами
    """
    cache.delete_pattern('index_products_*')
    cache.delete_pattern('product_*')
    cache.delete_pattern('related_products_*')
    cache.delete_pattern('category_*')
    print("✅ Все кеши продуктов очищены")


def get_cache_stats():
    """
    Возвращает статистику использования кеша
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        info = redis_conn.info()

        # Получаем список всех ключей
        keys = redis_conn.keys('catalog:*')

        return {
            'connected_clients': info.get('connected_clients'),
            'used_memory_human': info.get('used_memory_human'),
            'total_commands_processed': info.get('total_commands_processed'),
            'keyspace_hits': info.get('keyspace_hits'),
            'keyspace_misses': info.get('keyspace_misses'),
            'uptime_in_seconds': info.get('uptime_in_seconds'),
            'total_keys': len(keys),
            'keys': [k.decode('utf-8') for k in keys[:10]],  # Первые 10 ключей
        }
    except Exception as e:
        return {'error': str(e)}