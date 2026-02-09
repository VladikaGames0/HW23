from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Q

from .models import Category, Product
from .forms import ProductForm


class IndexView(ListView):
    """Главная страница со списком товаров"""
    model = Product
    template_name = 'catalog/index.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        # Фильтрация по категории, если указана
        category_id = self.request.GET.get('category')
        if category_id:
            return Product.objects.filter(category_id=category_id, is_available=True)
        return Product.objects.filter(is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    """Страница с подробной информацией о товаре"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['related_products'] = Product.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        return context


class CategoryProductsView(ListView):
    """Товары определенной категории"""
    template_name = 'catalog/category.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        return Product.objects.filter(category=self.category, is_available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context


class ContactsView(TemplateView):
    """Страница контактов"""
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['phone'] = '+7 (999) 123-45-67'
        context['email'] = 'info@catalog.ru'
        context['address'] = 'г. Москва, ул. Примерная, д. 10'
        context['categories'] = Category.objects.all()
        return context


# Новые CBV для CRUD операций
class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание нового продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание нового продукта'
        context['submit_text'] = 'Создать продукт'
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Продукт успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование существующего продукта"""
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    pk_url_kwarg = 'product_id'

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


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление продукта"""
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    pk_url_kwarg = 'product_id'
    success_url = reverse_lazy('catalog:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление продукта: {self.object.name}'
        context['categories'] = Category.objects.all()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Продукт успешно удален!')
        return super().delete(request, *args, **kwargs)


class ProductListView(ListView):
    """Список всех продуктов (для администраторов)"""
    model = Product
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        # Поиск по названию или описанию
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Product.objects.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            ).order_by('name')
        return Product.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['categories'] = Category.objects.all()
        return context