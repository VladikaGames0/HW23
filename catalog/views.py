from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def index(request):
    """Главная страница со списком товаров"""
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'catalog/index.html', {
        'products': products,
        'categories': categories
    })


def product_detail(request, product_id):
    """Страница с подробной информацией о товаре"""
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'categories': Category.objects.all(),
        'related_products': related_products
    })


def category_products(request, category_id):
    """Товары определенной категории"""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()

    return render(request, 'catalog/category.html', {
        'category': category,
        'products': products,
        'categories': categories
    })