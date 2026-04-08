from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('clients/', include('clients.urls')),
    path('stock/', include('stock.urls')),
    path('ventes/', include('ventes.urls')),
    path('ai/', include('ai_engine.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]