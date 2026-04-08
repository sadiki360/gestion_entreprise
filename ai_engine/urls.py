from django.urls import path
from . import views

urlpatterns = [
    path('',           views.ai_dashboard,      name='ai_dashboard'),
    path('promotions/', views.promotions_clients, name='promotions_clients'),
]