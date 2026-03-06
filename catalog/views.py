from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.exceptions import PermissionDenied

from .models import Category, Product
from .forms import ProductForm


class IndexView(ListView):
    """Главная страница со списком товаров - ОБЩЕДОСТУПНАЯ"""
    model = Product
    template_name = 'catalog/index.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        # Показываем только опубликованные товары
        category_id = self.request.GET.get('category')
        if category_id:
            return Product.objects.filter(
                category_id=category_id,
                publication_status='published'
            )
        return Product.objects.filter(publication_status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """Страница с подробной информацией о товаре - ОБЩЕДОСТУПНАЯ"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get_queryset(self):
        # Владельцы видят свои товары даже если не опубликованы
        if self.request.user.is_authenticated:
            return Product.objects.filter(
                Q(publication_status='published') | Q(owner=self.request.user)
            )
        return Product.objects.filter(publication_status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            publication_status='published'
        ).exclude(id=self.object.id)[:4]
        return context


class CategoryProductsView(ListView):
    """Товары определенной категории - ОБЩЕДОСТУПНАЯ"""
    template_name = 'catalog/category.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        # Показываем только опубликованные товары
        return Product.objects.filter(
            category=self.category,
            publication_status='published'
        ).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()

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


class ContactsView(TemplateView):
    """Страница контактов - ОБЩЕДОСТУПНАЯ"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['phone'] = '+7 (999) 123-45-67'
        context['email'] = 'info@catalog.ru'
        context['address'] = 'г. Москва, ул. Примерная, д. 10'
        context['categories'] = Category.objects.all()
        return context


# Миксин для проверки владельца или модератора
class OwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    """Проверяет, является ли пользователь владельцем или модератором"""

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        # Владелец или модератор (имеет право удалять любой продукт)
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
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        # Автоматически привязываем продукт к текущему пользователю
        form.instance.owner = self.request.user
        # Новый продукт по умолчанию создается как черновик
        form.instance.publication_status = 'draft'
        messages.success(self.request, 'Продукт успешно создан! Он отправлен на модерацию.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, UpdateView):
    """Редактирование существующего продукта - ТОЛЬКО ДЛЯ ВЛАДЕЛЬЦА ИЛИ МОДЕРАТОРА"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    pk_url_kwarg = 'product_id'

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'
    raise_exception = True  # Показывать 403 вместо редиректа на логин

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование продукта: {self.object.name}'
        context['submit_text'] = 'Сохранить изменения'
        context['is_update'] = True
        context['categories'] = Category.objects.all()
        return context

    def get_success_url(self):
        messages.success(self.request, 'Продукт успешно обновлен!')
        return reverse('catalog:product_detail', kwargs={'product_id': self.object.id})

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductDeleteView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, DeleteView):
    """Удаление продукта - ТОЛЬКО ДЛЯ ВЛАДЕЛЬЦА ИЛИ МОДЕРАТОРА"""
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
        context['categories'] = Category.objects.all()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


class ProductListView(LoginRequiredMixin, ListView):
    """Список всех продуктов (для администраторов) - ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        base_queryset = Product.objects.all()

        # Для обычных пользователей показываем только их продукты
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
        context['categories'] = Category.objects.all()
        context['is_moderator'] = self.request.user.has_perm('catalog.can_delete_any_product')
        return context