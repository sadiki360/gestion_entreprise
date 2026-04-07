from django.db import models
from clients.models import Client
from stock.models import Produit

class Vente(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_vente = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Vente #{self.id} - {self.client}"

class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produit} x{self.quantite}"