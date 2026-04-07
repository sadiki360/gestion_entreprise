from django.urls import path
from . import views

urlpatterns = [
    path('', views.vente_list, name='vente_list'),
    path('create/', views.vente_create, name='vente_create'),
    path('<int:pk>/', views.vente_detail, name='vente_detail'),
    path('<int:pk>/delete/', views.vente_delete, name='vente_delete'),
]