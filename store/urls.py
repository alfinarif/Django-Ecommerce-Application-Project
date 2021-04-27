from django.urls import path
from store import views
app_name = 'store'

urlpatterns = [
    path('', views.Home.as_view(), name='index'),
    path('product/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
]