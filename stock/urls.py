from django.urls import path
from . import views

urlpatterns = [
    path('', views.produit_list, name='produit_list'),
    path('create/', views.produit_create, name='produit_create'),
    path('<int:pk>/update/', views.produit_update, name='produit_update'),
    path('<int:pk>/delete/', views.produit_delete, name='produit_delete'),
]