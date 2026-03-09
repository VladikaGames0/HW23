@echo off
echo Настройка проекта Django...

REM Создаем виртуальное окружение
python -m venv venv
call venv\Scripts\activate

REM Обновляем pip
python -m pip install --upgrade pip

REM Устанавливаем зависимости
pip install django pillow python-dotenv

REM Проверяем установку
python -c "import django; print('Django версия:', django.get_version())"
python -c "try: from PIL import Image; print('Pillow установлен'); except: print('Ошибка Pillow')"

REM Применяем миграции
python manage.py migrate

REM Создаем суперпользователя
echo.
echo Создание суперпользователя...
python manage.py createsuperuser

REM Загружаем тестовые данные
echo.
echo Загрузка тестовых данных...
python manage.py load_catalog

echo.
echo Проект настроен!
echo Запустите сервер: python manage.py runserver
pause