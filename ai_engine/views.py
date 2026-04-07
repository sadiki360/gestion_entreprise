from django.shortcuts import render
from .analyzer import (
    analyse_ventes,
    recommandations_stock,
    recommandations_ventes,
    prediction_ventes_semaine,
)


def ai_dashboard(request):
    context = {
        'analyse': analyse_ventes(),
        'reco_stock': recommandations_stock(),
        'reco_ventes': recommandations_ventes(),
        'prediction': prediction_ventes_semaine(),
    }
    return render(request, 'ai_engine/ai_dashboard.html', context)