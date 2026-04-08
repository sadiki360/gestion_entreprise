from django.shortcuts import render
from .analyzer import (
    analyse_ventes,
    recommandations_stock,
    recommandations_ventes,
    prediction_ventes_semaine,
    analyser_clients_promotions,
    stats_segments,
)


def ai_dashboard(request):
    context = {
        'analyse':      analyse_ventes(),
        'reco_stock':   recommandations_stock(),
        'reco_ventes':  recommandations_ventes(),
        'prediction':   prediction_ventes_semaine(),
    }
    return render(request, 'ai_engine/ai_dashboard.html', context)


def promotions_clients(request):
    clients   = analyser_clients_promotions()
    stats     = stats_segments()

    # Statistiques rapides pour les cartes du haut
    total     = len(clients)
    vip_count = sum(1 for c in clients if c['segment'] == 'VIP')
    inactifs  = sum(1 for c in clients if c['segment'] == 'Inactif')
    urgent    = sum(1 for c in clients if c['segment'] in ('VIP', 'Loyal'))

    context = {
        'clients':    clients,
        'stats':      stats,
        'total':      total,
        'vip_count':  vip_count,
        'inactifs':   inactifs,
        'urgent':     urgent,
    }
    return render(request, 'ai_engine/promotions_clients.html', context)