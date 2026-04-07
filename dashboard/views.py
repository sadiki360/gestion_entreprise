from django.shortcuts import render
from clients.models import Client
from stock.models import Produit
from ventes.models import Vente
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

def dashboard(request):
    total_clients = Client.objects.count()
    total_produits = Produit.objects.count()
    total_ventes = Vente.objects.count()
    chiffre_affaires = Vente.objects.aggregate(Sum('total'))['total__sum'] or 0
    
    produits_alerte = Produit.objects.filter(quantite__lte=10)
    
    ventes_recentes = Vente.objects.order_by('-date_vente')[:5]
    
    last_7_days = []
    last_7_labels = []
    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        total = Vente.objects.filter(date_vente__date=day).aggregate(Sum('total'))['total__sum'] or 0
        last_7_days.append(float(total))
        last_7_labels.append(day.strftime('%d/%m'))

    context = {
        'total_clients': total_clients,
        'total_produits': total_produits,
        'total_ventes': total_ventes,
        'chiffre_affaires': chiffre_affaires,
        'produits_alerte': produits_alerte,
        'ventes_recentes': ventes_recentes,
        'last_7_days': last_7_days,
        'last_7_labels': last_7_labels,
    }
    return render(request, 'dashboard/dashboard.html', context)