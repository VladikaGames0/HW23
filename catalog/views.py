from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from .models import Category, Product
from .forms import ProductForm
from .services import (
    get_cached_product, get_cached_categories, get_cached_related_products,
    get_products_by_category, get_category_stats, get_cached_index_products,
    clear_all_product_caches, get_cache_stats
)


class IndexView(ListView):
    """Главная страница со списком товаров - с низкоуровневым кешированием"""
    model = Product
    template_name = 'catalog/index.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        # Получаем параметры запроса
        category_id = self.request.GET.get('category')
        page = self.request.GET.get('page', 1)

        # Используем сервисную функцию с кешированием
        return get_cached_index_products(category_id, page)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кеширование категорий через сервисную функцию
        context['categories'] = get_cached_categories()

        # Добавляем информацию о кеше для отладки
        if self.request.GET.get('debug') == '1':
            context['cache_stats'] = get_cache_stats()
            context['debug'] = True

        return context


class ProductDetailView(DetailView):
    """Страница с подробной информацией о товаре - с кешированием"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    @method_decorator(cache_page(60 * 15))  # Кешировать страницу на 15 минут
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        # Используем сервисную функцию с кешированием
        return get_cached_product(
            self.kwargs['product_id'],
            user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Кеширование категорий
        context['categories'] = get_cached_categories()

        # Кеширование похожих товаров
        context['related_products'] = get_cached_related_products(self.object)

        return context


class CategoryProductsView(ListView):
    """Товары определенной категории - ОБЩЕДОСТУПНАЯ"""
    template_name = 'catalog/category.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        return Product.objects.filter(
            category=self.category,
            publication_status='published'
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = get_cached_categories()

        products = context['products']
        if products:
            prices = [p.price for p in products]
            context['avg_price'] = sum(prices) / len(prices)
            context['min_price'] = min(prices)
            context['max_price'] = max(prices)
        else:
            context['avg_price'] = 0
            context['min_price'] = 0
            context['max_price'] = 0

        return context


class CategoryProductsDetailView(TemplateView):
    """Отдельное представление для отображения продуктов категории с кешированием"""
    template_name = 'catalog/category_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_id = self.kwargs.get('category_id')

        # Получаем категорию и продукты через сервисную функцию с кешированием
        category, products = get_products_by_category(
            category_id,
            user=self.request.user,
            published_only=True
        )

        if not category:
            from django.http import Http404
            raise Http404("Категория не найдена")

        context['category'] = category
        context['products'] = products

        # Получаем статистику с кешированием
        stats = get_category_stats(category_id)
        context.update(stats)

        # Все категории для меню (тоже с кешированием)
        context['categories'] = get_cached_categories()
        context['title'] = f'Товары в категории: {category.name}'

        # Для отладки
        if self.request.GET.get('debug') == '1':
            context['cache_stats'] = get_cache_stats()
            context['debug'] = True

        return context


class ContactsView(TemplateView):
    """Страница контактов - ОБЩЕДОСТУПНАЯ"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['phone'] = '+7 (999) 123-45-67'
        context['email'] = 'info@catalog.ru'
        context['address'] = 'г. Москва, ул. Примерная, д. 10'
        context['categories'] = get_cached_categories()
        return context


# Миксин для проверки владельца или модератора
class OwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    """Проверяет, является ли пользователь владельцем или модератором"""

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user == product.owner or user.has_perm('catalog.can_delete_any_product')


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание нового продукта - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового продукта'
        context['submit_text'] = 'Создать продукт'
        context['categories'] = get_cached_categories()
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.publication_status = 'draft'
        messages.success(self.request, 'Продукт успешно создан! Он отправлен на модерацию.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, UpdateView):
    """Редактирование существующего продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    pk_url_kwarg = 'product_id'

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'
    raise_exception = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование продукта: {self.object.name}'
        context['submit_text'] = 'Сохранить изменения'
        context['is_update'] = True
        context['categories'] = get_cached_categories()
        return context

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно обновлен!')
        return reverse('catalog:product_detail', kwargs={'product_id': self.object.id})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, DeleteView):
    """Удаление продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    pk_url_kwarg = 'product_id'
    success_url = reverse_lazy('catalog:product_list')

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление продукта: {self.object.name}'
        context['categories'] = get_cached_categories()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


class ProductListView(LoginRequiredMixin, ListView):
    """Список всех продуктов (для администраторов)"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        base_queryset = Product.objects.all()

        if not self.request.user.has_perm('catalog.can_delete_any_product'):
            base_queryset = base_queryset.filter(owner=self.request.user)

        if search_query:
            return base_queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            ).order_by('name')
        return base_queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['categories'] = get_cached_categories()
        context['is_moderator'] = self.request.user.has_perm('catalog.can_delete_any_product')
        return context


class ClearCacheView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Представление для очистки кеша (только для модераторов)"""
    template_name = 'catalog/clear_cache.html'

    def test_func(self):
        return self.request.user.has_perm('catalog.can_delete_any_product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_cached_categories()
        context['cache_stats'] = get_cache_stats()
        return context

    def post(self, request, *args, **kwargs):
        # Очищаем весь кеш
        clear_all_product_caches()
        messages.success(request, 'Кеш успешно очищен!')
        return redirect('catalog:index')