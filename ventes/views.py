from django.shortcuts import render, get_object_or_404, redirect
from .models import Vente, LigneVente
from .forms import VenteForm, LigneVenteForm

def vente_list(request):
    ventes = Vente.objects.all()
    return render(request, 'ventes/vente_list.html', {'ventes': ventes})

def vente_create(request):
    if request.method == 'POST':
        form = VenteForm(request.POST)
        if form.is_valid():
            vente = form.save()
            return redirect('vente_detail', pk=vente.pk)
    else:
        form = VenteForm()
    return render(request, 'ventes/vente_form.html', {'form': form})

def vente_detail(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    lignes = vente.lignes.all()
    return render(request, 'ventes/vente_detail.html', {'vente': vente, 'lignes': lignes})

def vente_delete(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    if request.method == 'POST':
        vente.delete()
        return redirect('vente_list')
    return render(request, 'ventes/vente_confirm_delete.html', {'vente': vente})