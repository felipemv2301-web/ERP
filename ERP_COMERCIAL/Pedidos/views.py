from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PedidoForm
from Productos.forms import ProductoFormSet
from Pedidos.models import Pedido
import datetime
from django.shortcuts import render
from django.forms import formset_factory
from Productos.models import Producto
from Productos.forms import ProductoForm
from datetime import datetime
from Pedidos.services.pdf_parser import procesar_archivo_pdf, procesar_archivo_ocr
from rest_framework.decorators import api_view
from rest_framework.response import Response


'''
-------------------------------------------------
Funciones CRUD para Pedidos y Productos
-------------------------------------------------
'''

def ingresar_pedido(request):
    resultado = None
    error = None

    # Inicializar formularios
    pedido_form = PedidoForm()
    ProductoFormSet = formset_factory(ProductoForm, extra=1, can_delete=True)
    formset = ProductoFormSet(prefix='productos')

    if request.method == "POST" and request.POST.get("accion") == "guardar":
        pedido_form = PedidoForm(request.POST)
        formset = ProductoFormSet(request.POST, prefix='productos')

        if pedido_form.is_valid() and formset.is_valid():
            pedido = pedido_form.save()
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    Producto.objects.create(
                        pedido=pedido,
                        nombre_producto=form.cleaned_data.get('nombre_producto', ''),
                        tipo_producto=form.cleaned_data.get('tipo_producto', ''),
                        tamano_producto=form.cleaned_data.get('tamano_producto', ''),
                        observacion_producto=form.cleaned_data.get('observacion_producto', ''),
                        cantidad_producto=form.cleaned_data.get('cantidad_producto', 0),
                        precio_unitario_producto=form.cleaned_data.get('precio_unitario_producto', Decimal('0.0'))
                    )
            pedido.calcular_totales()
            return redirect('pedidos:listar_pedidos')
        else:
            error = "Formulario con errores. Revisa los campos."

    return render(request, "pedidos/ingresar_pedido.html", {
        "pedido_form": pedido_form,
        "formset": formset,
        "resultado": resultado,
        "error": error
    })


def listar_pedidos(request):
    # Traer todos los pedidos con sus productos relacionados
    pedidos = Pedido.objects.prefetch_related('producto_set').all().order_by('-fecha_pedido')
    context = {
        'pedidos': pedidos
    }
    return render(request, 'Pedidos/listar_pedidos.html', context)

def editar_pedido(request, pedido_id):
    # Obtener el pedido de la base de datos
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Inicializar variables de mensajes
    resultado = None
    error = None

    # Inicializar formulario y formset
    pedido_form = PedidoForm(instance=pedido)
    ProductoFormSet = formset_factory(ProductoForm, extra=0, can_delete=True)

    # Crear formset con los productos existentes
    productos_qs = pedido.producto_set.all()
    initial_productos = [{
        "nombre_producto": p.nombre_producto,
        "tipo_producto": p.tipo_producto,
        "tamano_producto": p.tamano_producto,
        "observacion_producto": p.observacion_producto,
        "cantidad_producto": p.cantidad_producto,
        "precio_unitario_producto": p.precio_unitario_producto
    } for p in productos_qs]
    formset = ProductoFormSet(initial=initial_productos, prefix='productos')

    if request.method == "POST":
        pedido_form = PedidoForm(request.POST, instance=pedido)
        formset = ProductoFormSet(request.POST, prefix='productos')

        if pedido_form.is_valid() and formset.is_valid():
            # Guardar cambios del pedido
            pedido = pedido_form.save(commit=False)
            pedido.save()

            # Eliminar productos marcados para borrar
            for form, producto in zip(formset.forms, productos_qs):
                if form.cleaned_data.get('DELETE', False):
                    producto.delete()

            # Actualizar o crear productos
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    # Buscar si el producto existe (por posición en el queryset)
                    nombre = form.cleaned_data.get('nombre_producto', '')
                    cantidad = form.cleaned_data.get('cantidad_producto', 0)
                    precio = form.cleaned_data.get('precio_unitario_producto', Decimal('0.0'))
                    
                    # Crear nuevo producto si no existe
                    Producto.objects.update_or_create(
                        pedido=pedido,
                        nombre_producto=nombre,
                        defaults={
                            "tipo_producto": form.cleaned_data.get('tipo_producto', ''),
                            "tamano_producto": form.cleaned_data.get('tamano_producto', ''),
                            "observacion_producto": form.cleaned_data.get('observacion_producto', ''),
                            "cantidad_producto": cantidad,
                            "precio_unitario_producto": precio
                        }
                    )

            # Recalcular totales automáticamente
            pedido.calcular_totales()

            return redirect('pedidos:listar_pedidos')
        else:
            error = "Formulario con errores. Revisa los campos."

    return render(request, "pedidos/editar_pedido.html", {
        "pedido_form": pedido_form,
        "formset": formset,
        "resultado": resultado,
        "error": error
    })

'''
-------------------------------------------------
Subir y procesar archivo PDF o imagen usando la
API REST, OCR con pytesseract y pdfplumber
-------------------------------------------------
'''

@api_view(['POST'])
def procesar_documento_api(request):
    archivo = request.FILES.get("archivo")
    if not archivo:
        return Response({"error": "No se envió ningún archivo"}, status=400)

    try:
        if str(archivo.name).lower().endswith((".jpg", ".jpeg", ".png")):
            pedido_data, productos_data = procesar_archivo_ocr(archivo)
        else:
            pedido_data, productos_data = procesar_archivo_pdf(archivo)

        # Formatear fechas y totales
        pedido_data["fecha_pedido"] = pedido_data.get("fecha_pedido", "")
        pedido_data["total_neto_pedido"] = str(pedido_data.get("total_neto_pedido", "0.0"))
        pedido_data["total_pedido"] = str(pedido_data.get("total_pedido", "0.0"))

        return Response({"pedido": pedido_data, "productos": productos_data})
    except Exception as e:
        return Response({"error": str(e)}, status=500)