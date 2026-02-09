from django.urls import path
from .views import (
    IndexView, ProductDetailView, CategoryProductsView, ContactsView,
    ProductCreateView, ProductUpdateView, ProductDeleteView, ProductListView
)

app_name = 'catalog'

urlpatterns = [
    path("", IndexView.as_view(), name="index"),

    path("product/<int:product_id>/", ProductDetailView.as_view(), name="product_detail"),
    path("category/<int:category_id>/", CategoryProductsView.as_view(), name="category_products"),
    path("contacts/", ContactsView.as_view(), name="contacts"),

    # CRUD маршруты
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("product/<int:product_id>/edit/", ProductUpdateView.as_view(), name="product_edit"),
    path("product/<int:product_id>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]