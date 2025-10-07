from django import forms
from django.forms import inlineformset_factory
from Despachos.models import GuiaDespacho, DetalleDespacho
from Productos.models import Producto

class GuiaDespachoForm(forms.ModelForm):
    class Meta:
        model = GuiaDespacho
        fields = ['fecha_despacho', 'direccion_entrega', 'observacion_despacho']
        widgets = {
            'fecha_despacho': forms.DateInput(attrs={'type': 'date'}),
            'observacion_despacho': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            # Construye la dirección completa combinando los campos
            opciones = [
                (f"{d.calle} {d.numero}, {d.comuna}, {d.ciudad}", f"{d.calle} {d.numero}, {d.comuna}, {d.ciudad}")
                for d in cliente.direccioncliente_set.all()
            ]
            self.fields['direccion_entrega'].choices = opciones


class DetalleDespachoForm(forms.ModelForm):
    class Meta:
        model = DetalleDespacho
        fields = ['producto', 'cantidad_despachada', 'nombre_repartidor']

    def __init__(self, *args, **kwargs):
        pedido = kwargs.pop('pedido', None)
        super().__init__(*args, **kwargs)
        if pedido:
            # Filtra solo productos del pedido seleccionado
            self.fields['producto'].queryset = Producto.objects.filter(pedido=pedido)

DetalleDespachoFormSet = inlineformset_factory(
    GuiaDespacho,
    DetalleDespacho,
    form=DetalleDespachoForm,
    extra=1,
    can_delete=True
)