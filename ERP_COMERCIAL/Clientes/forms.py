from django import forms
from django.forms.models import inlineformset_factory
from .models import Cliente, DireccionCliente, ContactoCliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # excluimos cod_cliente porque se genera automáticamente
        exclude = ["cod_cliente"]

class DireccionClienteForm(forms.ModelForm):
    class Meta:
        model = DireccionCliente
        exclude = ["cliente"]

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get("cliente")
        calle = cleaned_data.get("calle")
        numero = cleaned_data.get("numero")
        ciudad = cleaned_data.get("ciudad")
        comuna = cleaned_data.get("comuna")

        if DireccionCliente.objects.filter(
            cliente=cliente,
            calle=calle,
            numero=numero,
            ciudad=ciudad,
            comuna=comuna
        ).exists():
            raise forms.ValidationError("Esta dirección ya ha sido ingresada para este cliente.")

        return cleaned_data

class ContactoClienteForm(forms.ModelForm):
    class Meta:
        model = ContactoCliente
        exclude = ["cliente"]

# Formsets para ingreso múltiple
DireccionClienteFormSet = inlineformset_factory(
    Cliente, DireccionCliente, form=DireccionClienteForm,
    extra=1, can_delete=True
)

ContactoClienteFormSet = inlineformset_factory(
    Cliente, ContactoCliente, form=ContactoClienteForm,
    extra=1, can_delete=True
)