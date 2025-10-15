from django import forms
from django.forms.models import inlineformset_factory
from .models import Cliente, DireccionCliente, ContactoCliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # excluimos cod_cliente porque se genera automáticamente
        exclude = ["cod_cliente, activo"]

class DireccionClienteForm(forms.ModelForm):
    cliente_actual = None  # atributo temporal para la validación

    class Meta:
        model = DireccionCliente
        fields = ['calle', 'numero', 'comuna', 'ciudad']

    def clean(self):
        cleaned_data = super().clean()
        calle = cleaned_data.get("calle")
        numero = cleaned_data.get("numero")
        comuna = cleaned_data.get("comuna")
        ciudad = cleaned_data.get("ciudad")

        # Determinar qué cliente usar: el de la instancia o el temporal
        cliente = self.cliente_actual or getattr(self.instance, 'cliente', None)

        if cliente and calle and numero and comuna and ciudad:
            qs = DireccionCliente.objects.filter(
                cliente=cliente,
                calle=calle,
                numero=numero,
                comuna=comuna,
                ciudad=ciudad,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Esta dirección ya ha sido ingresada para este cliente.")
        return cleaned_data

class ContactoClienteForm(forms.ModelForm):
    class Meta:
        model = ContactoCliente
        exclude = ["cliente"]

DireccionClienteFormSet = inlineformset_factory(
    Cliente, DireccionCliente,
    form=DireccionClienteForm,
    extra=1, can_delete=True
)

ContactoClienteFormSet = inlineformset_factory(
    Cliente, ContactoCliente,
    form=ContactoClienteForm,
    extra=1, can_delete=True
)