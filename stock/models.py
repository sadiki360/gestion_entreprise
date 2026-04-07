from django.db import models

class Produit(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=10)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    @property
    def en_rupture(self):
        return self.quantite <= self.seuil_alerte