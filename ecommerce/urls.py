from django.urls import path
from . import views

urlpatterns = [   
    path('ecommerce_home', views.home, name='ecommerce_home'),
    path('products', views.product_list, name='product_list'),
    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
]