from django.urls import path
from .views import IndexView, ProductDetailView, CategoryProductsView, ContactsView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("product/<int:product_id>/", ProductDetailView.as_view(), name="product_detail"),
    path("category/<int:category_id>/", CategoryProductsView.as_view(), name="category_products"),
    path("contacts/", ContactsView.as_view(), name="contacts"),
]