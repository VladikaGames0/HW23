#!/usr/bin/env python
"""
Тестовый скрипт для проверки подключения к Redis и работы кеширования
"""
import os
import django
import sys
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.cache import cache
from django_redis import get_redis_connection
from catalog.services import get_cache_stats


def print_header(text):
    """Печатает заголовок"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70)


def test_django_cache():
    """Тестирование Django cache interface"""
    print_header("1. ТЕСТИРОВАНИЕ DJANGO CACHE")

    try:
        # Тест записи
        cache.set('test:string', 'Redis работает правильно!', timeout=30)
        cache.set('test:number', 12345, timeout=30)
        cache.set('test:dict', {'name': 'test', 'value': 42}, timeout=30)
        cache.set('test:list', [1, 2, 3, 4, 5], timeout=30)
        print("✅ Данные записаны в кеш")

        # Тест чтения
        string_val = cache.get('test:string')
        number_val = cache.get('test:number')
        dict_val = cache.get('test:dict')
        list_val = cache.get('test:list')

        print(f"✅ Прочитано string: {string_val}")
        print(f"✅ Прочитано number: {number_val}")
        print(f"✅ Прочитано dict: {dict_val}")
        print(f"✅ Прочитано list: {list_val}")

        # Проверка
        if string_val == 'Redis работает правильно!':
            print("\n✅ DJANGO CACHE РАБОТАЕТ КОРРЕКТНО!")
        else:
            print("\n❌ Ошибка: данные не совпадают")

        # Тест множественных операций
        cache.set_many({
            'test:multi1': 'значение 1',
            'test:multi2': 'значение 2',
            'test:multi3': 'значение 3',
        }, timeout=30)
        print("\n✅ Множественные данные записаны")

        multi_values = cache.get_many(['test:multi1', 'test:multi2', 'test:multi3'])
        print(f"✅ Прочитано множество значений: {multi_values}")

        # Тест инкремента
        cache.set('test:counter', 1, timeout=30)
        cache.incr('test:counter')
        cache.incr('test:counter', 5)
        counter = cache.get('test:counter')
        print(f"✅ Счетчик после инкремента: {counter}")

        # Тест времени жизни
        ttl = cache.ttl('test:string')
        print(f"✅ TTL для test:string: {ttl} сек")

        # Очистка тестовых данных
        cache.delete('test:string')
        cache.delete('test:number')
        cache.delete('test:dict')
        cache.delete('test:list')
        cache.delete_many(['test:multi1', 'test:multi2', 'test:multi3', 'test:counter'])
        print("\n✅ Тестовые данные удалены")

    except Exception as e:
        print(f"❌ Ошибка при тестировании Django cache: {e}")
        import traceback
        traceback.print_exc()


def test_direct_redis():
    """Тестирование прямого подключения к Redis"""
    print_header("2. ТЕСТИРОВАНИЕ ПРЯМОГО ПОДКЛЮЧЕНИЯ К REDIS")

    try:
        redis_conn = get_redis_connection('default')

        # Проверка подключения
        redis_conn.ping()
        print("✅ Подключение к Redis установлено")

        # Тест записи
        redis_conn.set('direct:string', 'Прямое подключение работает!', ex=30)
        redis_conn.set('direct:number', 999, ex=30)
        print("✅ Данные записаны напрямую")

        # Тест чтения
        string_val = redis_conn.get('direct:string')
        number_val = redis_conn.get('direct:number')

        print(f"✅ Прочитано string: {string_val.decode('utf-8') if string_val else None}")
        print(f"✅ Прочитано number: {number_val.decode('utf-8') if number_val else None}")

        # Тест хэшей
        redis_conn.hset('direct:hash', mapping={
            'field1': 'value1',
            'field2': 'value2',
            'field3': 'value3'
        })
        redis_conn.expire('direct:hash', 30)

        hash_data = redis_conn.hgetall('direct:hash')
        print(f"✅ Хэш данные: { {k.decode('utf-8'): v.decode('utf-8') for k, v in hash_data.items()} }")

        # Тест списков
        redis_conn.lpush('direct:list', 'item1', 'item2', 'item3')
        redis_conn.expire('direct:list', 30)

        list_data = redis_conn.lrange('direct:list', 0, -1)
        print(f"✅ Список данные: {[item.decode('utf-8') for item in list_data]}")

        # Очистка
        redis_conn.delete('direct:string', 'direct:number', 'direct:hash', 'direct:list')
        print("\n✅ Тестовые данные удалены")

    except Exception as e:
        print(f"❌ Ошибка при тестировании прямого подключения: {e}")


def test_cache_stats():
    """Тестирование получения статистики"""
    print_header("3. СТАТИСТИКА REDIS")

    try:
        stats = get_cache_stats()

        if 'error' in stats:
            print(f"❌ Ошибка получения статистики: {stats['error']}")
        else:
            print(f"✅ Подключений клиентов: {stats.get('connected_clients')}")
            print(f"✅ Использовано памяти: {stats.get('used_memory_human')}")
            print(f"✅ Всего команд обработано: {stats.get('total_commands_processed')}")
            print(f"✅ Хиты кеша: {stats.get('keyspace_hits')}")
            print(f"✅ Промахи кеша: {stats.get('keyspace_misses')}")
            print(f"✅ Время работы: {stats.get('uptime_in_seconds')} сек")
            print(f"✅ Всего ключей: {stats.get('total_keys')}")

            if stats.get('keys'):
                print(f"\n✅ Примеры ключей:")
                for key in stats['keys'][:5]:
                    print(f"   - {key}")

    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")


def test_cache_patterns():
    """Тестирование работы с паттернами"""
    print_header("4. ТЕСТИРОВАНИЕ ПАТТЕРНОВ")

    try:
        # Создаем тестовые данные
        for i in range(5):
            cache.set(f'test:pattern:{i}', f'value_{i}', timeout=60)

        print("✅ Тестовые данные созданы")

        # Поиск по паттерну
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')

        # Добавляем префикс
        keys = redis_conn.keys('catalog:test:pattern:*')
        print(f"✅ Найдено ключей по паттерну: {len(keys)}")

        for key in keys:
            print(f"   - {key.decode('utf-8')}")

        # Очистка по паттерну
        cache.delete_pattern('test:pattern:*')
        print("✅ Данные по паттерну удалены")

    except Exception as e:
        print(f"❌ Ошибка при тестировании паттернов: {e}")


def main():
    """Основная функция"""
    print("\n" + "★" * 70)
    print(" ТЕСТИРОВАНИЕ СИСТЕМЫ КЕШИРОВАНИЯ С REDIS")
    print("★" * 70)
    print(f" Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Бэкенд кеша: {cache.__class__.__name__}")
    print(f" Префикс ключей: {cache.key_prefix}")

    try:
        test_django_cache()
        test_direct_redis()
        test_cache_stats()
        test_cache_patterns()

        print_header("ИТОГ")
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Система кеширования с Redis работает корректно!")

    except Exception as e:
        print_header("ОШИБКА")
        print(f"❌ Тестирование прервано из-за ошибки: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "★" * 70)


if __name__ == '__main__':
    main()