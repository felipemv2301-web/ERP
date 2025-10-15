from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from Despachos.models import GuiaDespacho, DetalleDespacho
from Pedidos.models import Pedido
from Despachos.forms import GuiaDespachoForm, DetalleDespachoFormSet
from Productos.models import Producto
from django.db.models import Sum
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import GuiaDespacho, DetalleDespacho
from .forms import GuiaDespachoForm, DetalleDespachoFormSet
from django.http import JsonResponse

def ingresar_guia_despacho(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    cliente = pedido.cliente
    productos = pedido.producto_set.all()

    # Calcular despachos previos
    despachado_db = {
        p.id: DetalleDespacho.objects.filter(
            producto=p,
            guia_despacho__pedido=pedido
        ).aggregate(total=Sum('cantidad_despachada'))['total'] or 0
        for p in productos
    }

    # Preparar info para el template
    productos_info = []
    for p in productos:
        total = p.cantidad_producto or 0
        despachado = despachado_db.get(p.id, 0)
        restante = max(total - despachado, 0)
        productos_info.append({
            "id": p.id,
            "nombre": p.nombre_producto,
            "tipo": getattr(p, "tipo_producto", ""),
            "tamano": getattr(p, "tamano_producto", ""),
            "precio": getattr(p, "precio_unitario_producto", 0),
            "cantidad_total": total,
            "despachado": despachado,
            "restante": restante,
        })

    if request.method == 'POST':
        form = GuiaDespachoForm(request.POST, cliente=cliente)
        formset = DetalleDespachoFormSet(
            request.POST,
            instance=GuiaDespacho(pedido=pedido),
            form_kwargs={'pedido': pedido}
        )

        if form.is_valid() and formset.is_valid():
            guia = form.save(commit=False)
            guia.pedido = pedido
            guia.save()
            formset.instance = guia

            # Validar cantidades despachadas
            despachado_formset = {p['id']: 0 for p in productos_info}
            errores = []
            error_en_cantidades = False

            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                    producto = f.cleaned_data.get('producto')
                    cantidad = f.cleaned_data.get('cantidad_despachada', 0)
                    if not producto:
                        errores.append("Debe seleccionar un producto en todos los detalles.")
                        error_en_cantidades = True
                        continue

                    restante_real = next(p['restante'] for p in productos_info if p['id'] == producto.id) - despachado_formset[producto.id]

                    if cantidad > restante_real:
                        errores.append(
                            f"No se puede despachar {cantidad} de '{producto.nombre_producto}'. "
                            f"Cantidad restante disponible: {restante_real}."
                        )
                        error_en_cantidades = True
                    else:
                        despachado_formset[producto.id] += cantidad

            if error_en_cantidades:
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "errors": errores})
                for e in errores:
                    messages.error(request, e)
            else:
                formset.save()
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"success": True, "message": "Guía de despacho ingresada correctamente."})
                messages.success(request, "Guía de despacho ingresada correctamente.")
                return redirect('despachos:listar_guia_despacho', pedido_id=pedido.id)
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": ["Por favor corrija los errores en el formulario."]})
            messages.error(request, "Por favor corrija los errores en el formulario.")

    else:
        form = GuiaDespachoForm(cliente=cliente)
        formset = DetalleDespachoFormSet(
            instance=GuiaDespacho(pedido=pedido),
            form_kwargs={'pedido': pedido}
        )

    return render(request, 'despachos/ingresar_guia_despacho.html', {
        'form': form,
        'formset': formset,
        'pedido': pedido,
        'cliente': cliente,
        'productos_info': productos_info,
    })


# Endpoint AJAX para obtener restante dinámicamente
def ajax_restante_producto(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    productos = pedido.producto_set.all()

    data = []
    for p in productos:
        despachado = DetalleDespacho.objects.filter(
            producto=p, guia_despacho__pedido=pedido
        ).aggregate(total=Sum('cantidad_despachada'))['total'] or 0
        restante = max((p.cantidad_producto or 0) - despachado, 0)
        data.append({'id': p.id, 'restante': restante})

    return JsonResponse({'productos': data})


def listar_guias_despacho(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    # Obtiene todas las guías de despacho asociadas a este pedido
    guias = GuiaDespacho.objects.filter(pedido=pedido).order_by('-fecha_despacho')
    
    return render(request, 'despachos/listar_guia_despacho.html', {
        'pedido': pedido,
        'guias': guias,
    })

