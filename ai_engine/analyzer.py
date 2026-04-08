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


# ═══════════════════════════════════════════════════════════════════════════
#  IA PROMOTIONS CLIENTS  — Algorithme RFM (Recence · Frequence · Montant)
# ═══════════════════════════════════════════════════════════════════════════

def analyser_clients_promotions():
    """
    Analyse chaque client selon 3 critères :
      R – Récence    : combien de jours depuis sa dernière vente
      F – Fréquence  : nombre total de ventes
      M – Montant    : chiffre d'affaires total généré

    Chaque critère est noté de 1 à 5.
    Score global = (R + F + M) / 3   → normalisé sur 100.

    Segments et promotions générés automatiquement :
      VIP         (score >= 80) : Offre exclusive VIP
      Loyal       (score >= 60) : Remise fidélité
      A reactiver (score >= 40) : Bon de reduction "on vous manque"
      Nouveau     (score >= 20) : Bienvenue — premiere remise
      Inactif     (score <  20) : Campagne de reconquete
    """
    from clients.models import Client
    from ventes.models import Vente

    today = timezone.now()

    # Récupérer toutes les ventes avec client et date
    ventes_qs = Vente.objects.all().values('client_id', 'date_vente', 'total')
    df = pd.DataFrame(list(ventes_qs))

    # Récupérer tous les clients
    clients_qs = Client.objects.all().values('id', 'nom', 'prenom', 'email', 'telephone')
    clients_df = pd.DataFrame(list(clients_qs))

    if clients_df.empty:
        return []

    if df.empty:
        # Aucune vente : tous les clients sont "Nouveaux"
        resultats = []
        for _, c in clients_df.iterrows():
            resultats.append({
                'id':         int(c['id']),
                'nom':        f"{c['prenom']} {c['nom']}",
                'email':      c['email'],
                'telephone':  c['telephone'],
                'segment':    'Nouveau',
                'score':      0,
                'recence':    '-',
                'frequence':  0,
                'montant':    0,
                'promotion':  'Offre de bienvenue — 10% sur votre premiere commande',
                'badge':      'secondary',
                'icone':      'bi-person-plus',
                'priorite':   3,
            })
        return resultats

    df['date_vente'] = pd.to_datetime(df['date_vente'], utc=True)
    df['total'] = df['total'].astype(float)

    # ── Calcul RFM par client ──────────────────────────────────────────────
    rfm = df.groupby('client_id').agg(
        derniere_vente=('date_vente', 'max'),
        frequence=('client_id', 'count'),
        montant=('total', 'sum'),
    ).reset_index()

    now_utc = pd.Timestamp(today).tz_convert('UTC')
    rfm['recence_jours'] = (now_utc - rfm['derniere_vente']).dt.days

    # ── Scoring 1-5 par quantile (ou valeur fixe si peu de données) ────────
    def score_quantile(series, ascending=True):
        """Attribue un score 1-5 par quintile."""
        if series.nunique() < 2:
            return pd.Series([3] * len(series), index=series.index)
        labels = [1, 2, 3, 4, 5] if not ascending else [5, 4, 3, 2, 1]
        try:
            return pd.qcut(series, q=5, labels=labels, duplicates='drop').astype(float)
        except Exception:
            return pd.Series([3] * len(series), index=series.index)

    # Récence : plus récent = meilleur → ascending=False (jours faibles = bon)
    rfm['score_r'] = score_quantile(rfm['recence_jours'], ascending=False)
    rfm['score_f'] = score_quantile(rfm['frequence'],     ascending=True)
    rfm['score_m'] = score_quantile(rfm['montant'],       ascending=True)

    rfm['score_global'] = ((rfm['score_r'] + rfm['score_f'] + rfm['score_m']) / 3 * 20).round(1)

    # ── Définition des segments ────────────────────────────────────────────
    def segment_client(row):
        s = row['score_global']
        r = row['recence_jours']
        if s >= 80:
            return ('VIP',         'success',  'bi-star-fill',           1,
                    "Offre VIP exclusive — -20% + livraison gratuite sur sa prochaine commande")
        elif s >= 60:
            return ('Loyal',       'primary',  'bi-heart-fill',          2,
                    "Remise fidelite -15% valable ce mois-ci")
        elif s >= 40:
            return ('A reactiver', 'warning',  'bi-arrow-clockwise',     3,
                    "Bon de reduction -10% 'On vous manque !' a envoyer par email")
        elif r <= 14:
            return ('Nouveau',     'info',     'bi-person-plus-fill',    4,
                    "Offre de bienvenue — -10% sur la prochaine commande")
        else:
            return ('Inactif',     'danger',   'bi-exclamation-triangle-fill', 5,
                    "Campagne de reconquete — offre speciale -25% pour relancer la relation")

    rfm[['segment', 'badge', 'icone', 'priorite', 'promotion']] = rfm.apply(
        lambda r: pd.Series(segment_client(r)), axis=1
    )

    # ── Jointure avec les infos clients ────────────────────────────────────
    merged = clients_df.merge(rfm, left_on='id', right_on='client_id', how='left')

    resultats = []
    for _, row in merged.iterrows():
        has_ventes = not pd.isna(row.get('score_global'))

        if has_ventes:
            recence_jours = int(row['recence_jours'])
            recence_label = f"il y a {recence_jours} jour{'s' if recence_jours > 1 else ''}"
            score         = float(row['score_global'])
            frequence     = int(row['frequence'])
            montant       = round(float(row['montant']), 2)
            segment       = row['segment']
            badge         = row['badge']
            icone         = row['icone']
            priorite      = int(row['priorite'])
            promotion     = row['promotion']
        else:
            recence_label = 'Jamais achete'
            score         = 0.0
            frequence     = 0
            montant       = 0.0
            segment       = 'Nouveau'
            badge         = 'secondary'
            icone         = 'bi-person-plus'
            priorite      = 6
            promotion     = "Offre de bienvenue — -10% sur la premiere commande"

        resultats.append({
            'id':        int(row['id']),
            'nom':       f"{row['prenom']} {row['nom']}",
            'email':     row['email'],
            'telephone': row['telephone'] if row['telephone'] else '-',
            'segment':   segment,
            'score':     score,
            'recence':   recence_label,
            'frequence': frequence,
            'montant':   montant,
            'promotion': promotion,
            'badge':     badge,
            'icone':     icone,
            'priorite':  priorite,
        })

    # Trier par priorite de promotion (VIP en premier)
    resultats.sort(key=lambda x: (x['priorite'], -x['score']))
    return resultats


def stats_segments():
    """Retourne le compte de clients par segment pour le graphique."""
    clients = analyser_clients_promotions()
    counts = {}
    for c in clients:
        seg = c['segment']
        counts[seg] = counts.get(seg, 0) + 1

    ordre = ['VIP', 'Loyal', 'A reactiver', 'Nouveau', 'Inactif']
    labels  = [s for s in ordre if s in counts]
    values  = [counts[s] for s in labels]
    couleurs = {
        'VIP':         '#22c55e',
        'Loyal':       '#3b82f6',
        'A reactiver': '#f59e0b',
        'Nouveau':     '#06b6d4',
        'Inactif':     '#ef4444',
    }
    colors = [couleurs.get(s, '#6b7280') for s in labels]
    return {'labels': labels, 'values': values, 'colors': colors}