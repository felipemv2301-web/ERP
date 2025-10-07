from django import forms
from Pedidos.models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cod_orden_compra', 'cliente', 'fecha_pedido']
        widgets = {
            'fecha_pedido': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(label="Selecciona PDF o imagen")