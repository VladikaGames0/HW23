from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
]