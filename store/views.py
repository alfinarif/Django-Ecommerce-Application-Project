from django.shortcuts import render

#models
from store.models import Category, Product

# import views
from django.views.generic import ListView, DeleteView

#mixin
from django.contrib.auth.mixins import LoginRequiredMixin

class Home(ListView):
    model = Product
    template_name = 'store/home.html'


class ProductDetail(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'store/product_detail.html'
