from django import forms
from .models import Abono

class AbonoForm(forms.ModelForm):
    class Meta:
        model = Abono
        fields = ['total_abono', 'fecha_abono']
        widgets = {
            'fecha_abono': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'total_abono': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        