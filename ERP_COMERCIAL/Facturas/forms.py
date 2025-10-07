from django import forms
from .models import Factura

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['fecha_emision_factura', 'cod_factura', 'total_factura']
        widgets = {
            'fecha_emision_factura': forms.DateInput(
                attrs={
                    'type': 'date',   # activa el calendario
                    'class': 'form-control'
                }
            ),
            'cod_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'total_factura': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        