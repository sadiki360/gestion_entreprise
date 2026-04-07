from django import forms
from .models import Vente, LigneVente

class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['client']

class LigneVenteForm(forms.ModelForm):
    class Meta:
        model = LigneVente
        fields = ['produit', 'quantite', 'prix_unitaire']