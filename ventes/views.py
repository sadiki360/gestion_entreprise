from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .pdf import export_ventes_pdf, export_facture_pdf
from .models import Vente, LigneVente
from .forms import VenteForm, LigneVenteForm

@login_required
def vente_list(request):
    ventes = Vente.objects.all()
    return render(request, 'ventes/vente_list.html', {'ventes': ventes})

@login_required
def vente_create(request):
    if request.method == 'POST':
        form = VenteForm(request.POST)
        if form.is_valid():
            vente = form.save()
            return redirect('vente_detail', pk=vente.pk)
    else:
        form = VenteForm()
    return render(request, 'ventes/vente_form.html', {'form': form})

@login_required
def vente_detail(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    lignes = vente.lignes.all()
    return render(request, 'ventes/vente_detail.html', {'vente': vente, 'lignes': lignes})

@login_required
def vente_delete(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    if request.method == 'POST':
        vente.delete()
        return redirect('vente_list')
    return render(request, 'ventes/vente_confirm_delete.html', {'vente': vente})

@login_required
def ventes_pdf(request):
    ventes = Vente.objects.all().order_by('-date_vente')
    return export_ventes_pdf(ventes)

@login_required
def facture_pdf(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    return export_facture_pdf(vente)