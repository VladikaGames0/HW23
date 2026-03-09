import os
import django
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

try:
    result = send_mail(
        subject='Тестовое письмо из Django',
        message='Если вы видите это письмо, то почта работает правильно!',
        from_email='vladikagames22@gmail.com',
        recipient_list=['vladikagames22@gmail.com'],  # Отправляем себе же
        fail_silently=False,
    )
    print(f"✅ Письмо отправлено! Результат: {result}")
except Exception as e:
    print(f"❌ Ошибка отправки: {e}")

    # Дополнительная диагностика
    import smtplib

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('vladikagames22@gmail.com', 'irkobpfzuzgtfmpr')
        print("✅ SMTP соединение успешно!")
        server.quit()
    except Exception as smtp_error:
        print(f"❌ SMTP ошибка: {smtp_error}")