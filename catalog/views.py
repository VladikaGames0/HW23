from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Category, Product


class IndexView(ListView):
    model = Product
    template_name = 'catalog/index.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
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
    template_name = 'catalog/category.html'
    context_object_name = 'products'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
        return Product.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context


class ContactsView(TemplateView):
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['phone'] = '+7 (999) 123-45-67'
        context['email'] = 'info@catalog.ru'
        context['address'] = 'г. Москва, ул. Примерная, д. 10'
        return context