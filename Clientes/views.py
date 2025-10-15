from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from .forms import ClienteForm, DireccionClienteForm, ContactoClienteForm, DireccionClienteFormSet, ContactoClienteFormSet
from .models import Cliente, DireccionCliente, ContactoCliente
from django.contrib import messages


'''
-------------------------------------------------
Funciones CRUD de clientes
-------------------------------------------------
'''

def ingresar_cliente(request):
    if request.method == "POST":
        #Llama a todos los formularios y formsets para un ingreso único
        cliente_form = ClienteForm(request.POST)
        direccion_formset = DireccionClienteFormSet(request.POST, prefix="direcciones")
        contacto_formset = ContactoClienteFormSet(request.POST, prefix="contactos")

        #Valida y guarda los formularios
        if cliente_form.is_valid() and direccion_formset.is_valid() and contacto_formset.is_valid():
            cliente = cliente_form.save()

            #Se guarda direccion y contacto asociada al cliente
            direcciones = direccion_formset.save(commit=False)
            for direccion in direcciones:
                direccion.cliente = cliente
                direccion.save()

            contactos = contacto_formset.save(commit=False)
            for contacto in contactos:
                contacto.cliente = cliente
                contacto.save()

            #Entrega un mensaje hacia el listado para confirmar el ingreso
            messages.success(request, f"Cliente: {cliente.nombre_fantasia_cliente}, direcciones y contactos guardados correctamente.")
            return redirect("clientes:listar_clientes")
        else:
            messages.error(request, "Hay errores en los formularios. Revisa los datos ingresados.")
    else:
        cliente_form = ClienteForm()
        direccion_formset = DireccionClienteFormSet(prefix="direcciones", queryset=DireccionCliente.objects.none())
        contacto_formset = ContactoClienteFormSet(prefix="contactos", queryset=ContactoCliente.objects.none())

    context = {
        "cliente_form": cliente_form,
        "direccion_formset": direccion_formset,
        "contacto_formset": contacto_formset,
    }

    return render(request, "clientes/ingresar_cliente.html", context)


def listar_clientes(request):
    clientes = Cliente.objects.filter(activo=True)
    return render(request, "clientes/listar_clientes.html", {"clientes": clientes})

def editar_cliente(request, cliente_id):
    """Vista para editar un cliente junto con sus direcciones y contactos."""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    direccion_prefix = "direcciones"
    contacto_prefix = "contactos"

    if request.method == "POST":
        cliente_form = ClienteForm(request.POST, instance=cliente)
        direccion_formset = DireccionClienteFormSet(
            request.POST, instance=cliente, prefix=direccion_prefix
        )
        contacto_formset = ContactoClienteFormSet(
            request.POST, instance=cliente, prefix=contacto_prefix
        )

        if cliente_form.is_valid() and direccion_formset.is_valid() and contacto_formset.is_valid():
            cliente_form.save()

            # Guardar direcciones
            direcciones = direccion_formset.save(commit=False)
            for direccion in direcciones:
                direccion.cliente = cliente
                direccion.save()
            # Eliminar direcciones marcadas para borrar
            for direccion in direccion_formset.deleted_objects:
                direccion.delete()

            # Guardar contactos
            contactos = contacto_formset.save(commit=False)
            for contacto in contactos:
                contacto.cliente = cliente
                contacto.save()
            # Eliminar contactos marcados para borrar
            for contacto in contacto_formset.deleted_objects:
                contacto.delete()

            messages.success(request, f"Cliente '{cliente.nombre_fantasia_cliente}' actualizado correctamente.")
            return redirect("clientes:listar_clientes")
        else:
            # Debug: imprimir errores
            print("ClienteForm errors:", cliente_form.errors)
            print("DireccionFormSet errors:", direccion_formset.errors)
            print("ContactoFormSet errors:", contacto_formset.errors)
            messages.error(request, "Hay errores en los formularios. Revisa los datos ingresados.")
    else:
        cliente_form = ClienteForm(instance=cliente)
        direccion_formset = DireccionClienteFormSet(instance=cliente, prefix=direccion_prefix)
        contacto_formset = ContactoClienteFormSet(instance=cliente, prefix=contacto_prefix)

    context = {
        "cliente": cliente,
        "cliente_form": cliente_form,
        "direccion_formset": direccion_formset,
        "contacto_formset": contacto_formset,
    }
    return render(request, "clientes/editar_cliente.html", context)

def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == "POST":
        cliente.activo = False
        cliente.save()
        messages.success(request, f"Cliente {cliente.nombre_fantasia_cliente} ha sido eliminado correctamente.")
        return redirect("clientes:listar_clientes")

    return redirect("clientes:listar_clientes")


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
        # Pasamos el cliente al form para la validación
        form.cliente_actual = cliente

        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = cliente
            direccion.save()
            messages.success(
                request,
                f"Dirección: {direccion.calle} {direccion.numero} agregada correctamente."
            )
            # Mantener en la misma vista para seguir ingresando direcciones
            return redirect('clientes:ingresar_direccion', cliente_id=cliente.id)
        else:
            messages.error(
                request,
                "Ocurrió un error al agregar la dirección. Revisa los datos e inténtalo nuevamente."
            )
    else:
        form = DireccionClienteForm()
        # Para que la validación futura sepa el cliente
        form.cliente_actual = cliente

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