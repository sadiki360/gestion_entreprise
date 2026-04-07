import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta


def get_ventes_data():
    from ventes.models import Vente, LigneVente
    ventes = Vente.objects.all().values('id', 'date_vente', 'total', 'client_id')
    return pd.DataFrame(list(ventes))


def get_stock_data():
    from stock.models import Produit
    produits = Produit.objects.all().values('id', 'nom', 'quantite', 'prix', 'seuil_alerte')
    return pd.DataFrame(list(produits))


def analyse_ventes():
    df = get_ventes_data()
    if df.empty:
        return {
            'total_ca': 0,
            'moyenne_journaliere': 0,
            'meilleur_jour': None,
            'tendance': 'Pas assez de données',
            'evolution': 0,
        }

    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['date'] = df['date_vente'].dt.date
    df['total'] = df['total'].astype(float)

    total_ca = float(df['total'].sum())
    moyenne_journaliere = float(df.groupby('date')['total'].sum().mean())

    par_jour = df.groupby('date')['total'].sum()
    meilleur_jour = str(par_jour.idxmax()) if not par_jour.empty else None

    if len(par_jour) >= 2:
        debut = float(par_jour.iloc[0])
        fin = float(par_jour.iloc[-1])
        evolution = ((fin - debut) / debut * 100) if debut > 0 else 0
        tendance = 'En hausse' if evolution > 0 else 'En baisse' if evolution < 0 else 'Stable'
    else:
        evolution = 0
        tendance = 'Stable'

    return {
        'total_ca': round(total_ca, 2),
        'moyenne_journaliere': round(moyenne_journaliere, 2),
        'meilleur_jour': meilleur_jour,
        'tendance': tendance,
        'evolution': round(evolution, 2),
    }


def recommandations_stock():
    df = get_stock_data()
    if df.empty:
        return []

    recommandations = []
    for _, row in df.iterrows():
        if row['quantite'] == 0:
            recommandations.append({
                'produit': row['nom'],
                'type': 'danger',
                'icone': 'bi-x-circle',
                'message': f"Rupture de stock — commander immédiatement",
            })
        elif row['quantite'] <= row['seuil_alerte']:
            recommandations.append({
                'produit': row['nom'],
                'type': 'warning',
                'icone': 'bi-exclamation-triangle',
                'message': f"Stock bas ({int(row['quantite'])} unités) — réapprovisionner bientôt",
            })
        elif row['quantite'] > row['seuil_alerte'] * 5:
            recommandations.append({
                'produit': row['nom'],
                'type': 'info',
                'icone': 'bi-info-circle',
                'message': f"Stock élevé ({int(row['quantite'])} unités) — envisager une promotion",
            })

    return recommandations


def recommandations_ventes():
    df = get_ventes_data()
    recommandations = []

    if df.empty:
        recommandations.append({
            'type': 'info',
            'icone': 'bi-lightbulb',
            'message': "Aucune vente enregistrée — commencez à saisir vos ventes pour obtenir des recommandations.",
        })
        return recommandations

    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['total'] = df['total'].astype(float)

    aujourd_hui = timezone.now().date()
    semaine_passee = aujourd_hui - timedelta(days=7)
    semaine_avant = aujourd_hui - timedelta(days=14)

    ventes_semaine = df[df['date_vente'].dt.date >= semaine_passee]['total'].sum()
    ventes_avant = df[
        (df['date_vente'].dt.date >= semaine_avant) &
        (df['date_vente'].dt.date < semaine_passee)
    ]['total'].sum()

    if ventes_avant > 0:
        variation = ((ventes_semaine - ventes_avant) / ventes_avant) * 100
        if variation < -20:
            recommandations.append({
                'type': 'danger',
                'icone': 'bi-graph-down-arrow',
                'message': f"Ventes en baisse de {abs(round(variation, 1))}% cette semaine — analysez les causes.",
            })
        elif variation > 20:
            recommandations.append({
                'type': 'success',
                'icone': 'bi-graph-up-arrow',
                'message': f"Excellente semaine ! Ventes en hausse de {round(variation, 1)}%.",
            })

    if len(df) >= 3:
        recommandations.append({
            'type': 'info',
            'icone': 'bi-lightbulb',
            'message': "Pensez à fidéliser vos clients réguliers avec des offres spéciales.",
        })

    return recommandations


def prediction_ventes_semaine():
    df = get_ventes_data()
    if df.empty or len(df) < 3:
        return {
            'prediction': 0,
            'fiabilite': 'Pas assez de données',
            'message': 'Ajoutez plus de ventes pour obtenir une prédiction fiable.',
        }

    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['total'] = df['total'].astype(float)
    par_jour = df.groupby(df['date_vente'].dt.date)['total'].sum().reset_index()
    par_jour.columns = ['date', 'total']
    par_jour = par_jour.sort_values('date')

    moyenne = float(par_jour['total'].mean())
    prediction = round(moyenne * 7, 2)

    nb_jours = len(par_jour)
    if nb_jours >= 14:
        fiabilite = 'Bonne'
    elif nb_jours >= 7:
        fiabilite = 'Moyenne'
    else:
        fiabilite = 'Faible'

    return {
        'prediction': prediction,
        'fiabilite': fiabilite,
        'message': f"Basé sur {nb_jours} jours de données.",
    }