from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UserRegistrationForm, UserLoginForm
from .models import User


class UserRegistrationView(CreateView):
    """Контроллер регистрации пользователя"""

    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Отправка приветственного письма при успешной регистрации"""
        response = super().form_valid(form)

        # Данные пользователя
        user_email = self.object.email

        # Формируем текст письма
        subject = 'Добро пожаловать в наш каталог товаров!'
        message = f"""
        Здравствуйте!

        Спасибо за регистрацию в нашем каталоге товаров!

        Ваш email: {user_email}

        Теперь вы можете:
        ✅ Просматривать все товары
        ✅ Добавлять новые товары
        ✅ Редактировать свои товары
        ✅ Оставлять комментарии

        С уважением,
        Команда каталога товаров
        """

        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1>Добро пожаловать!</h1>
            </div>

            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 0 0 5px 5px;">
                <p style="font-size: 16px;">Здравствуйте!</p>

                <p style="font-size: 16px;">Спасибо за регистрацию в нашем каталоге товаров!</p>

                <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Ваш email:</strong> {user_email}</p>
                </div>

                <h3 style="color: #333;">Теперь вы можете:</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px;">
                        ✅ Просматривать все товары
                    </li>
                    <li style="margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px;">
                        ✅ Добавлять новые товары
                    </li>
                    <li style="margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px;">
                        ✅ Редактировать свои товары
                    </li>
                    <li style="margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px;">
                        ✅ Оставлять комментарии
                    </li>
                </ul>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://127.0.0.1:8000" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; font-size: 16px;">
                        Перейти в каталог
                    </a>
                </div>

                <p style="margin-top: 30px; font-size: 14px; color: #666; text-align: center;">
                    С уважением,<br>
                    Команда каталога товаров
                </p>
            </div>
        </body>
        </html>
        """

        try:
            # Отправляем письмо
            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user_email],
                fail_silently=False,
            )
            messages.success(
                self.request,
                'Регистрация прошла успешно! '
                'Приветственное письмо отправлено на ваш email.'
            )
        except Exception as e:
            # Логируем ошибку, но не прерываем регистрацию
            print(f"Ошибка отправки письма: {e}")
            messages.warning(
                self.request,
                'Регистрация прошла успешно, '
                'но не удалось отправить приветственное письмо.'
            )

        # Автоматически авторизуем пользователя после регистрации
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(self.request, user)
            messages.info(self.request, 'Вы автоматически авторизованы в системе.')

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context


class UserLoginView(LoginView):
    """Контроллер авторизации пользователя"""

    form_class = UserLoginForm
    template_name = 'users/login.html'

    def get_success_url(self):
        return reverse_lazy('catalog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в систему'
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        """Добавляем сообщение об успешном входе"""
        messages.success(self.request, f'Добро пожаловать, {form.get_user().email}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Добавляем сообщение об ошибке"""
        messages.error(self.request, 'Неверный email или пароль.')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """Контроллер выхода из системы"""

    next_page = reverse_lazy('catalog:index')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль пользователя (только для авторизованных)"""

    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль пользователя'
        # Для меню категорий
        from catalog.models import Category
        context['categories'] = Category.objects.all()
        return context