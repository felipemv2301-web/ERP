from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from Despachos.models import GuiaDespacho, DetalleDespacho, DireccionCliente
from Productos.models import Producto
from django.core.exceptions import ValidationError
from django.db.models import Sum

class GuiaDespachoForm(forms.ModelForm):
    direccion_entrega = forms.ModelChoiceField(
        queryset=DireccionCliente.objects.none(),
        label="Dirección de entrega",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = GuiaDespacho
        fields = ['fecha_despacho', 'direccion_entrega', 'observacion_despacho']

    def __init__(self, *args, **kwargs):
        cliente = kwargs.pop('cliente', None)
        super().__init__(*args, **kwargs)
        if cliente:
            self.fields['direccion_entrega'].queryset = DireccionCliente.objects.filter(cliente=cliente)


class DetalleDespachoForm(forms.ModelForm):
    class Meta:
        model = DetalleDespacho
        fields = ['producto', 'cantidad_despachada', 'nombre_repartidor']

    def __init__(self, *args, **kwargs):
        pedido = kwargs.pop('pedido', None)
        super().__init__(*args, **kwargs)
        if pedido:
            self.fields['producto'].queryset = Producto.objects.filter(pedido=pedido)


# Validación de cantidades en el formset
class BaseDetalleDespachoFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            # Saltar forms vacíos o marcados para eliminar
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue

            producto = form.cleaned_data.get('producto')
            cantidad_despachada = form.cleaned_data.get('cantidad_despachada')

            # Validar que producto y cantidad existan
            if not producto:
                raise ValidationError("Debe seleccionar un producto en todas las filas.")
            if cantidad_despachada is None:
                raise ValidationError(f"Debe ingresar la cantidad despachada para '{producto.nombre_producto}'.")

            # Cantidad total ya despachada de este producto
            despachado_total = DetalleDespacho.objects.filter(
                producto=producto,
                guia_despacho__pedido=self.instance.pedido
            ).aggregate(total_despachado=Sum('cantidad_despachada'))['total_despachado'] or 0

            cantidad_pedido = producto.cantidad_producto
            if cantidad_despachada + despachado_total > cantidad_pedido:
                raise ValidationError(
                    f"No se puede despachar {cantidad_despachada} de '{producto.nombre_producto}'. "
                    f"Ya se han despachado {despachado_total}, cantidad total del pedido: {cantidad_pedido}."
                )


DetalleDespachoFormSet = inlineformset_factory(
    GuiaDespacho,
    DetalleDespacho,
    form=DetalleDespachoForm,
    extra=1,
    can_delete=True
)