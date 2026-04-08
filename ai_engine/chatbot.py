from ventes.models import Vente
from clients.models import Client
from stock.models import Produit
from django.db.models import Sum, Count
from datetime import timedelta
from django.utils import timezone


def process_question(question):
    q = question.lower().strip()

    # ===== VENTES =====
    if any(w in q for w in ['vente', 'ventes', 'vendu', 'chiffre', 'ca', 'total']):
        total = Vente.objects.aggregate(Sum('total'))['total__sum'] or 0
        nb = Vente.objects.count()
        return f"Vous avez {nb} vente(s) pour un chiffre d'affaires total de {round(float(total), 2)} DH."

    # ===== CLIENTS =====
    elif any(w in q for w in ['client', 'clients', 'combien de client']):
        nb = Client.objects.count()
        derniers = Client.objects.order_by('-date_creation')[:3]
        noms = ', '.join([f"{c.nom} {c.prenom}" for c in derniers])
        return f"Vous avez {nb} client(s). Derniers ajoutés : {noms}."

    # ===== STOCK =====
    elif any(w in q for w in ['stock', 'produit', 'produits', 'quantite', 'quantité']):
        nb = Produit.objects.count()
        bas = Produit.objects.filter(quantite__lte=10)
        if bas.exists():
            noms = ', '.join([p.nom for p in bas])
            return f"Vous avez {nb} produit(s). Stock bas pour : {noms}."
        return f"Vous avez {nb} produit(s). Tout le stock est en bon état."

    # ===== MEILLEUR PRODUIT =====
    elif any(w in q for w in ['meilleur', 'plus vendu', 'populaire', 'top']):
        from ventes.models import LigneVente
        top = LigneVente.objects.values('produit__nom').annotate(
            total=Sum('quantite')
        ).order_by('-total').first()
        if top:
            return f"Le produit le plus vendu est '{top['produit__nom']}' avec {top['total']} unité(s) vendues."
        return "Pas encore assez de données pour déterminer le meilleur produit."

    # ===== AUJOURD'HUI =====
    elif any(w in q for w in ["aujourd'hui", "aujourd hui", "journee", "journée", "ajourd"]):
        today = timezone.now().date()
        ventes = Vente.objects.filter(date_vente__date=today)
        total = ventes.aggregate(Sum('total'))['total__sum'] or 0
        return f"Aujourd'hui : {ventes.count()} vente(s) pour {round(float(total), 2)} DH."

    # ===== CETTE SEMAINE =====
    elif any(w in q for w in ['semaine', 'cette semaine', 'week']):
        debut = timezone.now().date() - timedelta(days=7)
        ventes = Vente.objects.filter(date_vente__date__gte=debut)
        total = ventes.aggregate(Sum('total'))['total__sum'] or 0
        return f"Cette semaine : {ventes.count()} vente(s) pour {round(float(total), 2)} DH."

    # ===== ALERTE STOCK =====
    elif any(w in q for w in ['alerte', 'rupture', 'manque', 'bas']):
        bas = Produit.objects.filter(quantite__lte=10)
        if bas.exists():
            details = ', '.join([f"{p.nom} ({p.quantite} unités)" for p in bas])
            return f"Produits en alerte : {details}."
        return "Aucun produit en rupture ou stock bas. Tout va bien !"

    # ===== BONJOUR =====
    elif any(w in q for w in ['bonjour', 'salut', 'hello', 'hi', 'salam', 'السلام']):
        nb_clients = Client.objects.count()
        nb_ventes = Vente.objects.count()
        nb_produits = Produit.objects.count()
        return f"Bonjour ! Voici un résumé rapide : {nb_clients} client(s), {nb_produits} produit(s), {nb_ventes} vente(s). Comment puis-je vous aider ?"

    # ===== AIDE =====
    elif any(w in q for w in ['aide', 'help', 'quoi', 'question', '?']):
        return ("Je peux répondre à des questions comme : "
                "'Combien de ventes ?', 'Quel est le stock ?', "
                "'Meilleur produit ?', 'Ventes cette semaine ?', "
                "'Y a-t-il des alertes stock ?'")

    # ===== DEFAULT =====
    else:
        return ("Je n'ai pas compris votre question. Essayez : "
                "'Combien de clients ?', 'État du stock', "
                "'Ventes aujourd\\'hui', 'Meilleur produit'.")