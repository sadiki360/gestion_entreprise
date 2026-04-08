"""
seed_data.py -- Commande Django pour peupler la base de donnees avec des donnees
realistes afin de tester le moteur IA (ai_engine).

Usage :
    python manage.py seed_data
    python manage.py seed_data --reset
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from clients.models import Client
from stock.models import Produit
from ventes.models import LigneVente, Vente


# ──────────────────────────────────────────────
# Donnees de reference
# ──────────────────────────────────────────────
CLIENTS_DATA = [
    {"nom": "Benali",    "prenom": "Youssef",  "email": "youssef.benali@email.ma",   "telephone": "0661234567"},
    {"nom": "Tahiri",    "prenom": "Fatima",   "email": "fatima.tahiri@email.ma",    "telephone": "0662345678"},
    {"nom": "Ouali",     "prenom": "Hassan",   "email": "hassan.ouali@email.ma",     "telephone": "0663456789"},
    {"nom": "Moussaoui", "prenom": "Samira",   "email": "samira.moussaoui@email.ma", "telephone": "0664567890"},
    {"nom": "Cherkaoui", "prenom": "Rachid",   "email": "rachid.cherkaoui@email.ma", "telephone": "0665678901"},
    {"nom": "Belmahi",   "prenom": "Zineb",    "email": "zineb.belmahi@email.ma",    "telephone": "0666789012"},
    {"nom": "El Fassi",  "prenom": "Mohamed",  "email": "mohamed.elfassi@email.ma",  "telephone": "0667890123"},
    {"nom": "Saidi",     "prenom": "Khadija",  "email": "khadija.saidi@email.ma",    "telephone": "0668901234"},
]

PRODUITS_DATA = [
    # (nom, prix, quantite, seuil_alerte, description)
    ("Ordinateur Portable HP",     4500.00, 15,  5,  "HP 15s, Core i5, 8GB RAM, 512GB SSD"),
    ("Imprimante Laser Brother",   1200.00,  2,  5,  "Imprimante laser monochrome, 30 ppm"),   # stock bas  -> warning IA
    ("Clavier Mecanique Logitech",  350.00, 80, 10,  "Clavier RGB, switches Cherry MX"),        # stock eleve -> info IA
    ("Souris Ergonomique",          180.00,  0, 10,  "Logitech MX Master 3, sans fil"),         # rupture   -> danger IA
    ("Ecran 24 pouces Dell",       1800.00, 12,  5,  "Full HD IPS, 75Hz, HDMI/DP"),
    ("Disque SSD 1To Samsung",      650.00, 25, 10,  "Samsung 870 EVO, SATA III"),
    ("Casque Audio Sony",           900.00,  3,  5,  "Sony WH-1000XM5, Noise Cancelling"),      # stock bas  -> warning IA
    ("Webcam Logitech C920",        450.00, 60, 10,  "Full HD 1080p, avec micro integre"),       # stock eleve -> info IA
    ("Hub USB-C 7 en 1",            220.00,  8, 10,  "HDMI, USB3.0, SD card, PD 100W"),
    ("Tapis de Souris XXL",          90.00, 35, 10,  "900x400mm, surface gaming"),
]


class Command(BaseCommand):
    help = "Peuple la base de donnees avec des donnees de demonstration pour le moteur IA."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime toutes les donnees existantes avant de creer les nouvelles.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("[RESET] Suppression des donnees existantes..."))
            LigneVente.objects.all().delete()
            Vente.objects.all().delete()
            Client.objects.all().delete()
            Produit.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("[OK] Donnees supprimees."))

        # -- 1. Clients ------------------------------------------
        self.stdout.write("[INFO] Creation des clients...")
        clients = []
        for data in CLIENTS_DATA:
            client, created = Client.objects.get_or_create(
                email=data["email"],
                defaults={
                    "nom":       data["nom"],
                    "prenom":    data["prenom"],
                    "telephone": data["telephone"],
                },
            )
            clients.append(client)
        self.stdout.write(self.style.SUCCESS(f"   -> {len(clients)} clients crees/recuperes."))

        # -- 2. Produits ------------------------------------------
        self.stdout.write("[INFO] Creation des produits...")
        produits = []
        for nom, prix, quantite, seuil, desc in PRODUITS_DATA:
            produit, created = Produit.objects.get_or_create(
                nom=nom,
                defaults={
                    "prix":         Decimal(str(prix)),
                    "quantite":     quantite,
                    "seuil_alerte": seuil,
                    "description":  desc,
                },
            )
            produits.append(produit)
        self.stdout.write(self.style.SUCCESS(f"   -> {len(produits)} produits crees/recuperes."))

        # -- 3. Ventes (30 derniers jours) ------------------------
        # Les 7 derniers jours ont un volume +30% pour declencher
        # la recommendation "Excellente semaine !" de l'IA.
        self.stdout.write("[INFO] Generation des ventes sur 30 jours...")
        today = timezone.now()
        ventes_creees = 0

        produits_en_stock = [p for p in produits if p.quantite > 0]

        for day_offset in range(29, -1, -1):
            day = today - timedelta(days=day_offset)

            # Volume plus eleve sur la derniere semaine
            nb_ventes_du_jour = random.randint(3, 6) if day_offset <= 7 else random.randint(1, 3)

            for _ in range(nb_ventes_du_jour):
                client = random.choice(clients)
                vente = Vente.objects.create(client=client, total=Decimal("0"))

                # Forcer la date (auto_now_add=True ne peut pas etre outrepasse directement)
                Vente.objects.filter(pk=vente.pk).update(date_vente=day)
                vente.refresh_from_db()

                # Lignes de vente : 1 a 3 produits par vente
                nb_lignes = random.randint(1, 3)
                nb_choix = min(nb_lignes, len(produits_en_stock))
                produits_choisis = random.sample(produits_en_stock, nb_choix)

                total_vente = Decimal("0")
                for produit in produits_choisis:
                    quantite_vendue = random.randint(1, 3)
                    variation = Decimal(str(round(random.uniform(0.95, 1.05), 4)))
                    prix = (produit.prix * variation).quantize(Decimal("0.01"))

                    LigneVente.objects.create(
                        vente=vente,
                        produit=produit,
                        quantite=quantite_vendue,
                        prix_unitaire=prix,
                    )
                    total_vente += prix * quantite_vendue

                Vente.objects.filter(pk=vente.pk).update(total=total_vente)
                ventes_creees += 1

        self.stdout.write(self.style.SUCCESS(f"   -> {ventes_creees} ventes creees sur 30 jours."))

        # -- Resume -----------------------------------------------
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 58))
        self.stdout.write(self.style.SUCCESS("[IA] DONNEES PRETES - le moteur IA peut maintenant analyser :"))
        self.stdout.write(self.style.SUCCESS("=" * 58))
        self.stdout.write(f"  Clients  : {Client.objects.count()}")
        self.stdout.write(f"  Produits : {Produit.objects.count()}")
        self.stdout.write(f"  Ventes   : {Vente.objects.count()}")
        self.stdout.write(f"  Lignes   : {LigneVente.objects.count()}")
        self.stdout.write("")
        self.stdout.write("  Conditions declenchees dans l'IA :")
        self.stdout.write("   [DANGER]  Rupture de stock  -> 'Souris Ergonomique' (qte 0)")
        self.stdout.write("   [WARNING] Stock bas         -> 'Imprimante Laser'   (qte 2)")
        self.stdout.write("   [INFO]    Stock eleve       -> 'Clavier Mecanique'  (qte 80)")
        self.stdout.write("   [OK]      Semaine en hausse -> ventes +30% cette semaine")
        self.stdout.write("   [OK]      Prediction fiable -> 30 jours de donnees")
        self.stdout.write("")
        self.stdout.write("  Lancez le serveur et allez sur http://127.0.0.1:8000/ai/")
