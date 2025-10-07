from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from .forms import ClienteForm, DireccionClienteForm, ContactoClienteForm
from .models import Cliente, DireccionCliente, ContactoCliente
from django.contrib import messages


'''
-------------------------------------------------
Funciones CRUD de clientes
-------------------------------------------------
'''

def ingresar_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Cliente ingresado correctamente.")
            return redirect("clientes:listar_clientes")
        else:
            messages.error(request, "Ocurrió un error al guardar el cliente. Revisa los datos ingresados.")
    else:
        form = ClienteForm()

    return render(request, "clientes/ingresar_cliente.html", {"form": form})


def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, "clientes/listar_clientes.html", {"clientes": clientes})

def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    direcciones = DireccionCliente.objects.filter(cliente=cliente)
    contactos = ContactoCliente.objects.filter(cliente=cliente)
    return render(request, "Clientes/modals/modal_detalle_cliente.html", {
        "cliente": cliente,
        "direcciones": direcciones,
        "contactos": contactos
    })

'''
-------------------------------------------------
Funciones CRUD de direcciones
-------------------------------------------------
'''

def ingresar_direccion(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    direcciones = DireccionCliente.objects.filter(cliente=cliente)

    if request.method == "POST":
        form = DireccionClienteForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = cliente
            direccion.save()
            messages.success(request, f"Dirección: {direccion.calle} {direccion.numero} agregada correctamente.")
            # Se mantiene en la misma vista para seguir ingresando direcciones
            return redirect('clientes:ingresar_direccion', cliente_id=cliente.id)
        else:
            messages.error(request, "Ocurrió un error al agregar la dirección. Revisa los datos e inténtalo nuevamente.")
    else:
        form = DireccionClienteForm()

    return render(
        request,
        "Clientes/ingresar_direccion.html",
        {"form": form, "cliente": cliente, "direcciones": direcciones}
    )

def eliminar_direccion(request, direccion_id):
    direccion = get_object_or_404(DireccionCliente, id=direccion_id)
    cliente_id = direccion.cliente.id
    if request.method == "POST":
        direccion.delete()
    return redirect('clientes:ingresar_direccion', cliente_id=cliente_id)

'''
-------------------------------------------------
Funciones CRUD de contactos
-------------------------------------------------
'''

def ingresar_contacto(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    contactos = ContactoCliente.objects.filter(cliente=cliente)

    if request.method == "POST":
        form = ContactoClienteForm(request.POST)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.cliente = cliente
            contacto.save()
            return redirect("clientes:ingresar_contacto", cliente_id=cliente.id)
    else:
        form = ContactoClienteForm()

    return render(request, "clientes/ingresar_contacto.html", {
        "form": form,
        "cliente": cliente,
        "contactos": contactos
    })

def eliminar_contacto(request, contacto_id):
    contacto = get_object_or_404(ContactoCliente, id=contacto_id)
    
    if request.method == "POST":
        contacto.delete()
        # Redirigimos a la página de detalle del cliente
        return redirect('clientes:eliminar_cliente', cliente_id=contacto.cliente.id)

    # Opcional: si alguien intenta acceder por GET, lo redirigimos
    return redirect('clientes:eliminar_cliente', cliente_id=contacto.cliente.id)