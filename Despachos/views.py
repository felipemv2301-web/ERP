from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from Pedidos.models import Pedido, Cliente
from Despachos.forms import GuiaDespachoForm, DetalleDespachoFormSet
from Despachos.models import GuiaDespacho

def ingresar_guia_despacho(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    cliente = pedido.cliente

    if request.method == 'POST':
        form = GuiaDespachoForm(request.POST, cliente=cliente)
        formset = DetalleDespachoFormSet(request.POST, form_kwargs={'pedido': pedido})

        if form.is_valid() and formset.is_valid():
            guia = form.save(commit=False)
            guia.pedido = pedido  # <--- aquí asignamos el pedido
            guia.save()
            formset.instance = guia
            formset.save()
            return redirect('despachos:listar_guia_despacho', pedido_id=pedido.id)
    else:
        form = GuiaDespachoForm(cliente=cliente)
        formset = DetalleDespachoFormSet(form_kwargs={'pedido': pedido})

    return render(request, 'despachos/ingresar_guia_despacho.html', {
        'form': form,
        'formset': formset,
        'pedido': pedido,
        'cliente': cliente,
    })

def listar_guias_despacho(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Obtiene todas las guías de despacho asociadas a este pedido
    guias = GuiaDespacho.objects.filter(pedido=pedido).order_by('-fecha_despacho')
    
    return render(request, 'despachos/listar_guia_despacho.html', {
        'pedido': pedido,
        'guias': guias,
    })

