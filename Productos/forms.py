from django import forms
from Productos.models import Producto
from Pedidos.models import Pedido
from django.forms import inlineformset_factory

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'tipo_producto', 'tamano_producto',
                  'observacion_producto', 'cantidad_producto', 'precio_unitario_producto']

ProductoFormSet = inlineformset_factory(
    Pedido,
    Producto,
    form=ProductoForm,
    extra=1,   # cantidad mínima de formularios vacíos
    can_delete=True
)