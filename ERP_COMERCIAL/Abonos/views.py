from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from Abonos.forms import AbonoForm
from Facturas.models import Factura
from django.contrib import messages

def ingresar_abono(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)
    AbonoFormSet = formset_factory(AbonoForm, extra=3)  # 3 formularios por defecto

    if request.method == "POST":
        formset = AbonoFormSet(request.POST)  # importante: pasar el request.POST
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:  # evitar vacíos
                    abono = form.save(commit=False)
                    abono.factura = factura
                    abono.save()
            messages.success(request, "Abonos registrados correctamente.")
            return redirect('listar_pedidos')  # 👈 usa el name de la URL
    else:
        formset = AbonoFormSet()

    return render(request, 'Facturas/ingresar_abono.html', {
        'factura': factura,
        'formset': formset,
    })