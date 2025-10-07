from django.shortcuts import render
from Abonos.forms import AbonoForm
from Facturas.forms import FacturaForm
from Abonos.models import Abono
from Facturas.models import Factura
from Pedidos.models import Pedido
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Sum
from django.core.exceptions import ValidationError
from decimal import Decimal

def ingresar_factura(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == "POST":
        factura_form = FacturaForm(request.POST)
        if factura_form.is_valid():
            factura = factura_form.save(commit=False)
            # Validación: total no puede superar total del pedido
            if factura.total_factura > pedido.total_pedido:
                factura_form.add_error('total_factura', 'El total de la factura no puede superar el total del pedido.')
            else:
                factura.pedido = pedido
                factura.save()
                #Redirige a detalle_factura, donde puedes ingresar y editar los abonos de la factura
                return redirect('facturas:detalle_factura', factura.id)
    else:
        factura_form = FacturaForm()

    return render(request, "facturas/ingresar_factura.html", {
        "factura_form": factura_form,
        "pedido": pedido
    })

def listar_facturas_ajax(request):
    """
    Vista que recibe el ID del pedido y renderiza el contenido HTML de las facturas
    para ser cargado en el modal a través de AJAX.
    """
    #Obtiene el ID del pedido enviado desde el script de AJAX
    pedido_id = request.GET.get('pedido_id')
    
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    #Se renderiza un modal para el ingreso del abono
    return render(request, 'pedidos/modals/modal_facturas.html', {'pedido': pedido})



#Permite ingresar abonos luego de ingresar la factura.
def detalle_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    abonos = factura.abonos.all()
    
    if request.method == "POST":
        form = AbonoForm(request.POST)
        if form.is_valid():
            abono = form.save(commit=False)
            abono.factura = factura

            # Validación: no superar saldo pendiente
            total_pagado = sum(a.total_abono for a in factura.abonos.all())
            saldo_restante = factura.total_factura - total_pagado
            if abono.total_abono > saldo_restante:
                form.add_error('total_abono', f'El abono no puede superar el saldo pendiente de {saldo_restante:.2f}.')
            else:
                abono.save()
                #rRedirect evita repost, lo que impide que al refrescar se añada otro abono
                return redirect('facturas:detalle_factura', factura_id=factura.id)
    else:
        form = AbonoForm()

    return render(request, "facturas/detalle_factura.html", {
        "factura": factura,
        "abonos": abonos,
        "form": form,
    })

def editar_abono(request, abono_id):
    abono = get_object_or_404(Abono, id=abono_id)
    factura = abono.factura 
    total_otros = factura.abonos.exclude(pk=abono.pk).aggregate(Sum('total_abono'))['total_abono__sum'] or Decimal('0.00')

    saldo_disponible_para_abono = factura.total_factura - total_otros

    if request.method == "POST":
        form = AbonoForm(request.POST, instance=abono)
        if form.is_valid():
            if form.cleaned_data['total_abono'] > saldo_disponible_para_abono:
                # Si excede el saldo, agregamos el error al formulario
                form.add_error('total_abono', f"El abono no puede superar el saldo pendiente (${saldo_disponible_para_abono:.2f}).")
            else:
                #Si es válido, intentamos guardar.
                try:
                    #El modelo Abono.save() valida. Si falla, va al 'except'
                    form.save() 
                    messages.success(request, "Abono actualizado correctamente.")
                    return redirect('facturas:detalle_factura', factura_id=factura.id)
                
                except ValidationError as e:
                    #Esto atrapa la excepción si la validación del modelo se dispara.
                    form.add_error('total_abono', e.message)
                    
                except Exception as e:
                    # Captura cualquier otro error de base de datos
                    form.add_error(None, f"Ocurrió un error inesperado al guardar: {e}")
                
    else:
        # Petición GET: Inicializa el formulario con la instancia
        form = AbonoForm(instance=abono)

    # 3. Renderizar el fragmento HTML del modal para la carga AJAX.
    return render(request, "facturas/modals/editar_abono_modal.html", {
        "form": form,
        "abono": abono,
        "factura": factura, 
        "saldo_disponible_para_abono": saldo_disponible_para_abono,
    })

def eliminar_abono(request, abono_id):
    abono = get_object_or_404(Abono, id=abono_id)
    factura = abono.factura
    abono.delete()
    factura.actualizar_estado()  # Actualiza el estado de la factura tras eliminar
    messages.success(request, "Abono eliminado correctamente.")
    return redirect('facturas:detalle_factura', factura_id=factura.id)

def listar_facturas_ajax(request):
    """
    Vista que recibe el ID del pedido y renderiza el contenido HTML de las facturas
    para ser cargado en el modal a través de AJAX.
    """
    #Obtiene el ID del pedido
    pedido_id = request.GET.get('pedido_id')
    
    #Busca el pedido
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    #Renderiza el modal con la información necesaria
    return render(request, 'pedidos/modals/modal_facturas.html', {'pedido': pedido})