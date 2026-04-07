from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit
from .forms import ProduitForm

def produit_list(request):
    produits = Produit.objects.all()
    return render(request, 'stock/produit_list.html', {'produits': produits})

def produit_create(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('produit_list')
    else:
        form = ProduitForm()
    return render(request, 'stock/produit_form.html', {'form': form})

def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('produit_list')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'stock/produit_form.html', {'form': form})

def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('produit_list')
    return render(request, 'stock/produit_confirm_delete.html', {'produit': produit})