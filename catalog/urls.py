from django.urls import path
from .views import (
    IndexView, ProductDetailView, CategoryProductsView, ContactsView,
    ProductCreateView, ProductUpdateView, ProductDeleteView, ProductListView,
    CategoryProductsDetailView, ClearCacheView
)

app_name = 'catalog'

urlpatterns = [
    # Общедоступные страницы
    path("", IndexView.as_view(), name="index"),
    path("product/<int:product_id>/", ProductDetailView.as_view(), name="product_detail"),
    path("category/<int:category_id>/", CategoryProductsView.as_view(), name="category_products"),
    path("category/<int:category_id>/products/", CategoryProductsDetailView.as_view(), name="category_products_detail"),
    path("contacts/", ContactsView.as_view(), name="contacts"),

    # Страницы с ограниченным доступом
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:product_id>/edit/", ProductUpdateView.as_view(), name="product_edit"),
    path("product/<int:product_id>/delete/", ProductDeleteView.as_view(), name="product_delete"),

    # Утилиты (только для модераторов)
    path("clear-cache/", ClearCacheView.as_view(), name="clear_cache"),
]