from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .analyzer import (
    analyse_ventes,
    recommandations_stock,
    recommandations_ventes,
    prediction_ventes_semaine,
    analyser_clients_promotions,
    stats_segments,
)
from .chatbot import process_question


@login_required
def ai_dashboard(request):
    context = {
        'analyse':     analyse_ventes(),
        'reco_stock':  recommandations_stock(),
        'reco_ventes': recommandations_ventes(),
        'prediction':  prediction_ventes_semaine(),
    }
    return render(request, 'ai_engine/ai_dashboard.html', context)


def promotions_clients(request):
    clients   = analyser_clients_promotions()
    stats     = stats_segments()

    total     = len(clients)
    vip_count = sum(1 for c in clients if c['segment'] == 'VIP')
    inactifs  = sum(1 for c in clients if c['segment'] == 'Inactif')
    urgent    = sum(1 for c in clients if c['segment'] in ('VIP', 'Loyal'))

    context = {
        'clients':   clients,
        'stats':     stats,
        'total':     total,
        'vip_count': vip_count,
        'inactifs':  inactifs,
        'urgent':    urgent,
    }
    return render(request, 'ai_engine/promotions_clients.html', context)


@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')
        reponse = process_question(question)
        return JsonResponse({'reponse': reponse})
    return JsonResponse({'error': 'Method not allowed'}, status=405)